#!/usr/bin/env python3
"""
Restructures Azure-Platform-Foundation from the bicep/docs/lessons split
into one subfolder per study day, and makes every source link clickable.

Run this ONCE, from inside the repo, after the original scaffold script.
Safe to run on a repo where you haven't added your own content yet - it
moves the generated lesson/lab content into the new layout and deletes the
old empty folders behind it. It does not touch anything you've written
yourself in files it doesn't recognize.

Before:
    01-compute-governance/
        bicep/            (empty, .gitkeep)
        docs/day-01-....md
        lessons/day-01-....md

After:
    01-compute-governance/
        day-01-rbac-and-management-groups/
            lesson.md       <- the teaching content
            lab.md          <- your portal + delivery write-up
            solution.bicep  <- your actual Bicep code goes here
"""

from pathlib import Path
import re

base_path = Path(__file__).resolve().parent

phase_folders = [
    "01-compute-governance",
    "01b-app-hosting",
    "02-networking",
    "03-storage",
    "04-identity-access",
    "05-monitoring-backup",
]


def linkify_bare_urls(text: str) -> str:
    """Wrap bare URLs in < > so they render as clickable links in any
    markdown viewer, instead of sitting as plain unclickable text."""
    return re.sub(r'(?<!<)(https?://[^\s<>\)]+)(?!>)', r'<\1>', text)


def linkify_titled_line(match: re.Match) -> str:
    title, url = match.group(1), match.group(2)
    return f'- [{title}]({url})'


restructured = 0
for phase in phase_folders:
    phase_path = base_path / phase
    lessons_dir = phase_path / "lessons"
    docs_dir = phase_path / "docs"
    bicep_dir = phase_path / "bicep"

    if not lessons_dir.exists():
        print(f"Skipping {phase} - no lessons folder found, already restructured?")
        continue

    for lesson_file in sorted(lessons_dir.glob("day-*.md")):
        slug = lesson_file.stem
        day_folder = phase_path / slug
        day_folder.mkdir(parents=True, exist_ok=True)

        lesson_text = linkify_bare_urls(lesson_file.read_text(encoding="utf-8"))
        (day_folder / "lesson.md").write_text(lesson_text, encoding="utf-8")
        lesson_file.unlink()

        matching_doc = docs_dir / lesson_file.name
        if matching_doc.exists():
            lab_text = linkify_bare_urls(matching_doc.read_text(encoding="utf-8"))
            (day_folder / "lab.md").write_text(lab_text, encoding="utf-8")
            matching_doc.unlink()

        solution_path = day_folder / "solution.bicep"
        if not solution_path.exists():
            solution_path.write_text(
                f"// {slug} - your Bicep code for this day goes here\n",
                encoding="utf-8",
            )
        restructured += 1

    # clean up the now-empty old folders
    for old in (lessons_dir, docs_dir, bicep_dir):
        if old.exists():
            for leftover in old.iterdir():
                leftover.unlink()
            old.rmdir()

    print(f"{phase}: restructured into per-day folders")

# Make bicep-study-resources.md links clickable too, and fix its stale
# reference to the old lessons/ folder structure
resources_file = base_path / "bicep-study-resources.md"
if resources_file.exists():
    text = resources_file.read_text(encoding="utf-8")
    text = text.replace(
        "Every lesson in this repo's lessons/ folders is built from these sources.",
        "Every lesson in this repo (in each day's lesson.md) is built from these sources.",
    )
    text = re.sub(r'^- (.+?) - (https?://\S+)$', linkify_titled_line, text, flags=re.MULTILINE)
    resources_file.write_text(text, encoding="utf-8")
    print("bicep-study-resources.md links made clickable")

# Update the root README's structure description to match the new layout
readme_file = base_path / "README.md"
if readme_file.exists():
    text = readme_file.read_text(encoding="utf-8")
    old_section = """## How Each Phase Folder Is Organized

- **bicep/** - your actual Bicep code as you build each lab
- **docs/** - one lab write-up per day, using the template in /assets
- **lessons/** - one Bicep lesson per day, written before you build that
  day's lab. No prior coding background assumed."""
    new_section = """## How Each Phase Folder Is Organized

Each phase folder contains one subfolder per study day
(`day-01-rbac-and-management-groups/`, etc). Inside each day's folder:

- **lesson.md** - the Bicep lesson for that day, written before you build.
  No prior coding background assumed.
- **lab.md** - your portal steps, verification, and write-up for that day
- **solution.bicep** - your actual Bicep code for that day's build"""
    if old_section in text:
        text = text.replace(old_section, new_section)
        readme_file.write_text(text, encoding="utf-8")
        print("Root README updated to describe the new layout")

print()
print(f"Done - {restructured} day folders created across {len(phase_folders)} phases.")