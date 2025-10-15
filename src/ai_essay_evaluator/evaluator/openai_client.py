import asyncio
import json
import logging
import re
import time

import openai
import pandas as pd
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Get your application logger
logger = logging.getLogger(__name__)

# Enhanced retry settings with better backoff strategy
RETRY_SETTINGS = {
    "stop": stop_after_attempt(7),  # Increased from 5
    "wait": wait_exponential(multiplier=1.5, min=2, max=30),  # Increased max wait time
    "retry": retry_if_exception_type((openai.OpenAIError, ValidationError, asyncio.TimeoutError, json.JSONDecodeError)),
    "before_sleep": before_sleep_log(logger, logging.INFO),
}


# Global rate limiting tracking
class RateLimitTracker:
    def __init__(self):
        self.request_window_start = time.time()
        self.requests_in_window = 0
        self.tokens_in_window = 0
        self.max_requests_per_minute = 5000  # Updated to 5000 RPM
        self.max_tokens_per_minute = 4000000  # 4M TPM


rate_tracker = RateLimitTracker()


class ExtendedScoringResponse(BaseModel):
    idea_development_score: int
    idea_development_feedback: str
    language_conventions_score: int
    language_conventions_feedback: str


class StandardScoringResponse(BaseModel):
    score: int
    feedback: str


def parse_reset_time(reset_str: str) -> int:
    """
    Parses a reset time string (e.g. "1s" or "6m0s") and returns the number of seconds.
    """
    minutes = 0
    seconds = 0
    m_match = re.search(r"(\d+)m", reset_str)
    if m_match:
        minutes = int(m_match.group(1))
    s_match = re.search(r"(\d+)s", reset_str)
    if s_match:
        seconds = int(s_match.group(1))
    return minutes * 60 + seconds


async def adaptive_rate_limit(async_logger=None):
    """Implement adaptive rate limiting based on time window tracking"""
    current_time = time.time()

    # Reset window counter if a minute has passed
    if current_time - rate_tracker.request_window_start >= 60:
        rate_tracker.request_window_start = current_time
        rate_tracker.requests_in_window = 0

    # Preemptive rate limiting based on fixed limits
    rate_tracker.requests_in_window += 1

    # Using fixed limits: 5000 requests per minute, leaving some buffer
    if rate_tracker.requests_in_window > 4800:  # 200 request buffer
        wait_time = 60 - (current_time - rate_tracker.request_window_start) + 1
        if wait_time > 0:
            if async_logger:
                await async_logger.log(
                    logging.INFO, f"Approaching rate limit. Pausing for {wait_time:.2f} seconds", module=__name__
                )
            await asyncio.sleep(wait_time)
            rate_tracker.request_window_start = time.time()
            rate_tracker.requests_in_window = 0


@retry(**RETRY_SETTINGS)
async def call_openai_parse(
    messages: list[dict[str, str]],
    model: str,
    client: AsyncOpenAI,
    scoring_format: str,
    async_logger=None,
    student_id: str = "Unknown",
):
    response_format = ExtendedScoringResponse if scoring_format == "extended" else StandardScoringResponse
    max_completion_tokens = 2000

    # Apply adaptive rate limiting before making request
    await adaptive_rate_limit(async_logger)

    try:
        response = await client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=0,
            response_format=response_format,
            max_tokens=max_completion_tokens,
        )

        structured = await extract_structured_response(response, scoring_format, async_logger, student_id)
        usage = response.usage
        return structured, usage

    except Exception as e:
        if async_logger:
            await async_logger.log(logging.ERROR, f"OpenAI API error for student {student_id}: {e!s}", module=__name__)
        raise


