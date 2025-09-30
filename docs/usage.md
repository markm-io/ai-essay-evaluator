(usage)=

# Usage

Assuming that you've followed the {ref}`installations steps <installation>`, you're now ready to use this package.

The AI Essay Evaluator provides two main command-line interfaces:

- **Evaluator**: Grade student essays using OpenAI models
- **Trainer**: Generate, validate, and fine-tune custom grading models

## Command Structure

```bash
uv run python -m ai_essay_evaluator <command> <subcommand> [OPTIONS]
```

Available commands:

- `evaluator` - CLI for grading student responses
- `trainer` - Generate, validate, merge, upload, and fine-tune JSONL files

---

## Evaluator: Grading Student Essays

### Quick Start with Project Folder

The simplest way to use the evaluator is with a project folder structure:

```
project_folder/
├── input.csv              # Student responses
├── question.txt           # The essay question/prompt
├── story/                 # Folder containing story text files
│   ├── story1.txt
│   └── story2.txt
├── rubric/                # Folder containing rubric text files
│   ├── rubric1.txt
│   └── rubric2.txt
└── output/                # Results will be saved here (auto-created)
```

**Basic command:**

```bash
uv run python -m ai_essay_evaluator evaluator grader \
  --project-folder ./project_folder \
  --scoring-format extended \
  --api-key YOUR_OPENAI_API_KEY
```

### Input CSV Format

Your input CSV file must contain these required columns:

- `Local Student ID` - Unique student identifier
- `Enrolled Grade Level` - Student's grade level
- `Tested Language` - Language of the test (e.g., "English", "Spanish")
- `Student Constructed Response` - The student's essay text

Optional column:

- `Passes` - Number of times to process each essay (for consistency checking)

**Example CSV:**

```csv
Local Student ID,Enrolled Grade Level,Tested Language,Student Constructed Response,Passes
12345,5,English,"The story demonstrates courage...",3
12346,5,English,"In the passage, the author shows...",3
```

### Scoring Formats

The tool supports three scoring formats, each with different fine-tuned models:

#### 1. Extended Format (`extended`)

Provides detailed scoring across multiple dimensions:

- **Idea Development Score** (0-4)
- **Idea Development Feedback** (detailed comments)
- **Language Conventions Score** (0-4)
- **Language Conventions Feedback** (detailed comments)

Default model: `ft:gpt-4o-mini-2024-07-18:securehst::B6YDFKyO`

#### 2. Item-Specific Format (`item-specific`)

Provides a single score and feedback:

- **Score** (0-4)
- **Feedback** (targeted comments)

Default model: `ft:gpt-4o-mini-2024-07-18:securehst::B72LJHWZ`

#### 3. Short Format (`short`)

Provides concise scoring:

- **Score** (0-4)
- **Feedback** (brief comments)

Default model: `ft:gpt-4o-mini-2024-07-18:securehst::B79Kzt5H`

### Full Parameter Reference

#### Required Parameters

- `--scoring-format` - Scoring format: `extended`, `item-specific`, or `short` (required)
- `--api-key` - Your OpenAI API key (required)

#### Project Folder Mode (Simplified)

- `--project-folder` - Path to folder containing all required files
  - Automatically discovers CSV file, story/, rubric/, and question.txt
  - Creates output/ folder for results

#### Manual Mode (Advanced)

When not using `--project-folder`, you must specify:

- `--input-file` - Path to input CSV file
- `--export-folder` - Where to save results
- `--export-file-name` - Base name for output files
- `--story-folder` - Folder containing story text files
- `--rubric-folder` - Folder containing rubric text files
- `--question-file` - Path to question text file

#### Optional Parameters

- `--openai-project` - OpenAI project ID for organization
- `--ai-model` - Override the default fine-tuned model
- `--log / --no-log` - Enable/disable logging (default: enabled)
- `--cost-analysis / --no-cost-analysis` - Track token usage and costs (default: enabled)
- `--passes` - Number of times to process each essay (overrides CSV column)
- `--merge-results / --no-merge-results` - Merge multiple pass results (default: enabled)
- `--show-progress / --no-show-progress` - Display progress bar (default: enabled)
- `--calculate-totals / --no-calculate-totals` - Calculate total scores (default: enabled)

### Output Files

The evaluator generates several output files in the export folder:

