import json
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.openai_client import (
    call_openai_parse,
    extract_structured_response,
    generate_prompt,
    get_default_response,
    parse_reset_time,
    process_with_openai,
    simplify_prompt,
)


@pytest.fixture
def mock_async_logger():
    logger = AsyncMock()
    logger.log = AsyncMock()
    return logger


@pytest.fixture
def mock_openai_client():
    client = AsyncMock()
    client.beta.chat.completions.parse = AsyncMock()
    return client


@pytest.fixture
def sample_response():
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps(
        {
            "idea_development_score": 3,
            "idea_development_feedback": "Great development of ideas with clear examples.",
            "language_conventions_score": 2,
            "language_conventions_feedback": "Good command of grammar with some minor errors.",
        }
    )
    response.usage = {"prompt_tokens": 500, "completion_tokens": 200}
    return response


@pytest.fixture
def sample_extended_response():
    return {
        "idea_development_score": 3,
        "idea_development_feedback": "Good development of ideas with supporting details.",
        "language_conventions_score": 2,
        "language_conventions_feedback": "Proper grammar with few errors.",
    }


@pytest.fixture
def sample_standard_response():
    return {"score": 3, "feedback": "Well-developed response with good structure and few errors."}


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Local Student ID": [123456, 789012],
            "Student Constructed Response": ["This is a test response", ""],
            "Tested Language": ["English", "Spanish"],
            "Enrolled Grade Level": [3, 4],
        }
    )


def test_parse_reset_time():
    assert parse_reset_time("1s") == 1
    assert parse_reset_time("30s") == 30
    assert parse_reset_time("1m") == 60
    assert parse_reset_time("2m30s") == 150


@pytest.mark.asyncio
async def test_extract_structured_response_extended(sample_response, mock_async_logger):
    # Test successful extraction
    result = await extract_structured_response(sample_response, "extended", mock_async_logger)
    assert result["idea_development_score"] == 3
    assert "Great development" in result["idea_development_feedback"]

    # Test handling invalid response
    invalid_response = MagicMock()
    invalid_response.choices = [MagicMock()]
    invalid_response.choices[0].message.content = "Not valid JSON"

    with pytest.raises(Exception):  # noqa: B017
        await extract_structured_response(invalid_response, "extended", mock_async_logger)
    assert mock_async_logger.log.called


@pytest.mark.asyncio
async def test_extract_structured_response_empty_feedback(mock_async_logger):
    # Test handling response with empty feedback
    empty_feedback_response = MagicMock()
    empty_feedback_response.choices = [MagicMock()]
    empty_feedback_response.choices[0].message.content = json.dumps(
        {
            "idea_development_score": 2,
            "idea_development_feedback": "Good points",
            "language_conventions_score": 1,
            "language_conventions_feedback": "",  # Empty feedback
        }
    )

    with pytest.raises(ValueError, match="Language conventions feedback is empty"):
        await extract_structured_response(empty_feedback_response, "extended", mock_async_logger)


@pytest.mark.asyncio
async def test_call_openai_parse(mock_openai_client, sample_response, mock_async_logger):
    mock_openai_client.beta.chat.completions.parse.return_value = sample_response

    messages = [{"role": "system", "content": "You are a grader"}, {"role": "user", "content": "Grade this response"}]

    with patch("ai_essay_evaluator.evaluator.openai_client.adaptive_rate_limit", AsyncMock()):
        result, usage = await call_openai_parse(
            messages, "gpt-4o", mock_openai_client, "extended", mock_async_logger, "123456"
        )

    assert result["idea_development_score"] == 3
    assert usage == sample_response.usage
    mock_openai_client.beta.chat.completions.parse.assert_called_once()


def test_generate_prompt():
    row = {"Student Constructed Response": "My test answer", "Tested Language": "English", "Enrolled Grade Level": 5}

    story_dict = {"title": "Test Story", "text": "Once upon a time..."}
    rubric_text = "Scoring rubric: 4 points for excellent response..."
    question_text = "What happened in the story?"

    messages = generate_prompt(row, "extended", story_dict, rubric_text, question_text)

    assert messages[0]["role"] == "system"
    assert "AI Grader" in messages[0]["content"]

    user_content = json.loads(messages[1]["content"])
    assert user_content["grade_level"] == "Grade 5"
    assert user_content["student_response"] == "My test answer"
    assert user_content["stories"] == story_dict


def test_get_default_response():
    extended = get_default_response("extended")
    assert extended["idea_development_score"] == 0
    assert "Error processing" in extended["idea_development_feedback"]

    standard = get_default_response("standard")
    assert standard["score"] == 0
    assert "Error processing" in standard["feedback"]


