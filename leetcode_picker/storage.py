"""CSV storage for problem data."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import Problem

DEFAULT_DATA_FILE = Path.home() / ".leetcode-picker" / "problems.csv"

# CSV headers
HEADERS = [
    "url",
    "title",
    "difficulty",
    "study_plan_urls",  # Now stores JSON array of URLs
    "last_pass_date",
    "completions",
    "submissions",
    "overridden_difficulty",
]


class ProblemStorage:
    """Handles CSV storage and retrieval of problem data."""

    def __init__(self, data_file: Optional[Path] = None):
        """Initialize storage with optional custom data file path."""
        self.data_file = data_file or DEFAULT_DATA_FILE
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self) -> None:
        """Ensure the data file and its directory exist."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            # Create empty CSV with headers
            with open(self.data_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=HEADERS)
                writer.writeheader()

    def load_problems(self) -> Dict[str, Problem]:
        """Load all problems from CSV file, indexed by URL."""
        problems = {}

        with open(self.data_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle backward compatibility for old format
                if "study_plan_url" in row:
                    # Old format - single URL
                    study_plan_urls = (
                        [row["study_plan_url"]] if row["study_plan_url"] else []
                    )
                else:
                    # New format - JSON array of URLs
                    try:
                        study_plan_urls = (
                            json.loads(row["study_plan_urls"])
                            if row["study_plan_urls"]
                            else []
                        )
                    except (json.JSONDecodeError, KeyError):
                        study_plan_urls = []

                problem = Problem(
                    url=row["url"],
                    title=row["title"],
                    difficulty=row["difficulty"],
                    study_plan_urls=study_plan_urls,
                    last_pass_date=row["last_pass_date"] or None,
                    completions=int(row["completions"]) if row["completions"] else 0,
                    submissions=int(row["submissions"]) if row["submissions"] else 0,
                    overridden_difficulty=row["overridden_difficulty"] or None,
                )
                problems[problem.url] = problem

        return problems

    def save_problems(self, problems: Dict[str, Problem]) -> None:
        """Save all problems to CSV file."""
        with open(self.data_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()

            for problem in problems.values():
                writer.writerow(
                    {
                        "url": problem.url,
                        "title": problem.title,
                        "difficulty": problem.difficulty,
                        "study_plan_urls": json.dumps(problem.study_plan_urls),
                        "last_pass_date": problem.last_pass_date or "",
                        "completions": problem.completions,
                        "submissions": problem.submissions,
                        "overridden_difficulty": problem.overridden_difficulty or "",
                    }
                )

    def add_or_update_problem(self, problem: Problem) -> None:
        """Add a new problem or update an existing one."""
        problems = self.load_problems()
        problems[problem.url] = problem
        self.save_problems(problems)

    def get_problem(self, url: str) -> Optional[Problem]:
        """Get a specific problem by URL."""
        problems = self.load_problems()
        return problems.get(url)

    def get_problems_by_study_plan(self, study_plan: str) -> List[Problem]:
        """Get all problems from a specific study plan."""
        problems = self.load_problems()
        return [p for p in problems.values() if study_plan in p.study_plan_url]

    def get_problems_by_difficulty(self, difficulty: str) -> List[Problem]:
        """Get all problems with a specific effective difficulty."""
        problems = self.load_problems()
        return [p for p in problems.values() if p.effective_difficulty == difficulty]

    def get_completed_problems(self) -> List[Problem]:
        """Get all completed problems."""
        problems = self.load_problems()
        return [p for p in problems.values() if p.is_completed]

    def get_unsolved_problems(self) -> List[Problem]:
        """Get all unsolved problems."""
        problems = self.load_problems()
        return [p for p in problems.values() if not p.is_completed]