1. **`{filename}_pass_1.csv`** - Results from the first pass
2. **`{filename}_pass_2.csv`** - Results from subsequent passes (if `--passes > 1`)
3. **`{filename}_merged.csv`** - Merged results (if `--merge-results` enabled)
4. **`{filename}_cost_analysis.csv`** - Token usage and cost breakdown (if `--cost-analysis` enabled)
5. **`{filename}.log`** - Detailed processing log (if `--log` enabled)

**Output CSV columns include:**

- All original input columns
- Score columns (based on scoring format)
- Feedback columns (based on scoring format)
- Processing metadata (if enabled)

### Usage Examples

#### Example 1: Basic Evaluation with Project Folder

```bash
uv run python -m ai_essay_evaluator evaluator grader \
  --project-folder ./my_essays \
  --scoring-format extended \
  --api-key sk-...
```

#### Example 2: Multiple Passes for Consistency

```bash
uv run python -m ai_essay_evaluator evaluator grader \
  --project-folder ./my_essays \
  --scoring-format item-specific \
  --api-key sk-... \
  --passes 3 \
  --merge-results
```

#### Example 3: Manual Mode with Custom Settings

```bash
uv run python -m ai_essay_evaluator evaluator grader \
  --input-file ./data/responses.csv \
  --export-folder ./results \
  --export-file-name final_grades \
  --scoring-format short \
  --story-folder ./data/stories \
  --rubric-folder ./data/rubrics \
  --question-file ./data/question.txt \
  --api-key sk-... \
  --no-progress
```

#### Example 4: Using Custom Fine-Tuned Model

```bash
uv run python -m ai_essay_evaluator evaluator grader \
  --project-folder ./my_essays \
  --scoring-format extended \
  --api-key sk-... \
  --ai-model ft:gpt-4o-mini-2024-07-18:org:YOUR_MODEL_ID \
  --openai-project proj_...
```

---

## Trainer: Fine-Tuning Custom Models

The trainer component helps you create and fine-tune custom grading models using your own data.

### Workflow Overview

1. **Generate** JSONL training data from your graded examples
2. **Validate** the JSONL file format
3. **Merge** multiple JSONL files (optional)
4. **Upload** to OpenAI
5. **Fine-tune** a custom model

### 1. Generate Training Data

Create a JSONL training dataset from your existing graded essays.

**Command:**

```bash
uv run python -m ai_essay_evaluator trainer generate \
  --story-folder ./training_data/story \
  --question ./training_data/question.txt \
  --rubric ./training_data/rubric.txt \
  --csv ./training_data/graded_essays.csv \
  --output training_dataset.jsonl \
  --scoring-format extended
```

**Parameters:**

- `--story-folder` - Folder containing story text files (required)
- `--question` - Path to question text file (required)
- `--rubric` - Path to rubric text file (required)
- `--csv` - Path to CSV with graded examples (required)
- `--output` - Output JSONL filename (default: `fine_tuning.jsonl`)
- `--scoring-format` - Output format: `extended`, `item-specific`, or `short` (required)

**Input CSV for training must include:**

- `Local Student ID`
- `Enrolled Grade Level`
- `Tested Language`
- `Student Constructed Response`
- Score columns (matching your chosen scoring format)
- Feedback columns (matching your chosen scoring format)

**For extended format:**

- `Idea_Development_Score`
- `Idea_Development_Feedback`
- `Language_Conventions_Score`
- `Language_Conventions_Feedback`

**For item-specific/short formats:**

- `Score`
- `Feedback`

### 2. Validate Training Data

Validate that your JSONL file is properly formatted for OpenAI fine-tuning.

**Command:**

```bash
uv run python -m ai_essay_evaluator trainer validate \
  --file training_dataset.jsonl \
  --scoring-format extended
```

**Parameters:**

- `--file` - Path to JSONL file to validate (required)
- `--scoring-format` - Scoring format used: `extended`, `item-specific`, or `short` (default: `extended`)

The validator checks:

- JSON structure validity
- Required fields presence
- Message format compliance
- Response structure matching scoring format

### 3. Merge Multiple Datasets

Combine multiple JSONL training files into a single dataset.

**Command:**

```bash
uv run python -m ai_essay_evaluator trainer merge \
  --folder ./training_datasets \
  --output merged_training.jsonl
```

**Parameters:**

- `--folder` - Folder containing JSONL files to merge (required)
- `--output` - Output merged JSONL filename (default: `merged_fine_tuning.jsonl`)

### 4. Upload to OpenAI

Upload your validated JSONL file to OpenAI for fine-tuning.

