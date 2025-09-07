"""LeetCode study plan scraper and problem fetcher."""

import re
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from .models import Problem

# Study plan URLs
STUDY_PLANS = {
    "leetcode-75": "https://leetcode.com/studyplan/leetcode-75/",
    "top-interview-150": "https://leetcode.com/studyplan/top-interview-150/",
}

# Optional study plan
OPTIONAL_STUDY_PLANS = {
    "grind75": "https://www.techinterviewhandbook.org/grind75/",
}


class LeetCodeScraper:
    """Scrapes LeetCode study plans for problem lists."""

    def __init__(self):
        """Initialize scraper with session."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            }
        )

    def scrape_leetcode_study_plan(self, plan_name: str, plan_url: str) -> List[Problem]:
        """Scrape a LeetCode study plan for problem list."""
        problems = []

        try:
            response = self.session.get(plan_url)
            response.raise_for_status()

            # LeetCode uses GraphQL and dynamic loading, so we need to extract
            # the initial data from the page
            soup = BeautifulSoup(response.content, "html.parser")

            # Look for script tags containing problem data
            script_tags = soup.find_all("script")

            for script in script_tags:
                if script.string and "studyPlan" in script.string:
                    # Extract problem URLs and titles using regex
                    # This is a simplified approach - real implementation might
                    # need to handle GraphQL responses
                    problem_matches = re.findall(
                        r'"titleSlug":"([^"]+)".*?"title":"([^"]+)".*?"difficulty":"([^"]+)"',
                        script.string,
                    )

                    for slug, title, difficulty in problem_matches:
                        problem_url = f"https://leetcode.com/problems/{slug}/"
                        problems.append(
                            Problem(
                                url=problem_url,
                                title=title,
                                difficulty=difficulty.lower(),
                                study_plan_url=plan_url,
                            )
                        )

            # If no problems found via script extraction, try HTML parsing
            if not problems:
                problems = self._fallback_html_parsing(plan_url, soup)

        except requests.RequestException as e:
            print(f"Error scraping {plan_name}: {e}")

        return problems

    def _fallback_html_parsing(self, plan_url: str, soup: BeautifulSoup) -> List[Problem]:
        """Fallback HTML parsing for problem extraction."""
        problems = []

        # Look for problem links in common patterns
        problem_links = soup.find_all("a", href=re.compile(r"/problems/[^/]+/?$"))

        for link in problem_links:
            href = link.get("href")
            if href.startswith("/problems/"):
                problem_url = f"https://leetcode.com{href}"
                title = link.get_text(strip=True)

                # Default difficulty if not found
                difficulty = "medium"

                # Try to find difficulty nearby
                difficulty_elem = link.find_next(string=re.compile(r"Easy|Medium|Hard"))
                if difficulty_elem:
                    difficulty = difficulty_elem.strip().lower()

                problems.append(
                    Problem(
                        url=problem_url,
                        title=title,
                        difficulty=difficulty,
                        study_plan_url=plan_url,
                    )
                )

        return problems

    def scrape_grind75(self) -> List[Problem]:
        """Scrape Grind75 problems (simplified implementation)."""
        problems = []
        grind75_url = OPTIONAL_STUDY_PLANS["grind75"]

        try:
            response = self.session.get(grind75_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Grind75 has a different structure - this is a placeholder
            # Real implementation would need to handle their specific format
            problem_elements = soup.find_all("div", class_="problem")

            for elem in problem_elements:
                # Extract problem details from Grind75 format
                title_elem = elem.find("a")
                if title_elem:
                    # Convert Grind75 links to LeetCode URLs
                    title = title_elem.get_text(strip=True)
                    # This would need real logic to map titles to LeetCode URLs
                    problem_url = self._map_title_to_leetcode_url(title)

                    if problem_url:
                        problems.append(
                            Problem(
                                url=problem_url,
                                title=title,
                                difficulty="medium",  # Default
                                study_plan_url=grind75_url,
                            )
                        )

        except requests.RequestException as e:
            print(f"Error scraping Grind75: {e}")

        return problems

    def _map_title_to_leetcode_url(self, title: str) -> str:
        """Map problem title to LeetCode URL (simplified)."""
        # This would need a comprehensive mapping or search functionality
        slug = title.lower().replace(" ", "-").replace("(", "").replace(")", "")
        return f"https://leetcode.com/problems/{slug}/"

    def scrape_all_study_plans(self) -> Dict[str, List[Problem]]:
        """Scrape all configured study plans."""
        all_problems = {}

        # Scrape main study plans
        for plan_name, plan_url in STUDY_PLANS.items():
            print(f"Scraping {plan_name}...")
            problems = self.scrape_leetcode_study_plan(plan_name, plan_url)
            all_problems[plan_name] = problems
            time.sleep(1)  # Be nice to the server

        # Optionally scrape Grind75
        print("Scraping Grind75...")
        grind75_problems = self.scrape_grind75()
        if grind75_problems:
            all_problems["grind75"] = grind75_problems

        return all_problems

    def update_problem_database(self, storage) -> None:
        """Update the problem database with scraped data."""
        all_problems = self.scrape_all_study_plans()

        total_added = 0
        for plan_name, problems in all_problems.items():
            for problem in problems:
                # Check if problem already exists
                existing = storage.get_problem(problem.url)
                if existing:
                    # Update title and difficulty if needed
                    existing.title = problem.title
                    existing.difficulty = problem.difficulty
                    storage.add_or_update_problem(existing)
                else:
                    # Add new problem
                    storage.add_or_update_problem(problem)
                    total_added += 1

        print(f"Added {total_added} new problems to database")
