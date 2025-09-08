#!/usr/bin/env python3
"""Debug script to analyze Grind75 website structure."""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_grind75():
    """Analyze the Grind75 website structure."""
    
    url = "https://www.techinterviewhandbook.org/grind75/"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    })
    
    try:
        response = session.get(url)
        response.raise_for_status()
        
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for problem-related elements
        print("\n=== Looking for problem elements ===")
        
        # Check for common patterns
        patterns_to_check = [
            "problem",
            "leetcode",
            "difficulty",
            "title",
            "question",
            "card",
            "item",
            "row"
        ]
        
        for pattern in patterns_to_check:
            # Check by class
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            if elements:
                print(f"Found {len(elements)} elements with class containing '{pattern}'")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  {i+1}: {elem.name} class='{elem.get('class')}' text='{elem.get_text()[:50]}...'")
            
            # Check by data attributes
            elements = soup.find_all(attrs={f"data-{pattern}": True})
            if elements:
                print(f"Found {len(elements)} elements with data-{pattern} attribute")
        
        # Look for tables
        tables = soup.find_all("table")
        print(f"\nFound {len(tables)} tables")
        for i, table in enumerate(tables):
            print(f"  Table {i+1}: {len(table.find_all('tr'))} rows")
        
        # Look for lists
        lists = soup.find_all(["ul", "ol"])
        print(f"\nFound {len(lists)} lists")
        for i, lst in enumerate(lists):
            items = lst.find_all("li")
            print(f"  List {i+1}: {len(items)} items")
            if items:
                print(f"    First item: {items[0].get_text()[:100]}...")
        
        # Look for script tags that might contain data
        print("\n=== Looking for data in script tags ===")
        scripts = soup.find_all("script")
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                # Look for problem-related data
                if any(keyword in content.lower() for keyword in ["problem", "leetcode", "difficulty"]):
                    print(f"Script {i+1} contains problem-related data")
                    print(f"  Length: {len(content)}")
                    # Try to find JSON data
                    json_matches = re.findall(r'\{[^}]*"problem"[^}]*\}', content)
                    if json_matches:
                        print(f"  Found {len(json_matches)} JSON-like problem objects")
                        print(f"  Sample: {json_matches[0][:200]}...")
        
        # Look for Next.js data
        print("\n=== Looking for Next.js data ===")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data and next_data.string:
            try:
                data = json.loads(next_data.string)
                print("Found __NEXT_DATA__")
                print(f"Keys: {list(data.keys())}")
                
                # Navigate through the data structure
                if "props" in data:
                    print(f"Props keys: {list(data['props'].keys())}")
                    if "pageProps" in data["props"]:
                        page_props = data["props"]["pageProps"]
                        print(f"PageProps keys: {list(page_props.keys())}")
                        
                        # Look for problem data
                        for key, value in page_props.items():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"  {key}: list with {len(value)} items")
                                if isinstance(value[0], dict):
                                    print(f"    Sample keys: {list(value[0].keys())}")
                            elif isinstance(value, dict):
                                print(f"  {key}: dict with keys {list(value.keys())}")
                        
            except json.JSONDecodeError:
                print("Failed to parse __NEXT_DATA__ as JSON")
        
        # Save full HTML for manual inspection
        with open("/tmp/grind75.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\nSaved full HTML to /tmp/grind75.html")
        
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")

if __name__ == "__main__":
    analyze_grind75()