**Command:**

```bash
uv run python -m ai_essay_evaluator trainer upload \
  --file training_dataset.jsonl \
  --api-key YOUR_OPENAI_API_KEY
```

**Parameters:**

- `--file` - Path to JSONL file to upload (required)
- `--api-key` - OpenAI API key (optional, can use environment variable)

**Output:** Returns a file ID (e.g., `file-abc123...`) needed for fine-tuning.

### 5. Start Fine-Tuning Job

Create a fine-tuning job with your uploaded dataset.

**Option A: Upload and fine-tune in one step**

```bash
uv run python -m ai_essay_evaluator trainer fine-tune \
  --file training_dataset.jsonl \
  --scoring-format extended \
  --api-key YOUR_OPENAI_API_KEY
```

**Option B: Use existing file ID**

```bash
uv run python -m ai_essay_evaluator trainer fine-tune \
  --file-id file-abc123... \
  --api-key YOUR_OPENAI_API_KEY
```

**Parameters:**

- `--file` - Path to JSONL file (validates, uploads, then fine-tunes)
- `--file-id` - Existing OpenAI file ID (skips validation and upload)
- `--scoring-format` - Required if using `--file`
- `--api-key` - OpenAI API key (optional, can use environment variable)

**Output:** Returns a fine-tuning job ID (e.g., `ftjob-xyz789...`)

### Complete Training Workflow Example

```bash
# Step 1: Generate JSONL from graded essays
uv run python -m ai_essay_evaluator trainer generate \
  --story-folder ./data/stories \
  --question ./data/question.txt \
  --rubric ./data/rubric.txt \
  --csv ./data/graded_samples.csv \
  --output my_training_data.jsonl \
  --scoring-format extended

# Step 2: Validate the generated file
uv run python -m ai_essay_evaluator trainer validate \
  --file my_training_data.jsonl \
  --scoring-format extended

# Step 3: Upload and start fine-tuning
uv run python -m ai_essay_evaluator trainer fine-tune \
  --file my_training_data.jsonl \
  --scoring-format extended \
  --api-key sk-...

# Step 4: Monitor your fine-tuning job on OpenAI dashboard
# Once complete, use the model ID with the evaluator:
uv run python -m ai_essay_evaluator evaluator grader \
  --project-folder ./new_essays \
  --scoring-format extended \
  --api-key sk-... \
  --ai-model ft:gpt-4o-mini-2024-07-18:org:YOUR_NEW_MODEL_ID
```

---

## Features

### Cost Analysis

When enabled (default), the tool tracks:

- Token usage (prompt tokens, completion tokens, total)
- Estimated costs based on model pricing
- Per-essay cost breakdown
- Summary statistics

Output saved to `{filename}_cost_analysis.csv`

### Logging

Comprehensive async logging tracks:

- Processing progress
- API call success/failures
- Error messages and retry attempts
- Performance metrics

Output saved to `{filename}.log`

### Rate Limiting

Built-in adaptive rate limiting:

- Respects OpenAI API rate limits (5000 RPM, 4M TPM)
- Automatic backoff on rate limit errors
- Configurable retry logic with exponential backoff

### Progress Tracking

Real-time progress bar shows:

- Number of essays processed
- Current processing speed
- Estimated time remaining

---

## Troubleshooting

### Common Issues

**1. "Missing required columns" error**

- Ensure your CSV has: `Local Student ID`, `Enrolled Grade Level`, `Tested Language`, `Student Constructed Response`
- Check column names for exact spelling and capitalization

**2. "No CSV input file found in project folder"**

- Ensure you have at least one `.csv` file in your project folder
- Use `--input-file` to specify the file explicitly

**3. Rate limit errors**

- The tool handles these automatically with retries
- For large batches, processing may slow down temporarily
- Consider using `--passes 1` for faster initial runs

**4. OpenAI API authentication errors**

- Verify your API key is correct
- Check that your organization has access to the model
- Use `--openai-project` if you have multiple projects

**5. Fine-tuning validation errors**

- Ensure your graded CSV has all required score/feedback columns
- Check that scoring format matches your data structure
- Run `trainer validate` to get detailed error messages

### Getting Help

For additional support:

- Check the [API Reference](ai_essay_evaluator) for module documentation
- Review the [Contributing Guide](contributing) for development setup
- Open an issue on [GitHub](https://github.com/markm-io/ai-essay-evaluator/issues)