async def process_with_openai(
    df,
    ai_model,
    api_key,
    stories,
    rubrics,
    question,
    scoring_format,
    openai_project,
    progress_callback=None,
    async_logger=None,
):
    client = AsyncOpenAI(
        api_key=api_key,
        project=openai_project,
        timeout=60,  # Increased timeout
        max_retries=5,  # Increased retries
    )

    # Reduce concurrency to prevent overwhelming the API
    semaphore = asyncio.Semaphore(25)  # Reduced from 100

    async def process_row(index, row):
        student_id = str(int(row.get("Local Student ID")))
        student_response = row["Student Constructed Response"]
        student_language = row["Tested Language"]

        # Check if response is blank
        if not student_response or student_response.strip() == "":
            if async_logger:
                await async_logger.log(
                    logging.INFO,
                    f"Blank response detected for student {student_id}. Skipping API call.",
                    module=__name__,
                )
            if progress_callback:
                await progress_callback()
            # Return default response for blank submissions
            if student_language == "Spanish":
                return index, (
                    {
                        "idea_development_score": 0,
                        "idea_development_feedback": "No se proporcionó respuesta del estudiante",
                        "language_conventions_score": 0,
                        "language_conventions_feedback": "Tenga en cuenta que si una respuesta recibe un puntaje "
                        "de 0 en el rasgo de Desarrollo de ideas, la respuesta también "
                        "obtendrá 0 puntos en el rasgo de Convenciones.",
                    },
                    {},
                )
            else:
                return index, (
                    {
                        "idea_development_score": 0,
                        "idea_development_feedback": "No Student Response Provided",
                        "language_conventions_score": 0,
                        "language_conventions_feedback": "Please note that if a response receives a score point 0 "
                        "in the Idea Development trait, the response will also earn 0 points in "
                        "the Conventions trait.",
                    },
                    {},
                )

        async with semaphore:
            prompt = generate_prompt(row, scoring_format, stories, rubrics, question)
            try:
                result = await call_openai_parse(prompt, ai_model, client, scoring_format, async_logger, student_id)
                if progress_callback:
                    await progress_callback()
                return index, result
            except Exception as e:
                if async_logger:
                    await async_logger.log(
                        logging.ERROR,
                        f"Failed to process student {student_id} after all retries: {e!s}",
                        module=__name__,
                        exc_info=True,
                    )
                # Instead of returning default response immediately, try one more time with a backup approach
                try:
                    # Brief pause before retry
                    await asyncio.sleep(2)
                    # Simplify the prompt if possible
                    simplified_prompt = simplify_prompt(prompt)
                    result = await call_openai_parse(
                        simplified_prompt, ai_model, client, scoring_format, async_logger, student_id
                    )
                    if progress_callback:
                        await progress_callback()
                    return index, result
                except Exception as e2:
                    if async_logger:
                        await async_logger.log(
                            logging.ERROR,
                            f"Backup approach failed for student {student_id}: {e2!s}",
                            module=__name__,
                        )
                    if progress_callback:
                        await progress_callback()
                    return index, (get_default_response(scoring_format), {})

    # Use smaller batches for better throughput management
    batch_size = 100  # Reduced from 500
    results = []
    for start in range(0, len(df), batch_size):
        batch = df.iloc[start : start + batch_size]
        tasks = [process_row(idx, row) for idx, row in batch.iterrows()]
        batch_results = []
        for coro in asyncio.as_completed(tasks):
            try:
                idx, res = await coro
                batch_results.append((idx, res))
            except Exception as e:
                if async_logger:
                    await async_logger.log(
                        logging.ERROR,
                        f"Unexpected error in batch processing: {e!s}",
                        module=__name__,
                        exc_info=True,
                    )

        results.extend(batch_results)

        # Add a brief pause between batches to prevent rate limiting
        await asyncio.sleep(1)

    # Build a dictionary mapping each original index to its structured result and gather usage details
    structured_results_dict = {}
    usage_list = []
    for idx, (structured, usage) in results:
        structured_results_dict[idx] = structured
        if usage:
            usage_list.append(usage)

    # Create a DataFrame from the structured results and reindex it to match the original DataFrame order
    structured_df = pd.DataFrame.from_dict(structured_results_dict, orient="index")
    structured_df = structured_df.reindex(df.index)

    # Verify no missing or invalid data
    if structured_df.isnull().any().any():
        if async_logger:
            await async_logger.log(
                logging.WARNING,
                f"Found {structured_df.isnull().sum().sum()} missing values in results",
                module=__name__,
            )
        # Fill missing values with default responses
        for idx in structured_df.index[structured_df.isnull().any(axis=1)]:
            structured_df.loc[idx] = get_default_response(scoring_format)

    return pd.concat([df, structured_df], axis=1), usage_list


