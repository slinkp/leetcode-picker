#!/usr/bin/env python3
"""Debug script to test submission pagination."""

from leetcode_picker.sync import LeetCodeSync


def test_pagination():
    """Test how many submissions we can actually fetch."""
    sync = LeetCodeSync()

    # Test getting larger batches
    print("Testing larger batch sizes...")

    for limit in [20, 50, 100, 200]:
        print(f"\nTesting limit={limit}")
        result = sync.get_user_submissions(offset=0, limit=limit)
        if result:
            submissions = result.get("submissions", [])
            has_next = result.get("hasNext", False)
            print(f"  Got {len(submissions)} submissions")
            print(f"  Has next: {has_next}")

            if submissions:
                first_title = submissions[0].get("title", "Unknown")
                last_title = submissions[-1].get("title", "Unknown")
                print(f"  First: {first_title}")
                print(f"  Last: {last_title}")
        else:
            print("  Failed to get submissions")

    # Test getting all with smaller batches
    print(f"\n{'='*50}")
    print("Testing complete pagination with limit=50...")

    all_submissions = []
    offset = 0
    limit = 50
    page = 1

    while True:
        print(f"Page {page} (offset={offset})...")
        result = sync.get_user_submissions(offset, limit)
        if not result or not result.get("submissions"):
            print("  No more submissions")
            break

        submissions = result["submissions"]
        all_submissions.extend(submissions)
        has_next = result.get("hasNext", False)

        print(f"  Got {len(submissions)} submissions (total: {len(all_submissions)})")
        print(f"  Has next: {has_next}")

        if not has_next:
            print("  Reached end")
            break

        offset += limit
        page += 1

        # Safety limit
        if page > 20:
            print("  Stopping at page 20 for safety")
            break

    print(f"\nFinal total: {len(all_submissions)} submissions")

    # Count accepted submissions
    accepted = [s for s in all_submissions if s.get("status") == 10]
    print(f"Accepted submissions: {len(accepted)}")

    # Group by problem to see unique problems
    unique_problems = {}
    for sub in accepted:
        title_slug = sub.get("titleSlug")
        if title_slug:
            unique_problems[title_slug] = sub.get("title", "")

    print(f"Unique accepted problems: {len(unique_problems)}")


if __name__ == "__main__":
    test_pagination()
