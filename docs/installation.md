(installation)=

# Installation

## Prerequisites

Before installing AI Essay Evaluator, ensure you have:

- **Python 3.10 or higher** - Check your version with `python --version`
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
- **pip** or **uv** package manager (recommended)

## Install via pip

The package is published on [PyPI](https://pypi.org/project/ai-essay-evaluator/) and can be installed with `pip`:

```bash
pip install ai-essay-evaluator
```

## Install via uv (Recommended for Development)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver, especially useful for development:

```bash
# Install uv if you haven't already
pip install uv

# Install ai-essay-evaluator
uv pip install ai-essay-evaluator
```

## Verify Installation

Verify the installation by checking the available commands:

```bash
python -m ai_essay_evaluator --help
```

Or with uv:

```bash
uv run python -m ai_essay_evaluator --help
```

You should see output showing the `evaluator` and `trainer` commands.

## Setup

### 1. Prepare Your OpenAI API Key

You'll need to provide your OpenAI API key when running commands. You can either:

**Option A: Pass it as a command-line argument**

```bash
python -m ai_essay_evaluator evaluator grader \
  --api-key sk-your-api-key-here \
  --project-folder ./my_project \
  --scoring-format extended
```

**Option B: Set as an environment variable**

```bash
# Linux/macOS
export OPENAI_API_KEY='sk-your-api-key-here'

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY='sk-your-api-key-here'
```

Then run without `--api-key`:

```bash
python -m ai_essay_evaluator evaluator grader \
  --project-folder ./my_project \
  --scoring-format extended
```

### 2. Prepare Your Project Structure

For the evaluator, create a project folder with the following structure:

```
my_project/
├── input.csv              # Your student responses
├── question.txt           # The essay prompt/question
├── story/                 # Folder with story files
│   └── story1.txt
└── rubric/                # Folder with rubric files
    └── rubric1.txt
```

### 3. Prepare Your Input CSV

Your CSV file must include these columns:

- `Local Student ID` - Student identifier
- `Enrolled Grade Level` - Grade level
- `Tested Language` - Language (e.g., "English")
- `Student Constructed Response` - The essay text

**Example CSV:**

```csv
Local Student ID,Enrolled Grade Level,Tested Language,Student Constructed Response
12345,5,English,"The story shows courage when..."
12346,5,English,"In the passage, the author demonstrates..."
```

## Development Installation

If you're contributing to the project or want to run from source:

```bash
# Clone the repository
git clone https://github.com/markm-io/ai-essay-evaluator.git
cd ai-essay-evaluator

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Troubleshooting Installation

### Issue: "Command not found: python"

Try using `python3` instead:

```bash
python3 -m ai_essay_evaluator --help
```

### Issue: "No module named 'ai_essay_evaluator'"

Ensure the package is installed:

```bash
pip list | grep ai-essay-evaluator
```

If not listed, reinstall:

```bash
pip install --upgrade ai-essay-evaluator
```

### Issue: "Permission denied" during installation

Use the `--user` flag:

```bash
pip install --user ai-essay-evaluator
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ai-essay-evaluator
```

## Next Steps

Next, see the {ref}`section about usage <usage>` to learn how to use the tool.