def simplify_prompt(messages):
    """Create a simpler version of the prompt to increase chances of successful processing"""
    system_msg = messages[0]
    user_msg = messages[1]

    # Parse the user content if it's JSON
    try:
        if isinstance(user_msg["content"], str):
            content = json.loads(user_msg["content"])
        else:
            content = user_msg["content"]

        # Create a simplified content with just essential elements
        simplified_content = {
            "grade_level": content.get("grade_level", ""),
            "question": content.get("question", ""),
            "rubric": content.get("rubric", ""),
            "student_response": content.get("student_response", ""),
        }

        # Create simplified messages
        return [system_msg, {"role": "user", "content": json.dumps(simplified_content, ensure_ascii=False)}]
    except Exception:
        # If parsing fails, return original messages
        return messages


async def extract_structured_response(response, scoring_format, async_logger=None, student_id="Unknown"):
    response_text = response.choices[0].message.content.strip()

    try:
        # Check if response is already a dict (might happen with some API versions)
        if isinstance(response_text, dict):
            structured_output = response_text
        else:
            # Try to parse JSON - handle both proper JSON and cases where there's extra content
            try:
                structured_output = json.loads(response_text)
            except json.JSONDecodeError as err:
                # Try to extract just the JSON part using regex
                json_match = re.search(r"(\{.*\})", response_text, re.DOTALL)
                if json_match:
                    try:
                        structured_output = json.loads(json_match.group(1))
                    except Exception as e2:
                        raise ValueError("Could not extract valid JSON") from e2
                else:
                    raise ValueError("Response does not contain valid JSON") from err

        # Check for empty or minimal feedback
        if scoring_format == "extended":
            idea_feedback = structured_output.get("idea_development_feedback", "").strip()
            lang_feedback = structured_output.get("language_conventions_feedback", "").strip()

            if not idea_feedback or idea_feedback == "." or len(idea_feedback) < 5:
                raise ValueError("Idea development feedback is empty or insufficient")

            if not lang_feedback or lang_feedback == "." or len(lang_feedback) < 5:
                raise ValueError("Language conventions feedback is empty or insufficient")
        else:
            feedback = structured_output.get("feedback", "").strip()
            if not feedback or feedback == "." or len(feedback) < 5:
                raise ValueError("Feedback is empty or insufficient")

        # Validate with appropriate model
        if scoring_format == "extended":
            # Ensure language_conventions_score is 0 if idea_development_score is 0
            if structured_output.get("idea_development_score") == 0:
                structured_output["language_conventions_score"] = 0
                if not structured_output.get("language_conventions_feedback").startswith("Error"):
                    structured_output["language_conventions_feedback"] = (
                        "Please note that if a response receives a score point 0 in the Idea Development trait, "
                        "the response will also earn 0 points in the Conventions trait."
                    )

            return ExtendedScoringResponse(**structured_output).model_dump()
        else:
            return StandardScoringResponse(**structured_output).model_dump()
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        if async_logger:
            await async_logger.log(
                logging.ERROR,
                f"Response validation failed for student {student_id}: {e}, Response: {response_text[:100]}...",
                module=__name__,
            )
        raise


