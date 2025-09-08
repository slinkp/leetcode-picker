# LeetCode Picker

A CLI tool for picking random LeetCode problems and tracking your progress without spoilers.

## Features

- **Random Problem Selection**: Pick unsolved problems from LeetCode 75 and Top Interview 150 study plans
- **Progress Tracking**: Track completion dates, attempt counts, and overall progress
- **Difficulty Override**: Set custom difficulty levels for problems where you disagree with LeetCode's rating
- **Review Mode**: Revisit previously solved problems, with optional filtering by time elapsed
- **CSV Storage**: Simple file-based storage in `~/.leetcode-picker/problems.csv`

## Installation

```bash
pip install -e .
```

This installs the `leetcode-picker` command globally.

## Quick Start

```bash
# Get a random unsolved problem
leetcode-picker choose

# Get an easy problem from LeetCode 75
leetcode-picker choose --difficulty easy --study-plan leetcode-75

# Mark a problem as completed
leetcode-picker mark-complete https://leetcode.com/problems/two-sum/

# Check your progress
leetcode-picker progress

# Review a previously solved problem
leetcode-picker review --weeks-ago 4

# Override difficulty for a problem
leetcode-picker override-difficulty https://leetcode.com/problems/hard-problem/ easy

# List completed Grind75 titles (in Grind75 order)
leetcode-picker grind75-completed

# Force refresh of study plans and update local DB
leetcode-picker refresh
```

## Commands

### `choose` - Pick a random unsolved problem
- `--difficulty`: Filter by difficulty (easy, medium, hard)
- `--study-plan`: Filter by study plan (leetcode-75, top-interview-150)

### `review` - Pick a random previously solved problem  
- `--weeks-ago`: Only show problems solved at least N weeks ago
- `--difficulty`: Filter by difficulty (easy, medium, hard)

### `mark-complete` - Mark a problem as completed
- `url`: The LeetCode problem URL
- `--date`: Completion date (YYYY-MM-DD, defaults to today)

### `override-difficulty` - Override difficulty level
- `url`: The LeetCode problem URL  
- `difficulty`: New difficulty level (easy, medium, hard)

### `progress` - Show progress on study plans
Shows completion percentages for each study plan.

### `grind75-completed` - List completed Grind75 titles in order
Outputs the titles (with LeetCode URLs) of your completed problems in the same
order as the Grind75 list, along with a completion summary. Use this to manually
mark them complete on the Grind75 website.

### `refresh` - Re-scrape study plans and update local database
Forces a refresh of the local problem database by scraping all configured study
plans again. This merges study plan URLs into existing problems and preserves
your completion data.

## Data Storage

Problems are stored in `~/.leetcode-picker/problems.csv` with the following fields:
- URL, title, difficulty, study plan URL
- Last completion date, number of completions/submissions
- Overridden difficulty level

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run linter (required before commits)
./black-flake8-mypy leetcode_picker/

# Run CLI during development
python -m leetcode_picker.main --help
```

## Study Plans

The tool automatically scrapes problems from:
- **LeetCode 75**: https://leetcode.com/studyplan/leetcode-75/
- **Top Interview 150**: https://leetcode.com/studyplan/top-interview-150/

Problems are fetched automatically on first run and can be updated by running any command.
