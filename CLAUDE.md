# CLAUDE.md / CONVENTIONS.md

This file provides guidance to Claude Code (claude.ai/code), Aider, and other tools when working with code in this repository.

## Project Overview

This is a Python CLI tool for picking random LeetCode problems and tracking progress. The tool helps select problems from study plans (LeetCode 75, Top Interview 150) while avoiding spoilers like difficulty categories.

## Development Environment

- **Python Version**: Python 3.13
- **Virtual Environment**: Uses direnv with Python virtual environment located at `/Users/paul/src/leetcode-picker/.direnv/python-3.13`
- **Environment Manager**: direnv is configured via `.envrc` file with `layout python python3.13`

## Architecture & Core Features

The CLI tool is designed to:

1. **Problem Management**: Track problems from multiple study plans with metadata (URL, title, completion dates, submission counts, difficulty)
2. **Data Storage**: Simple CSV file storage for problem tracking
3. **LeetCode Integration**: Authenticate via GitHub OAuth to fetch user's submission history
4. **Problem Selection**: Random problem picker with filtering by difficulty, study plan, and completion status

### Key Data Fields
- Problem URL and title
- Last completion date (YYYY-MM-DD format)
- Number of completions and total submissions  
- Difficulty level with override capability
- Study plan URL association

## Commands to Implement

Based on PLAN.md, the CLI should support:
- `choose`: Pick random unsolved problem (with optional difficulty/study plan filters)
- `review`: Pick previously completed problem (with "solved N weeks ago" option)
- `override-difficulty`: Set custom difficulty level for problems
- `progress`: Show completion stats for each study plan
- `mark-complete`: Mark problem as completed with date

## Development Workflow

### Code Quality & Linting
**CRITICAL**: All Python code must pass linting before any commits. Run the linter script after every code edit:

```bash
./black-flake8-mypy [files]
```

This script runs:
1. **Black**: Code formatting (line length: 90 characters)
2. **Flake8**: Style and error checking (configured in `.flake8`)
3. **Mypy**: Type checking (must pass - script exits on failure)

**Configuration**:
- Line length: 90 characters (Black and Flake8)
- Flake8 ignores: E203, E501, E701
- Flake8 excludes: .git, __pycache__, .direnv, htmlcov

### Implementation Guidelines

When implementing:

1. Use the existing virtual environment: `/Users/paul/src/leetcode-picker/.direnv/python-3.13`
2. Follow the architecture outlined in PLAN.md
3. Store problem data in CSV format
4. Implement LeetCode API integration for fetching user progress
5. Focus on CLI interface with the commands listed above
6. **Always run `./black-flake8-mypy` and fix all issues before committing**

## Study Plan Sources

- Primary: LeetCode 75 (https://leetcode.com/studyplan/leetcode-75/)
- Primary: Top Interview 150 (https://leetcode.com/studyplan/top-interview-150/)  
- Optional: Grind75 (https://www.techinterviewhandbook.org/grind75/)

## Notes

- Problem difficulty should use overridden values when available, falling back to default difficulty
- The tool intentionally avoids showing categories/topics to prevent spoilers
- LeetCode authentication uses GitHub OAuth
- Submission history can be accessed via `/submissions` endpoint for each problem