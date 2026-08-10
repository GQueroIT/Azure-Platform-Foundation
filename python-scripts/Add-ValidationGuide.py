#!/usr/bin/env python3
"""
Adds assets/validation-guide.md (explains az bicep build / validate /
what-if for someone who's never used them) and updates the root README to
document the actual daily loop, including that validation step, and to
point at the business context additions.

Assumes it lives one folder below the repo root, same as the other
scripts in python-scripts/.
"""

from pathlib import Path

base_path = Path(__file__).resolve().parent.parent

validation_guide = """# Validating a Bicep Deployment Before You Run It

You said you wouldn't know to do this without being told, so here's the
full explanation, not just the command.

## The Problem This Solves
Right now, your only way to know if a Bicep file is correct is to deploy
it and see what happens. That's slow, and on a bad day it means deploying
something broken, paying for it while it exists, then tearing it down and
starting over. Validation catches most mistakes in seconds, before
anything is actually created in Azure.

## Two Different Commands, Two Different Jobs

### 1. `az bicep build` - "Is this file even valid syntax?"
```bash
az bicep build --file main.bicep
```
This compiles your Bicep into an ARM JSON file and fails loudly if there's
a syntax error - a missing bracket, a typo in a property name, a resource
type that doesn't exist. It does NOT check Azure at all. It's the fastest
possible check, and it's free, so there's no reason not to run it every
time you save a file.

### 2. `az deployment group validate` - "Would Azure actually accept this?"
```bash
az deployment group validate \\
  --resource-group your-rg-name \\
  --template-file main.bicep
```
This goes further than `bicep build` - it actually sends your template to
Azure Resource Manager and asks "if I deployed this right now, would it
succeed?" It catches things a syntax check can't: a VM size that isn't
available in your region, a name that's already taken, a parameter that's
missing. It still creates nothing. It's a dry run against the real API.

### 3. `az deployment group what-if` - "What would actually change?"
```bash
az deployment group what-if \\
  --resource-group your-rg-name \\
  --template-file main.bicep
```
This is the most useful one once you're editing something that already
exists. It shows you a diff: what would be created, what would be
modified, what would be deleted, before any of it happens. If you expect
it to say "1 resource created" and it says "1 resource created, 3
resources deleted," that's your warning, not a surprise after the fact.

## Reading the Output
- `validate` gives you either a clean success, or an error object with a
  `code` and a `message`. The `message` almost always tells you exactly
  what's wrong - read it fully before assuming you need to search for the
  error online.
- `what-if` color-codes its output: green for create, orange for modify,
  red for delete. If you see red and didn't expect it, stop and figure
  out why before deploying.

## Where This Fits In Your Daily Loop
Add this between "translate to Bicep" and "deploy" - see the root
README's Daily Loop section.

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-cli>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/deploy-what-if>
"""

assets_path = base_path / "assets"
assets_path.mkdir(parents=True, exist_ok=True)
(assets_path / "validation-guide.md").write_text(validation_guide, encoding="utf-8")
print("assets/validation-guide.md created")

readme_file = base_path / "README.md"
if readme_file.exists():
    text = readme_file.read_text(encoding="utf-8")

    daily_loop_section = """
## Daily Loop

1. Read the lesson (`lesson.md`) for that day
2. Build it in the Azure Portal first
3. Translate it to Bicep (`solution.bicep`)
4. Validate before deploying - `az bicep build`, then
   `az deployment group validate`, then `az deployment group what-if`.
   See `assets/validation-guide.md` if you're not sure what these do or
   why they matter - short answer: they catch mistakes for free, before
   you pay for anything.
5. Deploy, and confirm it matches what `what-if` predicted
6. Verify it actually works the way the lesson said it should
7. Fill in `lab.md` - steps taken, verification, any issues you hit
8. Read the lesson's "Why This Matters" section and make sure you could
   explain it out loud, not just recite it
9. Commit and push - don't let work sit uncommitted past one session
10. Confirm nothing billable is left running before you close the laptop
"""

    old_learning = """## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from."""

    new_learning = """## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from, and `assets/validation-guide.md` for
how to check your Bicep before deploying it. Every lesson also ends with a
"Why This Matters" section tying that day's work to a real business
reason - it's worth reading even after you've built the lab."""

    if "## Daily Loop" not in text:
        text = text.replace(old_learning, daily_loop_section.strip() + "\n\n" + new_learning)
        readme_file.write_text(text, encoding="utf-8")
        print("Root README updated with Daily Loop section")
    else:
        print("README already has a Daily Loop section - left it alone")

print()
print("Done.")