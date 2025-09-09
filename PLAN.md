# Plan.md

A command line tool which will give me a random problem to work on and track my progress.
Let's use python 3.
The virtualenv is in `/Users/paul/src/leetcode-picker/.direnv/python-3.13`

## ✅ COMPLETED

The problem list can be kept in a simple file. CVS is fine.
Info to track:
- ✅ URL
- ✅ Title
- ✅ Last pass date in YYYY-MM-DD format
- ✅ Number of completions (passing submissions)
- ✅ Number of submissions
- ✅ Difficulty level
- ✅ Study plan URL
- ✅ Overridden difficulty level

✅ First, compile a master list from these 2 study plan URLs:
https://leetcode.com/studyplan/leetcode-75/
https://leetcode.com/studyplan/top-interview-150/

✅ Track problems from this list as well (optional because I'm not intending to complete this list, I'm just curious):
https://www.techinterviewhandbook.org/grind75/

(Those two are tracked for me automatically on leetcode, BUT i don't like picking problems from there because it shows me the categories - which is a big spoiler - as well as the difficulty level.)

## ✅ LeetCode Authentication and Sync

Implemented cookie-based authentication (setup via `leetcode-picker auth`) and submission sync (`leetcode-picker sync`) using the LeetCode GraphQL API. Synced submission data is merged into the local CSV and reflected in progress and checklist views.

## ✅ CLI interface - COMPLETED

Need commands for the following:

- ✅ Choose problem: Choose a new random unsolved problem (optional difficulty level; optional study plan name or URL, by default only choose from leetcode-75 and top-interview-150)
When filtering by difficulty level, use the overridden difficulty level if it exists, otherwise use the difficulty level from the master list.

- ✅ Review: same, but choose a problem I've completed before.  Additional option: "choose problems solved at least N weeks ago"

- ✅ Override difficulty: For a given problem, specify a difficulty level override for a problem where I disagree with the difficulty level (leetcode is terrible at this)

- ✅ Show progress (count and percent complete on each study plan)
- ✅ Verbose progress checklist: `progress -v [study_plan]` prints ordered checklists with completion marks
- ✅ Grind75 checklist: `grind75-completed` shows all Grind75 problems in order with completion marks

- ✅ Mark (URL) as completed with date

## ✅ IMPLEMENTATION STATUS

**FULLY FUNCTIONAL CLI TOOL COMPLETED:**
- ✅ 209 problems scraped from LeetCode 75 and Top Interview 150
- ✅ CSV storage at `~/.leetcode-picker/problems.csv`
- ✅ Global CLI command `leetcode-picker` installed
- ✅ All requested commands working: choose, review, override-difficulty, progress, mark-complete
- ✅ Difficulty and study plan filtering
- ✅ Progress tracking with percentages
- ✅ Clean code passing all linters (Black, Flake8, MyPy)

### TODO: Less important side quest

Ideally marking complete would also mark problems complete on grind75 if the problem appears there; the challenge is that appears to only be stored in my firefox browser state, possibly in local storage, and i cleared all of it recently.
There don't appear to be anchors for these elements, although there are aria labels based on the problem title
eg 

```js
<button aria-label="Mark Valid Anagram as complete" class="inline-flex items-center border border-transparent p-0 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-1 text-gray-300  hover:text-gray-400 focus:ring-gray-300" type="button"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" class="h-8 w-8"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></button>
```

Current workaround: use `leetcode-picker grind75-completed` to print the Grind75 checklist with checkmarks and URLs for manual marking. Full automation is still TBD.






