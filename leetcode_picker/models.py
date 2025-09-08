"""Data models for LeetCode problems and tracking."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Problem:
    """Represents a LeetCode problem with tracking information."""

    url: str
    title: str
    difficulty: str
    study_plan_urls: list[str]  # Can belong to multiple study plans
    last_pass_date: Optional[str] = None  # YYYY-MM-DD format
    completions: int = 0
    submissions: int = 0
    overridden_difficulty: Optional[str] = None

    # Backward compatibility property
    @property
    def study_plan_url(self) -> str:
        """Get the first study plan URL for backward compatibility."""
        return self.study_plan_urls[0] if self.study_plan_urls else ""

    @property
    def effective_difficulty(self) -> str:
        """Get the effective difficulty (overridden or original)."""
        return self.overridden_difficulty or self.difficulty

    @property
    def is_completed(self) -> bool:
        """Check if the problem has been completed at least once."""
        return self.completions > 0

    def mark_completed(self, date: Optional[str] = None) -> None:
        """Mark the problem as completed on the given date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        self.last_pass_date = date
        self.completions += 1
        self.submissions += 1

    def add_submission(self) -> None:
        """Add a failed submission."""
        self.submissions += 1
