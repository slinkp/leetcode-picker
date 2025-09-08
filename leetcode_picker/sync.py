"""Sync LeetCode submission history with local database."""

from typing import Dict, List, Optional

from .auth import LeetCodeAuth
from .storage import ProblemStorage


class LeetCodeSync:
    """Syncs LeetCode submission data with local problem database."""

    def __init__(self):
        """Initialize sync with auth and storage."""
        self.auth = LeetCodeAuth()
        self.storage = ProblemStorage()

    def get_user_submissions(self, offset: int = 0, limit: int = 100) -> Optional[Dict]:
        """Get user's submission history from LeetCode GraphQL API."""
        session = self.auth.get_authenticated_session()
        if not session:
            return None

        query = {
            "query": """
            query userSubmissions($offset: Int, $limit: Int) {
                submissionList(offset: $offset, limit: $limit) {
                    submissions {
                        id
                        title
                        titleSlug
                        status
                        statusDisplay
                        lang
                        timestamp
                        url
                        isPending
                        memory
                        runtime
                        __typename
                    }
                    hasNext
                    totalSubmissions
                }
            }
            """,
            "variables": {"offset": offset, "limit": limit},
        }

        try:
            response = session.post(
                "https://leetcode.com/graphql", json=query, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data and "submissionList" in data["data"]:
                return data["data"]["submissionList"]
            return None
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return None

    def get_all_submissions(self) -> List[Dict]:
        """Get all user submissions by paginating through results."""
        all_submissions = []
        offset = 0
        limit = 100

        print("Fetching submission history...")

        while True:
            result = self.get_user_submissions(offset, limit)
            if not result or not result.get("submissions"):
                break

            submissions = result["submissions"]
            all_submissions.extend(submissions)

            print(f"Fetched {len(all_submissions)} submissions so far...")

            if not result.get("hasNext", False):
                break

            offset += limit

        print(f"Total submissions found: {len(all_submissions)}")
        return all_submissions

    def get_accepted_problems(self) -> Dict[str, Dict]:
        """Get only accepted submissions, grouped by problem."""
        submissions = self.get_all_submissions()
        accepted_problems = {}

        for submission in submissions:
            if submission.get("status") != 10:  # 10 = Accepted
                continue

            title_slug = submission.get("titleSlug")
            if not title_slug:
                continue

            problem_url = f"https://leetcode.com/problems/{title_slug}/"

            # Track the earliest acceptance and total accepted submissions
            if problem_url not in accepted_problems:
                accepted_problems[problem_url] = {
                    "title": submission.get("title", ""),
                    "first_accepted": submission.get("timestamp", 0),
                    "last_accepted": submission.get("timestamp", 0),
                    "total_accepted": 0,
                    "languages": set(),
                }

            problem_data = accepted_problems[problem_url]
            timestamp = submission.get("timestamp", 0)

            # Update timestamps
            if timestamp < problem_data["first_accepted"]:
                problem_data["first_accepted"] = timestamp
            if timestamp > problem_data["last_accepted"]:
                problem_data["last_accepted"] = timestamp

            problem_data["total_accepted"] += 1

            # Track languages used
            lang = submission.get("lang")
            if lang:
                problem_data["languages"].add(lang)

        return accepted_problems

    def sync_submission_data(self) -> None:
        """Sync LeetCode submission data with local problem database."""
        if not self.auth.test_authentication():
            print("❌ Authentication failed. Run 'leetcode-picker auth' first.")
            return

        print("🔄 Syncing submission history with local database...")

        # Get accepted problems from LeetCode
        accepted_problems = self.get_accepted_problems()

        if not accepted_problems:
            print("No accepted submissions found.")
            return

        # Load existing problems from database
        existing_problems = self.storage.load_problems()

        updated_count = 0
        new_problems_found = 0

        for problem_url, submission_data in accepted_problems.items():
            if problem_url in existing_problems:
                # Update existing problem
                problem = existing_problems[problem_url]

                # Convert timestamp to date (LeetCode uses Unix timestamp)
                import datetime

                last_date = datetime.datetime.fromtimestamp(
                    submission_data["last_accepted"]
                ).strftime("%Y-%m-%d")

                # Update completion data
                problem.last_pass_date = last_date
                problem.completions = submission_data["total_accepted"]
                problem.submissions = submission_data[
                    "total_accepted"
                ]  # Conservative estimate

                self.storage.add_or_update_problem(problem)
                updated_count += 1
            else:
                # Problem not in our database - might be outside study plans
                new_problems_found += 1
                print(f"Found problem not in study plans: {submission_data['title']}")

        print("✅ Sync complete!")
        print(f"   Updated {updated_count} problems with submission data")
        if new_problems_found > 0:
            print(
                f"   Found {new_problems_found} additional problems outside study plans"
            )

    def get_stats(self) -> Dict[str, int]:
        """Get basic stats about synced data."""
        if not self.auth.test_authentication():
            return {}

        accepted_problems = self.get_accepted_problems()
        existing_problems = self.storage.load_problems()

        synced_count = sum(
            1 for url in accepted_problems.keys() if url in existing_problems
        )

        return {
            "total_accepted": len(accepted_problems),
            "in_study_plans": synced_count,
            "outside_study_plans": len(accepted_problems) - synced_count,
        }
