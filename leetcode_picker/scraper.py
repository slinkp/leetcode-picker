"""LeetCode study plan scraper and problem fetcher."""

import re
import time
import sys
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

    def scrape_grind75(self, verbose: bool = False) -> List[Problem]:
        """Scrape Grind75 page (no grouping) in on-page order, deduped by URL."""
        problems: List[Problem] = []
        grind75_url = STUDY_PLANS["grind75"]

        # Always use "no grouping" view for stable order
        fetch_url = grind75_url.rstrip("/")
        if "grouping=" not in fetch_url:
            fetch_url = f"{fetch_url}/?grouping=none"

        try:
            if verbose:
                print(f"[grind75] GET {fetch_url}", file=sys.stderr)
            resp = self.session.get(fetch_url)
            if verbose:
                print(
                    f"[grind75] status={resp.status_code} bytes={len(resp.text)}",
                    file=sys.stderr,
                )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error scraping grind75: {e}")
            return problems

        soup = BeautifulSoup(resp.content, "html.parser")

        # Extract LeetCode problem URLs from raw HTML (Next.js JSON), preserve order
        html = resp.text
        if verbose:
            snippet = html[:4000]
            print("[grind75] html head snippet:", file=sys.stderr)
            print(snippet, file=sys.stderr)

        seen_slugs: set[str] = set()
        items: List[Dict[str, str]] = []

        pattern = r"https?://leetcode\.com/problems/([a-z0-9\-]+)/?"
        total_occurrences = len(re.findall(pattern, html, flags=re.I))
        if verbose:
            print(
                f"[grind75] total link occurrences: {total_occurrences}", file=sys.stderr
            )

        for m in re.finditer(pattern, html, re.I):
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

        # Fallback: scan Next.js chunk scripts if main HTML had no links
        if not items:
            script_tags = soup.find_all("script", src=True)
            script_srcs = [tag.get("src", "") for tag in script_tags if tag.get("src")]
            # Consider only Next.js chunk scripts
            chunk_srcs = [
                s
                for s in script_srcs
                if "/_next/static/chunks/" in s and s.endswith(".js")
            ]

            # Normalize to absolute URLs
            def abs_url(u: str) -> str:
                return (
                    u
                    if u.startswith("http")
                    else f"https://www.techinterviewhandbook.org{u}"
                )

            chunk_urls = [abs_url(s) for s in chunk_srcs]

            # Prioritize the main page chunk for better ordering
            chunk_urls.sort(key=lambda u: (("app/page" not in u), u))

            if verbose:
                print(
                    f"[grind75] chunk scripts found: {len(chunk_urls)}", file=sys.stderr
                )
                for u in chunk_urls[:5]:
                    print(f"[grind75] chunk: {u}", file=sys.stderr)

            # Patterns to match URLs and slugs in various encodings
            patterns = [
                r"https?://leetcode\.com/problems/([a-z0-9\-]+)/?",
                r"leetcode\.com\\?/problems\\?/([a-z0-9\-]+)",
                r'["\']/?problems/([a-z0-9\-]+)/?["\']',
            ]

            for js_url in chunk_urls:
                try:
                    if verbose:
                        print(f"[grind75] GET {js_url}", file=sys.stderr)
                    js_resp = self.session.get(js_url)
                    if verbose:
                        print(
                            f"[grind75] {js_url} status={js_resp.status_code} "
                            f"bytes={len(js_resp.text)}",
                            file=sys.stderr,
                        )
                    js_resp.raise_for_status()
                except requests.RequestException as e:
                    if verbose:
                        print(
                            f"[grind75] error fetching chunk {js_url}: {e}",
                            file=sys.stderr,
                        )
                    continue

                js = js_resp.text
                before = len(items)

                for pat in patterns:
                    for mm in re.finditer(pat, js, re.I):
                        slug = mm.group(1).lower()
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

                        items.append(
                            {"title": title, "url": lc_url, "difficulty": "medium"}
                        )

                if verbose:
                    added = len(items) - before
                    print(
                        f"[grind75] {js_url} added {added}, total={len(items)}",
                        file=sys.stderr,
                    )

                # Stop once we likely have the full list
                if len(items) >= 75:
                    break

        if verbose:
            print(f"[grind75] unique slugs found: {len(seen_slugs)}", file=sys.stderr)
            if items:
                sample = [it["url"] for it in items[:15]]
                print("[grind75] first URLs:", file=sys.stderr)
                for u in sample:
                    print(f"  {u}", file=sys.stderr)
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

    def scrape_all_study_plans(self, verbose: bool = False) -> Dict[str, List[Problem]]:
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
        grind75_problems = self.scrape_grind75(verbose=verbose)
        all_problems["grind75"] = grind75_problems

        return all_problems

    def update_problem_database(self, storage, verbose: bool = False) -> None:
        """Update the problem database with scraped data, merging overlapping problems."""
        all_problems = self.scrape_all_study_plans(verbose=verbose)

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
