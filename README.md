# AI Essay Evaluator

<p align="center">
  <a href="https://github.com/markm-io/ai-essay-evaluator/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/markm-io/ai-essay-evaluator/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://ai-essay-evaluator.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/ai-essay-evaluator.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/markm-io/ai-essay-evaluator">
    <img src="https://img.shields.io/codecov/c/github/markm-io/ai-essay-evaluator.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/ai-essay-evaluator/">
    <img src="https://img.shields.io/pypi/v/ai-essay-evaluator.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/ai-essay-evaluator.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/ai-essay-evaluator.svg?style=flat-square" alt="License">
</p>

---

**Documentation**: <a href="https://ai-essay-evaluator.readthedocs.io" target="_blank">https://ai-essay-evaluator.readthedocs.io </a>

**Source Code**: <a href="https://github.com/markm-io/ai-essay-evaluator" target="_blank">https://github.com/markm-io/ai-essay-evaluator </a>

---

A comprehensive Python framework for automated essay evaluation using OpenAI's GPT models. This tool enables educators to grade student essays at scale with customizable scoring rubrics, fine-tune models with their own grading data, and generate detailed feedback across multiple scoring dimensions.

## Features

- **Automated Essay Grading** - Evaluate student essays using fine-tuned OpenAI GPT-4o-mini models
- **Multiple Scoring Formats** - Choose from extended (multi-dimensional), item-specific, or short scoring formats
- **Custom Model Training** - Generate training datasets and fine-tune models with your own grading examples
- **Project Folder Mode** - Simple folder structure for organizing essays, rubrics, and prompts
- **Cost Tracking** - Built-in token usage and cost analysis for OpenAI API calls
- **Batch Processing** - Grade hundreds of essays with progress tracking and async processing
- **Multi-Pass Grading** - Run multiple grading passes for consistency checking
- **Rate Limit Handling** - Automatic retry logic and adaptive rate limiting
- **Comprehensive Logging** - Async logging for debugging and auditing

## Quick Start

### Installation

Install via pip:

```bash
pip install ai-essay-evaluator
```

Or using uv (recommended for development):

```bash
uv pip install ai-essay-evaluator
```

### Basic Usage

1. **Set up your project folder:**

```
my_project/
├── input.csv              # Student responses
├── question.txt           # Essay prompt
├── story/                 # Story files
│   └── story1.txt
└── rubric/                # Rubric files
    └── rubric1.txt
```

2. **Run the evaluator:**

```bash
python -m ai_essay_evaluator evaluator grader \
  --project-folder ./my_project \
  --scoring-format extended \
  --api-key YOUR_OPENAI_API_KEY
```

3. **Check results in** `my_project/output/`

### Training Your Own Model

```bash
# Generate training data from graded examples
python -m ai_essay_evaluator trainer generate \
  --story-folder ./training/story \
  --question ./training/question.txt \
  --rubric ./training/rubric.txt \
  --csv ./training/graded_samples.csv \
  --output training.jsonl \
  --scoring-format extended

# Validate and fine-tune
python -m ai_essay_evaluator trainer validate --file training.jsonl
python -m ai_essay_evaluator trainer fine-tune \
  --file training.jsonl \
  --scoring-format extended \
  --api-key YOUR_OPENAI_API_KEY
```

For detailed documentation, visit the [full usage guide](https://ai-essay-evaluator.readthedocs.io/en/latest/usage.html).

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/markm-io"><img src="https://avatars.githubusercontent.com/u/45011486?v=4?s=80" width="80px;" alt="Mark Moreno"/><br /><sub><b>Mark Moreno</b></sub></a><br /><a href="https://github.com/markm-io/ai-essay-evaluator/commits?author=markm-io" title="Code">💻</a> <a href="#ideas-markm-io" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/markm-io/ai-essay-evaluator/commits?author=markm-io" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