def test_simplify_prompt():
    original_messages = [
        {"role": "system", "content": "You are a grader"},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "grade_level": "Grade 4",
                    "question": "Analyze the story",
                    "rubric": "Detailed rubric...",
                    "student_response": "My answer",
                    "extra_info": "Additional context",
                    "more_data": {"nested": "value"},
                }
            ),
        },
    ]

    simplified = simplify_prompt(original_messages)

    # System message should remain unchanged
    assert simplified[0] == original_messages[0]

    # User message should have simplified content
    simple_content = json.loads(simplified[1]["content"])
    assert "grade_level" in simple_content
    assert "student_response" in simple_content
    assert "extra_info" not in simple_content
    assert "more_data" not in simple_content


@pytest.mark.asyncio
async def test_process_with_openai_blank_response(sample_df, mock_openai_client, mock_async_logger):
    progress_callback = AsyncMock()

    # Create a sample df with a blank response
    blank_df = pd.DataFrame(
        {
            "Local Student ID": [123456],
            "Student Constructed Response": [""],  # Blank response
            "Tested Language": ["English"],
            "Enrolled Grade Level": [3],
        }
    )

    default_response = get_default_response("extended")
    default_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    # Mock the call_openai_parse function to return our controlled response
    async def mock_call(*args, **kwargs):
        return default_response, default_usage

    with patch("ai_essay_evaluator.evaluator.openai_client.call_openai_parse", mock_call):
        # Also patch any other functions to avoid external dependencies
        with patch("ai_essay_evaluator.evaluator.openai_client.generate_prompt"):
            _results_df, _usage = await process_with_openai(
                blank_df,
                "gpt-4o",
                "test-api-key",
                {},
                "test-rubric",
                "test-question",
                "extended",
                "test-project",
                progress_callback,
                mock_async_logger,
            )

    # Verify blank response detection was logged
    assert any(
        "Blank response detected" in call[0][1] for call in mock_async_logger.log.call_args_list if len(call[0]) > 1
    )
    assert progress_callback.call_count > 0


@pytest.mark.asyncio
async def test_process_with_openai_error_handling(sample_df, mock_openai_client, mock_async_logger):
    # Mock call_openai_parse to raise a simple exception
    async def mock_call(*args, **kwargs):
        raise ValueError("Test error")

    with patch("ai_essay_evaluator.evaluator.openai_client.call_openai_parse", mock_call):
        with patch("ai_essay_evaluator.evaluator.openai_client.get_default_response") as mock_default:
            # Make sure default response is returned
            mock_default.return_value = {
                "idea_development_score": 0,
                "idea_development_feedback": "Error processing",
                "language_conventions_score": 0,
                "language_conventions_feedback": "Error processing",
            }

            results_df, _usage = await process_with_openai(
                sample_df,
                "gpt-4o",
                "test-api-key",
                {},
                "test-rubric",
                "test-question",
                "extended",
                "test-project",
                None,
                mock_async_logger,
            )

    # Check error was logged and default responses were used
    assert any(
        "Failed to process student" in call[0][1] for call in mock_async_logger.log.call_args_list if len(call[0]) > 1
    )

    # Check the results contain the expected columns
    assert all(
        column in results_df.columns
        for column in [
            "idea_development_score",
            "idea_development_feedback",
            "language_conventions_score",
            "language_conventions_feedback",
        ]
    )


@pytest.mark.asyncio
async def test_adaptive_rate_limit():
    """Test adaptive rate limiting function."""
    import time

    from ai_essay_evaluator.evaluator.openai_client import adaptive_rate_limit, rate_tracker

    # Reset rate tracker
    rate_tracker.request_window_start = time.time()
    rate_tracker.requests_in_window = 0

    # Should not block for first few requests
    await adaptive_rate_limit()
    assert rate_tracker.requests_in_window == 1


@pytest.mark.asyncio
async def test_extract_structured_response_standard_format(mock_async_logger):
    """Test extracting standard format response."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps({"score": 3, "feedback": "Good work"})

    result = await extract_structured_response(response, "standard", mock_async_logger)
    assert result["score"] == 3
    assert result["feedback"] == "Good work"


def test_generate_prompt_spanish():
    """Test prompt generation for Spanish language."""
    row = {"Student Constructed Response": "Mi respuesta", "Tested Language": "Spanish", "Enrolled Grade Level": 4}

    story_dict = {"title": "Historia"}
    rubric_text = "Rúbrica"
    question_text = "¿Qué pasó?"

    messages = generate_prompt(row, "short", story_dict, rubric_text, question_text)

    user_content = json.loads(messages[1]["content"])
    assert "español" in user_content["evaluation_guidance"].lower()


def test_get_default_response_all_formats():
    """Test default responses for all formats."""
    # Extended format
    extended = get_default_response("extended")
    assert "idea_development_score" in extended
    assert "language_conventions_score" in extended

    # Standard format
    standard = get_default_response("standard")
    assert "score" in standard
    assert "feedback" in standard

    # Item-specific format (should behave like standard)
    item_specific = get_default_response("item-specific")
    assert "score" in item_specific

    # Short format (should behave like standard)
    short = get_default_response("short")
    assert "score" in short
