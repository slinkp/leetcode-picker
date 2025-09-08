#!/usr/bin/env python3
"""Test different approaches to get Grind75 data."""

import requests
import json
from bs4 import BeautifulSoup


def test_grind75_approaches():
    """Test different approaches to get Grind75 problem data."""

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    # Approach 1: Check if there's an API endpoint
    print("=== Approach 1: Look for API endpoints ===")
    api_urls = [
        "https://www.techinterviewhandbook.org/api/grind75",
        "https://www.techinterviewhandbook.org/api/problems",
        "https://www.techinterviewhandbook.org/_next/static/chunks/pages/grind75.js",
        "https://api.techinterviewhandbook.org/grind75",
    ]

    for url in api_urls:
        try:
            response = session.get(url)
            print(f"{url}: {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                print(f"  Content-Type: {content_type}")
                if "json" in content_type:
                    try:
                        data = response.json()
                        print(
                            f"  JSON keys: {list(data.keys()) if isinstance(data, dict) else 'List with ' + str(len(data)) + ' items'}"
                        )
                    except:
                        print("  Failed to parse JSON")
                else:
                    print(f"  Content length: {len(response.text)}")
        except Exception as e:
            print(f"{url}: Error - {e}")

    # Approach 2: Use a known list of Grind75 problems
    print("\n=== Approach 2: Use known Grind75 problem list ===")

    # This is the canonical Grind75 list that I can hardcode
    grind75_problems = [
        {"title": "Two Sum", "difficulty": "Easy"},
        {"title": "Valid Parentheses", "difficulty": "Easy"},
        {"title": "Merge Two Sorted Lists", "difficulty": "Easy"},
        {"title": "Best Time to Buy and Sell Stock", "difficulty": "Easy"},
        {"title": "Valid Palindrome", "difficulty": "Easy"},
        {"title": "Invert Binary Tree", "difficulty": "Easy"},
        {"title": "Valid Anagram", "difficulty": "Easy"},
        {"title": "Binary Search", "difficulty": "Easy"},
        {"title": "Flood Fill", "difficulty": "Easy"},
        {"title": "Maximum Subarray", "difficulty": "Medium"},
        {"title": "Insert Interval", "difficulty": "Medium"},
        {"title": "01 Matrix", "difficulty": "Medium"},
        {"title": "K Closest Points to Origin", "difficulty": "Medium"},
        {
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "Medium",
        },
        {"title": "3Sum", "difficulty": "Medium"},
        {"title": "Binary Tree Level Order Traversal", "difficulty": "Medium"},
        {"title": "Clone Graph", "difficulty": "Medium"},
        {"title": "Course Schedule", "difficulty": "Medium"},
        {"title": "Implement Trie (Prefix Tree)", "difficulty": "Medium"},
        {"title": "Coin Change", "difficulty": "Medium"},
        {"title": "Product of Array Except Self", "difficulty": "Medium"},
        {"title": "Validate Binary Search Tree", "difficulty": "Medium"},
        {"title": "Number of Islands", "difficulty": "Medium"},
        {"title": "Rotting Oranges", "difficulty": "Medium"},
        {"title": "Search in Rotated Sorted Array", "difficulty": "Medium"},
        {"title": "Combination Sum", "difficulty": "Medium"},
        {"title": "Permutations", "difficulty": "Medium"},
        {"title": "Merge Intervals", "difficulty": "Medium"},
        {"title": "Lowest Common Ancestor of a Binary Tree", "difficulty": "Medium"},
        {"title": "Time Based Key-Value Store", "difficulty": "Medium"},
        {"title": "Accounts Merge", "difficulty": "Medium"},
        {"title": "Sort Colors", "difficulty": "Medium"},
        {"title": "Word Break", "difficulty": "Medium"},
        {"title": "Partition Equal Subset Sum", "difficulty": "Medium"},
        {"title": "String to Integer (atoi)", "difficulty": "Medium"},
        {"title": "Spiral Matrix", "difficulty": "Medium"},
        {"title": "Subsets", "difficulty": "Medium"},
        {"title": "Binary Tree Right Side View", "difficulty": "Medium"},
        {"title": "Longest Palindromic Substring", "difficulty": "Medium"},
        {"title": "Unique Paths", "difficulty": "Medium"},
        {
            "title": "Construct Binary Tree from Preorder and Inorder Traversal",
            "difficulty": "Medium",
        },
        {"title": "Container With Most Water", "difficulty": "Medium"},
        {"title": "Letter Combinations of a Phone Number", "difficulty": "Medium"},
        {"title": "Word Search", "difficulty": "Medium"},
        {"title": "Find All Anagrams in a String", "difficulty": "Medium"},
        {"title": "Minimum Height Trees", "difficulty": "Medium"},
        {"title": "Task Scheduler", "difficulty": "Hard"},
        {"title": "LRU Cache", "difficulty": "Medium"},
        {"title": "Kth Smallest Element in a BST", "difficulty": "Medium"},
        {"title": "Minimum Window Substring", "difficulty": "Hard"},
        {"title": "Serialize and Deserialize Binary Tree", "difficulty": "Hard"},
        {"title": "Trapping Rain Water", "difficulty": "Hard"},
        {"title": "Find Median from Data Stream", "difficulty": "Hard"},
        {"title": "Word Ladder", "difficulty": "Hard"},
        {"title": "Basic Calculator", "difficulty": "Hard"},
        {"title": "Maximum Profit in Job Scheduling", "difficulty": "Hard"},
        {"title": "Merge k Sorted Lists", "difficulty": "Hard"},
        {"title": "Largest Rectangle in Histogram", "difficulty": "Hard"},
    ]

    print(f"Hardcoded Grind75 list has {len(grind75_problems)} problems")

    # Convert titles to likely LeetCode URLs
    def title_to_leetcode_url(title):
        """Convert problem title to likely LeetCode URL."""
        # Remove special characters and convert to kebab-case
        slug = title.lower()
        slug = slug.replace("(", "").replace(")", "").replace(",", "")
        slug = slug.replace(" - ", "-").replace(" ", "-")
        slug = slug.replace("--", "-")
        return f"https://leetcode.com/problems/{slug}/"

    print("\nSample URLs:")
    for problem in grind75_problems[:5]:
        url = title_to_leetcode_url(problem["title"])
        print(f"  {problem['title']} -> {url}")

    return grind75_problems


if __name__ == "__main__":
    test_grind75_approaches()
