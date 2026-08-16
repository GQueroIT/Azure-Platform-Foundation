#!/usr/bin/env python3
"""
Azure-Platform-Foundation - Update Workflow to Phase-Batched

Replaces the README's "## Daily Loop" section (build one day, portal then
Bicep, same session) with a "## Workflow: Phase-Batched" section: build
every day in a phase through the Portal first, tear the whole phase down,
then do the Bicep pass for the whole phase against a clean resource group,
tear down again, move to the next phase.

Day 14 (Bastion + VPN Gateway) stays an exception either way - it comes
down the same day it's built, regardless of where the rest of the phase's
Portal pass stands.

This does NOT touch Terraform, and deliberately says nothing about it -
Terraform stays its own project after AZ-104, per the original repo scope
(see New-AzurePlatformFoundationScaffold.py's docstring). Folding a third
pass into this repo would reopen that decision for no benefit to the AZ-104
timeline this repo exists to serve.

Safe to re-run: skipped if the new section is already present.

Run from anywhere; resolves the repo root from this script's own location
(python-scripts/, one level below repo root).
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if not (REPO_ROOT / "README.md").exists():
    print(f"ERROR: expected repo root at {REPO_ROOT} but no README.md found there.")
    print("This script must live in python-scripts/, one level below the repo root.")
    sys.exit(1)

OLD_DAILY_LOOP = """## Daily Loop

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
10. Confirm nothing billable is left running before you close the laptop"""

NEW_WORKFLOW = """## Workflow: Phase-Batched (Portal First, Then Bicep)

This project runs phase by phase, not strictly day by day. Within a
phase (e.g. `01-compute-governance`, Days 00-06), every day gets built in
the Portal first, in order. Only once the whole phase is Portal-complete
does the Bicep pass for that phase begin - also day by day, in order,
against a freshly torn-down resource group, not a redeploy over what's
still sitting there from the Portal pass.

**Why Portal comes first, and comes first for the whole phase:** AZ-104
is primarily a Portal/CLI/PowerShell administration exam - it does not
test writing Bicep. The Portal pass, done well, is the part directly
responsible for passing. The Bicep pass is real and valuable for the
portfolio and the Cloud Engineer track this project feeds into, but it's
reinforcement - a second encounter with the same material, which is a
legitimate way to deepen recall, not the primary exam-prep vehicle. If
time ever gets tight before the exam date, the Portal pass and the
weekend PowerShell/Python practice are what to protect first - a phase's
Bicep pass slipping doesn't hurt exam readiness the way skipping or
rushing the Portal pass would.

### Portal Pass (per phase)

1. Skim every day's `lesson.md` "Core Concepts" section for the whole
   phase before building anything - gives you the map before you start
   clicking.
2. Build each day's lab in the Portal, in order.
3. Fill in that day's `lab.md` "Steps Taken (Portal)" section thoroughly,
   with screenshots, as you go - not after. Once the Bicep pass for this
   phase starts, the Portal resource may no longer exist, and this
   write-up becomes your only reference, not a nice-to-have.
4. Where it applies, query what you just built with PowerShell
   (`Get-Az*` cmdlets) or the CLI - this maps directly to what AZ-104
   actually tests, more directly than the Bicep pass does.
5. **Exception: Day 14 (Bastion + VPN Gateway).** These bill hourly with
   no pause option and are the most expensive resources in the entire
   build. They come down the same day they're built, regardless of where
   the rest of the phase's Portal pass stands - don't let them ride out
   the rest of the phase.
6. Once every day in the phase is built and documented, self-test: can
   you explain each resource's purpose out loud, without notes.
7. Tear down every resource group from the phase. Confirm $0 running and
   log it in `COST-LOG.md` before starting the Bicep pass.

### Bicep Pass (per phase, after the Portal pass is fully torn down)

1. Starting from a clean resource group, write each day's
   `solution.bicep` in order, working from that day's `lesson.md`
   (Annotated Example) and your own `lab.md` write-up from the Portal
   pass - not from a live resource, since it's gone.
2. Validate before deploying, every time - `az bicep build`, then
   `az deployment group validate`, then `az deployment group what-if`.
   See `assets/validation-guide.md` if you're not sure what these do or
   why they matter - short answer: they catch mistakes for free, before
   you pay for anything.
3. Deploy, and confirm it matches what `what-if` predicted.
4. Verify it actually works the way the lesson said it should.
5. Update `lab.md`'s Bicep Translation, Verification, and Issues & Fixes
   sections.
6. Commit and push - don't let a phase's Bicep work sit uncommitted.
7. Tear the phase down again once it's fully deployed clean, documented,
   and committed.
8. Move to the next phase's Portal pass."""

MARKER = "## Workflow: Phase-Batched (Portal First, Then Bicep)"


def main():
    readme_path = REPO_ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")

    if MARKER in text:
        print("SKIP: README.md already has the phase-batched workflow section")
        return

    if OLD_DAILY_LOOP not in text:
        print("ERROR: could not find the expected '## Daily Loop' section in README.md.")
        print("The README may have been edited since this script was written.")
        print("No changes made - update the OLD_DAILY_LOOP text in this script to match")
        print("your current README, or edit README.md by hand instead.")
        sys.exit(1)

    text = text.replace(OLD_DAILY_LOOP, NEW_WORKFLOW)
    readme_path.write_text(text, encoding="utf-8")
    print("UPDATED: README.md - Daily Loop replaced with phase-batched workflow")


if __name__ == "__main__":
    main()