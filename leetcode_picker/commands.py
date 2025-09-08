"""CLI command implementations."""

import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional

from .auth import LeetCodeAuth
from .scraper import LeetCodeScraper, STUDY_PLANS
from .storage import ProblemStorage
from .sync import LeetCodeSync


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
        if study_plan not in ["leetcode-75", "top-interview-150", "grind75"]:
            print(f"Unknown study plan: {study_plan}")
            print("Available plans: leetcode-75, top-interview-150, grind75")
            return

        problems = [
            p for p in problems if any(study_plan in url for url in p.study_plan_urls)
        ]
    else:
        # Default: only show problems from main study plans
        problems = [
            p
            for p in problems
            if any(
                plan in url for plan in STUDY_PLANS.values() for url in p.study_plan_urls
            )
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
        # Check which study plans this problem belongs to (can be multiple)
        for plan_name, plan_url in STUDY_PLANS.items():
            if any(plan_url in url for url in problem.study_plan_urls):
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


def list_grind75_completed_titles() -> None:
    """Print completed problem titles in Grind75 order for manual marking."""
    storage = ProblemStorage()
    _ensure_problems_loaded(storage)
    problems = storage.load_problems()

    scraper = LeetCodeScraper()
    try:
        grind_problems = scraper.scrape_grind75()
    except Exception as exc:  # pragma: no cover
        print(f"Error scraping Grind75: {exc}")
        return

    completed: list[tuple[int, str]] = []
    for idx, p in enumerate(grind_problems, start=1):
        local = problems.get(p.url)
        if local and local.is_completed:
            completed.append((idx, p.title))

    for idx, title in completed:
        print(f"{idx}. {title}")

    print(f"\nTotal completed in Grind75: {len(completed)}/{len(grind_problems)}")


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


def setup_auth() -> None:
    """Set up LeetCode authentication by guiding user through cookie extraction."""
    auth = LeetCodeAuth()

    print("🔐 LeetCode Authentication Setup")
    print("=" * 40)
    print()
    print("To authenticate with LeetCode, you need to extract cookies from your browser.")
    print()
    print("📋 Step-by-step instructions:")
    print()
    print("1. Open your browser and go to https://leetcode.com")
    print("2. Make sure you're logged in (you should see your profile)")
    print("3. Right-click anywhere on the page and select 'Inspect' (or press F12)")
    print("4. Go to the 'Network' tab in the developer tools")
    print("5. Refresh the page (F5 or Ctrl+R)")
    print("6. Look for a request to 'leetcode.com' in the network requests")
    print("7. Click on that request and look at the 'Request Headers' section")
    print("8. Find the 'Cookie' header and copy the values for:")
    print("   - LEETCODE_SESSION (long string starting with 'eyJ')")
    print("   - csrftoken (shorter alphanumeric string)")
    print()
    print(
        "Alternatively, you can go to chrome://settings/cookies/detail?site=leetcode.com"
    )
    print("and find the LEETCODE_SESSION and csrftoken values there.")
    print()

    # Get cookies from user
    print("Please enter your cookies:")
    session_cookie = input("LEETCODE_SESSION: ").strip()
    csrf_token = input("csrftoken: ").strip()

    if not session_cookie or not csrf_token:
        print("❌ Both cookies are required. Please try again.")
        return

    # Save cookies
    auth.save_cookies(session_cookie, csrf_token)
    print(f"✅ Cookies saved to {auth.auth_file}")

    # Test authentication
    print("\n🔍 Testing authentication...")
    if auth.test_authentication():
        user_info = auth.get_user_info()
        if user_info:
            username = user_info.get("username", "Unknown")
            first_name = user_info.get("firstName", "")
            last_name = user_info.get("lastName", "")
            full_name = f"{first_name} {last_name}".strip()

            print("✅ Authentication successful!")
            print(f"   User: {username}")
            if full_name:
                print(f"   Name: {full_name}")

            # Show profile info if available
            profile = user_info.get("profile", {})
            if profile and profile.get("ranking"):
                print(f"   Ranking: {profile['ranking']}")
        else:
            print("✅ Authentication working, but couldn't fetch user info.")
    else:
        print("❌ Authentication failed. Please check your cookies and try again.")
        print("   Make sure you're logged into LeetCode and the cookies are correct.")


def sync_submissions() -> None:
    """Sync submission history from LeetCode."""
    sync = LeetCodeSync()
    sync.sync_submission_data()


def _ensure_problems_loaded(storage: ProblemStorage) -> None:
    """Ensure the problem database has data, scrape if needed."""
    problems = storage.load_problems()

    if not problems:
        print("No problems found in database. Scraping study plans...")
        scraper = LeetCodeScraper()
        scraper.update_problem_database(storage)
        print("Problem database updated!")
