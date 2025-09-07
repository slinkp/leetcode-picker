# Plan.md

A command line tool which will give me a random problem to work on and track my progress.
Let's use python 3.
The virtualenv is in `/Users/paul/src/leetcode-picker/.direnv/python-3.13`

The problem list can be kept in a simple file. CVS is fine.
Info to track:
- URL
- Title
- Last pass date in YYYY-MM-DD format
- Number of completions (passing submissions)
- Number of submissions
- Difficulty level
- Study plan URL
- Overridden difficulty level


First, compile a master list from these 2 study plan URLs:
https://leetcode.com/studyplan/leetcode-75/
https://leetcode.com/studyplan/top-interview-150/

Track problems from this list as well (optional because I'm not intending to complete this list, I'm just curious):
https://www.techinterviewhandbook.org/grind75/


(Those two are tracked for me automatically on leetcode, BUT i don't like picking problems from there because it shows me the categories - which is a big spoiler - as well as the difficulty level.)

Next, use my leetcode login to see which problems I've done.
I don't care how you do this. Leetcode uses my github account via oauth
One way is to visit the URL of each problem and append `/submissions`, eg
`https://leetcode.com/problems/kth-smallest-element-in-a-bst/submissions/`
Another would be to go through my history and navigate from there: https://leetcode.com/progress/


## CLI interface

Need commands for the following:

- Choose problem: Choose a new random unsolved problem (optional difficulty level; optional study plan name or URL, by default only choose from leetcode-75 and top-interview-150)
When filtering by difficulty level, use the overridden difficulty level if it exists, otherwise use the difficulty level from the master list.

- Review: same, but choose a problem I've completed before.  Additional option: "choose problems solved at least N weeks ago"

- Override difficulty: For a given problem, specify a difficulty level override for a problem where I disagree with the difficulty level (leetcode is terrible at this)

- Show progress (count and percent complete on each study plan)

- Mark (URL) as completed with date


### Less important side quest

Ideally marking complete would also mark problems complete on grind75 if the problem appears there; the challenge is that appears to only be stored in my firefox browser state, possibly in local storage, and i cleared all of it recently.
There don't appear to be anchors for these elements, although there are aria labels based on the problem title
eg 

```js
<button aria-label="Mark Valid Anagram as complete" class="inline-flex items-center border border-transparent p-0 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-1 text-gray-300  hover:text-gray-400 focus:ring-gray-300" type="button"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" class="h-8 w-8"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></button>
```

Since there's only 75 there I'd be OK with marking them manually if you can give me a list of completed problem titles in the same order as grind75, unless you can suggest an easy way to automate it






