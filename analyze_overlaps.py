#!/usr/bin/env python3
"""Analyze overlapping problems between study plans."""

from leetcode_picker.scraper import LeetCodeScraper, STUDY_PLANS
from collections import defaultdict


def analyze_overlaps():
    """Find problems that appear in multiple study plans."""
    scraper = LeetCodeScraper()

    # Get problems from each study plan
    all_problems_by_plan = {}
    problem_to_plans = defaultdict(list)

    for plan_name, plan_url in STUDY_PLANS.items():
        print(f"Scraping {plan_name}...")
        problems = scraper.scrape_leetcode_study_plan(plan_name, plan_url)
        all_problems_by_plan[plan_name] = problems

        print(f"Found {len(problems)} problems in {plan_name}")

        # Map each problem URL to which plans it appears in
        for problem in problems:
            problem_to_plans[problem.url].append(plan_name)

    # Find overlapping problems
    overlapping_problems = {
        url: plans for url, plans in problem_to_plans.items() if len(plans) > 1
    }

    print(f"\nOverlap Analysis:")
    print(f"Total unique problems: {len(problem_to_plans)}")
    print(f"Problems in multiple plans: {len(overlapping_problems)}")

    if overlapping_problems:
        print(f"\nOverlapping problems:")
        for url, plans in overlapping_problems.items():
            # Find the problem title
            title = "Unknown"
            for plan_name in plans:
                for problem in all_problems_by_plan[plan_name]:
                    if problem.url == url:
                        title = problem.title
                        break
            print(f"  {title}")
            print(f"    URL: {url}")
            print(f"    Plans: {', '.join(plans)}")
            print()

    # Summary by plan
    print("Plan summaries:")
    for plan_name, problems in all_problems_by_plan.items():
        print(f"  {plan_name}: {len(problems)} problems")

    return overlapping_problems, problem_to_plans


if __name__ == "__main__":
    analyze_overlaps()
