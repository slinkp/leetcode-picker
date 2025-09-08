#!/usr/bin/env python3
"""Main CLI entry point for leetcode-picker."""

import argparse
import sys

from .commands import (
    choose_problem,
    mark_complete,
    override_difficulty,
    review_problem,
    setup_auth,
    show_progress,
)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="leetcode-picker",
        description="A CLI tool for picking random LeetCode problems and tracking progress",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Choose command
    choose_parser = subparsers.add_parser("choose", help="Pick a random unsolved problem")
    choose_parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty level",
    )
    choose_parser.add_argument(
        "--study-plan",
        help="Filter by study plan (leetcode-75, top-interview-150)",
    )

    # Review command
    review_parser = subparsers.add_parser(
        "review", help="Pick a random previously solved problem"
    )
    review_parser.add_argument(
        "--weeks-ago",
        type=int,
        help="Only show problems solved at least N weeks ago",
    )
    review_parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty level",
    )

    # Override difficulty command
    override_parser = subparsers.add_parser(
        "override-difficulty", help="Override difficulty level for a problem"
    )
    override_parser.add_argument("url", help="Problem URL")
    override_parser.add_argument(
        "difficulty",
        choices=["easy", "medium", "hard"],
        help="New difficulty level",
    )

    # Progress command
    subparsers.add_parser("progress", help="Show progress on study plans")

    # Mark complete command
    mark_parser = subparsers.add_parser(
        "mark-complete", help="Mark a problem as completed"
    )
    mark_parser.add_argument("url", help="Problem URL")
    mark_parser.add_argument(
        "--date", help="Completion date (YYYY-MM-DD, default: today)"
    )

    # Auth setup command
    subparsers.add_parser("auth", help="Set up LeetCode authentication")

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "choose":
            choose_problem(args.difficulty, args.study_plan)
        elif args.command == "review":
            review_problem(args.weeks_ago, args.difficulty)
        elif args.command == "override-difficulty":
            override_difficulty(args.url, args.difficulty)
        elif args.command == "progress":
            show_progress()
        elif args.command == "mark-complete":
            mark_complete(args.url, args.date)
        elif args.command == "auth":
            setup_auth()
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
