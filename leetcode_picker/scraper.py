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
                                study_plan_urls=[plan_url],
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
                        study_plan_urls=[plan_url],
                    )
                )

        return problems

    def scrape_grind75(self) -> List[Problem]:
        """Scrape Grind75 page (no grouping) in on-page order, deduped by URL."""
        problems: List[Problem] = []
        grind75_url = STUDY_PLANS["grind75"]

        # Always use "no grouping" view for stable order
        fetch_url = grind75_url.rstrip("/")
        if "grouping=" not in fetch_url:
            fetch_url = f"{fetch_url}/?grouping=none"

        try:
            resp = self.session.get(fetch_url)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error scraping grind75: {e}")
            return problems

        soup = BeautifulSoup(resp.content, "html.parser")

        # Extract LeetCode problem URLs from raw HTML (Next.js JSON), preserve order
        html = resp.text

        seen_slugs: set[str] = set()
        items: List[Dict[str, str]] = []

        for m in re.finditer(
            r"https?://leetcode\.com/problems/([a-z0-9\-]+)/?", html, re.I
        ):
            slug = m.group(1).lower()
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            lc_url = f"https://leetcode.com/problems/{slug}/"

            # Derive a readable title from slug; local DB title is preferred later
            title = slug.replace("-", " ").title()
            title = (
                title.replace("Ii", "II")
                .replace("Iii", "III")
                .replace("Iv", "IV")
                .replace("Bst", "BST")
                .replace("Lru", "LRU")
                .replace("Atoi", "atoi")
            )
            if slug == "01-matrix":
                title = "01 Matrix"
            if slug == "3sum":
                title = "3Sum"

            items.append({"title": title, "url": lc_url, "difficulty": "medium"})

        if len(items) != 75:
            print(f"Warning: Grind75 scrape yielded {len(items)} items (expected 75)")

        for it in items[:75]:
            problems.append(
                Problem(
                    url=it["url"],
                    title=it["title"],
                    difficulty=it["difficulty"],
                    study_plan_urls=[grind75_url],
                )
            )

        return problems

    def _map_title_to_leetcode_url(self, title: str) -> str:
        """Map problem title to LeetCode URL with proper handling of special cases."""
        # Convert to lowercase and handle special characters
        slug = title.lower()

        # Handle special cases that don't follow standard patterns
        special_cases = {
            "01 matrix": "01-matrix",
            "3sum": "3sum",
            "kth smallest element in a bst": "kth-smallest-element-in-a-bst",
            "lru cache": "lru-cache",
            "string to integer (atoi)": "string-to-integer-atoi",
        }

        if slug in special_cases:
            return f"https://leetcode.com/problems/{special_cases[slug]}/"

        # Standard conversion: remove special characters and convert spaces to hyphens
        slug = slug.replace("(", "").replace(")", "").replace(",", "")
        slug = slug.replace(" - ", "-").replace(" ", "-")
        slug = slug.replace("--", "-").strip("-")

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

        # Scrape Grind75
        print("Scraping Grind75...")
        grind75_problems = self.scrape_grind75()
        all_problems["grind75"] = grind75_problems

        return all_problems

    def update_problem_database(self, storage) -> None:
        """Update the problem database with scraped data, merging overlapping problems."""
        all_problems = self.scrape_all_study_plans()

        # Collect all problems and merge overlaps
        merged_problems: Dict[str, Problem] = {}

        for plan_name, problems in all_problems.items():
            for problem in problems:
                if problem.url in merged_problems:
                    # Problem exists - merge study plan URLs
                    existing = merged_problems[problem.url]
                    # Add the new study plan URL if not already present
                    if problem.study_plan_urls[0] not in existing.study_plan_urls:
                        existing.study_plan_urls.extend(problem.study_plan_urls)
                else:
                    # New problem
                    merged_problems[problem.url] = problem

        # Save merged problems to database
        existing_db_problems = storage.load_problems()
        total_added = 0
        total_updated = 0

        for problem in merged_problems.values():
            if problem.url in existing_db_problems:
                # Update existing problem, preserve completion data
                existing = existing_db_problems[problem.url]
                existing.title = problem.title
                existing.difficulty = problem.difficulty
                existing.study_plan_urls = (
                    problem.study_plan_urls
                )  # Update with merged list
                storage.add_or_update_problem(existing)
                total_updated += 1
            else:
                # Add new problem
                storage.add_or_update_problem(problem)
                total_added += 1

        print(
            f"Added {total_added} new problems, updated {total_updated} existing problems"
        )
