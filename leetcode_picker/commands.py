"""CLI command implementations."""

import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional

from .scraper import LeetCodeScraper, STUDY_PLANS
from .storage import ProblemStorage


def choose_problem(difficulty: Optional[str], study_plan: Optional[str]) -> None:
    """Choose a random unsolved problem."""
    storage = ProblemStorage()

    # First ensure we have problems in the database
    _ensure_problems_loaded(storage)

    # Get unsolved problems
    problems = storage.get_unsolved_problems()

    # Filter by difficulty if specified
    if difficulty:
        problems = [p for p in problems if p.effective_difficulty == difficulty]

    # Filter by study plan if specified
    if study_plan:
        if study_plan not in ["leetcode-75", "top-interview-150"]:
            print(f"Unknown study plan: {study_plan}")
            print("Available plans: leetcode-75, top-interview-150")
            return

        problems = [p for p in problems if study_plan in p.study_plan_url]
    else:
        # Default: only show problems from main study plans
        problems = [
            p
            for p in problems
            if any(plan in p.study_plan_url for plan in STUDY_PLANS.values())
        ]

    if not problems:
        print("No unsolved problems found with the given criteria.")
        return

    # Choose a random problem
    chosen = random.choice(problems)

    print(f"Selected problem: {chosen.title}")
    print(f"Difficulty: {chosen.effective_difficulty}")
    print(f"URL: {chosen.url}")
    if chosen.overridden_difficulty:
        print(f"Original difficulty: {chosen.difficulty} (overridden)")


def review_problem(weeks_ago: Optional[int], difficulty: Optional[str]) -> None:
    """Choose a random previously solved problem."""
    storage = ProblemStorage()

    # Get completed problems
    problems = storage.get_completed_problems()

    # Filter by difficulty if specified
    if difficulty:
        problems = [p for p in problems if p.effective_difficulty == difficulty]

    # Filter by weeks ago if specified
    if weeks_ago:
        cutoff_date = (datetime.now() - timedelta(weeks=weeks_ago)).strftime("%Y-%m-%d")
        problems = [
            p for p in problems if p.last_pass_date and p.last_pass_date <= cutoff_date
        ]

    if not problems:
        print("No completed problems found with the given criteria.")
        return

    # Choose a random problem
    chosen = random.choice(problems)

    print(f"Review problem: {chosen.title}")
    print(f"Difficulty: {chosen.effective_difficulty}")
    print(f"URL: {chosen.url}")
    print(f"Last completed: {chosen.last_pass_date}")
    print(f"Completions: {chosen.completions}/{chosen.submissions}")


def override_difficulty(url: str, difficulty: str) -> None:
    """Override difficulty level for a problem."""
    storage = ProblemStorage()

    problem = storage.get_problem(url)
    if not problem:
        print(f"Problem not found: {url}")
        print("Make sure the URL is correct and the problem is in the database.")
        return

    old_difficulty = problem.effective_difficulty
    problem.overridden_difficulty = difficulty
    storage.add_or_update_problem(problem)

    print(f"Updated difficulty for {problem.title}")
    print(f"  {old_difficulty} → {difficulty}")


def show_progress() -> None:
    """Show progress on study plans."""
    storage = ProblemStorage()

    # First ensure we have problems in the database
    _ensure_problems_loaded(storage)

    # Get all problems grouped by study plan
    plan_stats: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"total": 0, "completed": 0}
    )

    problems = storage.load_problems()

    for problem in problems.values():
        # Determine which study plan this belongs to
        plan_name = "unknown"
        for name, url in STUDY_PLANS.items():
            if url in problem.study_plan_url:
                plan_name = name
                break

        plan_stats[plan_name]["total"] += 1
        if problem.is_completed:
            plan_stats[plan_name]["completed"] += 1

    print("Study Plan Progress:")
    print("=" * 50)

    for plan_name, stats in plan_stats.items():
        if stats["total"] == 0:
            continue

        completed = stats["completed"]
        total = stats["total"]
        percentage = (completed / total) * 100 if total > 0 else 0

        print(f"{plan_name}:")
        print(f"  Progress: {completed}/{total} ({percentage:.1f}%)")
        print(f"  Remaining: {total - completed}")
        print()


def mark_complete(url: str, date: Optional[str]) -> None:
    """Mark a problem as completed."""
    storage = ProblemStorage()

    problem = storage.get_problem(url)
    if not problem:
        print(f"Problem not found: {url}")
        print("Make sure the URL is correct and the problem is in the database.")
        return

    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

    old_completions = problem.completions
    problem.mark_completed(date)
    storage.add_or_update_problem(problem)

    print(f"Marked {problem.title} as completed")
    print(f"  Date: {problem.last_pass_date}")
    print(f"  Completions: {old_completions} → {problem.completions}")


def _ensure_problems_loaded(storage: ProblemStorage) -> None:
    """Ensure the problem database has data, scrape if needed."""
    problems = storage.load_problems()

    if not problems:
        print("No problems found in database. Scraping study plans...")
        scraper = LeetCodeScraper()
        scraper.update_problem_database(storage)
        print("Problem database updated!")