def generate_prompt(row, scoring_format, story_dict, rubric_text, question_text):
    # Original function implementation unchanged
    student_response = row["Student Constructed Response"]
    if scoring_format == "extended":
        extended_system_content = (
            "four keys: 'idea_development_score' (an integer), 'idea_development_feedback' (a string), "
            "'language_conventions_score' (an integer), and 'language_conventions_feedback' (a string)"
        )
    else:
        extended_system_content = "two keys: 'score' (an integer) and 'feedback' (a string)"

    # Normalize language format
    tested_language = row["Tested Language"].strip().lower()
    grade_level = row["Enrolled Grade Level"]

    # Language instructions
    if tested_language == "spanish":
        language_instruction = (
            "El estudiante ha realizado la prueba en español. "
            "Proporcione la retroalimentación y la evaluación en español."
        )
    else:
        language_instruction = "The student has taken the test in English. Provide feedback and evaluation in English."

    # Structured prompt to reduce token usage
    user_prompt = {
        "grade_level": f"Grade {grade_level}",
        "language": tested_language.capitalize(),
        "stories": story_dict,
        "question": question_text,
        "rubric": rubric_text,
        "evaluation_guidance": (
            f"Analyze the student's response in a grade-appropriate manner. "
            f"Ensure feedback aligns with expectations for Grade {grade_level}. "
            f"{language_instruction}"
        ),
        "student_response": student_response,
    }

    user_message = {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}

    messages = [
        {
            "role": "system",
            "content": (
                f"AI Grader: Evaluate student responses based on rubric. "
                f"Your task is to assess the student's answer using the provided story, question, and rubric. "
                f"\n\n"
                f"IMPORTANT - Distinguishing Evidence-Based Writing from Plagiarism:\n"
                f"- Students are REQUIRED to use evidence from the source texts to support their answers.\n"
                f"- Using quotes with attribution (e.g., 'The text says...', 'According to...') is EXPECTED "
                f"and CORRECT.\n"
                f"- Referencing character names, settings, plot points, and citing specific paragraphs/lines "
                f"is APPROPRIATE.\n"
                f"- Using vocabulary from the source material when analyzing those texts is NORMAL.\n"
                f"\n"
                f"Assign a score of 0 for plagiarism ONLY when ALL of these conditions are met:\n"
                f"1. At least 70% of the response consists of verbatim copied text from the source materials\n"
                f"2. The response does NOT clearly attempt to answer the specific question asked\n"
                f"3. There is little to no original analysis, explanation, or synthesis after any cited evidence\n"
                f"4. The response lacks proper attribution or quotation markers for extensive copying\n"
                f"\n"
                f"ACCEPTABLE evidence-based writing (grade 1-3 based on rubric, NOT 0) has these features:\n"
                f"- States a clear central idea or thesis that answers the question\n"
                f"- Includes evidence from the text with proper attribution ('The text says...', 'According to...', "
                f"'In paragraph X...')\n"
                f"- Provides original analysis or explanation connecting evidence to the central idea "
                f"('This shows...', 'This proves...', 'This demonstrates...')\n"
                f"- Uses student's own connecting language between ideas, even if citing source material\n"
                f"- References characters, events, or concepts from the text as part of answering the question\n"
                f"\n"
                f"UNACCEPTABLE plagiarism (score 0) has these features:\n"
                f"- Response repeats the question verbatim with no original answer\n"
                f"- Response consists primarily of plot summary or copied sentences with no analysis\n"
                f"- Response copies multiple consecutive sentences verbatim without quotation marks or attribution\n"
                f"- Response lacks original connecting language or synthesis between copied fragments\n"
                f"- Response fails to demonstrate any attempt to answer the specific question asked\n"
                f"\n"
                f"Evaluation Process:\n"
                f"1. First, check if the response attempts to answer the specific question asked\n"
                f"2. Identify what percentage of the response is the student's own words vs. copied text\n"
                f"3. Look for evidence of analysis, synthesis, or explanation (e.g., 'This shows...', "
                f"'This proves...', 'They are similar because...')\n"
                f"4. If the response shows an attempt to answer with evidence and some analysis, grade it based on "
                f"the rubric criteria (NOT 0)\n"
                f"5. Only assign 0 if it's predominantly copied text with no meaningful attempt to answer or analyze\n"
                f"\n"
                f"Return your evaluation strictly as a JSON object with exactly {extended_system_content}. "
                f"Do not include any additional text or commentary. Ensure that the JSON output is valid and parsable."
            ),
        },
        user_message,
    ]
    return messages


def get_default_response(scoring_format):
    if scoring_format == "extended":
        return {
            "idea_development_score": 0,
            "idea_development_feedback": "Error processing response. Please review manually.",
            "language_conventions_score": 0,
            "language_conventions_feedback": "Error processing response. Please review manually.",
        }
    else:
        return {"score": 0, "feedback": "Error processing response. Please review manually."}
