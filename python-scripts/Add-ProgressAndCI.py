#!/usr/bin/env python3
"""
Creates PROGRESS.md (a definition-of-done checklist plus a day-by-day
tracker) and .github/workflows/bicep-build.yml (a GitHub Actions check
that lints and builds every .bicep file on push/PR).

The CI workflow needs no Azure login and no secrets - az bicep lint/build
are purely local operations against ubuntu-latest's pre-installed Azure
CLI, they never talk to your actual subscription. It just proves every
.bicep file in the repo is syntactically valid.

Assumes it lives one folder below the repo root, same as the other
scripts in python-scripts/.
"""

from pathlib import Path

base_path = Path(__file__).resolve().parent.parent

progress = """# Progress Tracker

## Definition of Done
This build counts as AZ-104-ready when every one of these is actually true,
not just "mostly true":

- [ ] All 30 `lab.md` files have Steps Taken, Verification, Issues & Fixes,
      and Key Takeaways filled in - not just the Objective section
- [ ] All 30 `solution.bicep` files contain real, working code that passes
      `az deployment group validate`
- [ ] `COST-LOG.md` has an entry for every session, running total known
- [ ] `TROUBLESHOOTING.md` has real entries - a completely empty log by
      Week 6 more likely means issues went undocumented, not that none
      happened
- [ ] A practice exam score consistently landing above ~80%
- [ ] The exam is actually booked, with a date on the calendar

## Day-by-Day

### Week 1-2: Compute & Governance / App Hosting
- [ ] Day 00 - Bicep Fundamentals (read only, no lab)
- [ ] Day 01 - RBAC and Management Groups
- [ ] Day 02 - Azure Policy
- [ ] Day 03 - Resource Locks and Budgets
- [ ] Day 04 - VMs and Availability Zones
- [ ] Day 05 - VM Scale Sets
- [ ] Day 06 - Managed Disks and VM Extensions
- [ ] Day 07 - App Service
- [ ] Day 08 - Azure Container Apps
- [ ] Day 09 - Bicep Consolidation Pass
- [ ] Day 10 - Self-Test and Teardown

### Week 3: Networking
- [ ] Day 11 - VNet, Subnets, and NSGs
- [ ] Day 12 - VNet Peering and Private DNS
- [ ] Day 13 - Load Balancer and Application Gateway
- [ ] Day 14 - Azure Bastion and VPN Gateway
- [ ] Day 15 - Network Watcher and Week Review

### Week 4: Storage
- [ ] Day 16 - Storage Accounts and Redundancy
- [ ] Day 17 - Blob Storage and Lifecycle Management
- [ ] Day 18 - Azure Files
- [ ] Day 19 - SAS Tokens and Private Endpoints
- [ ] Day 20 - Storage Week Review and Teardown

### Week 5: Identity & Access
- [ ] Day 21 - Entra ID Users and Groups
- [ ] Day 22 - RBAC vs Entra Roles
- [ ] Day 23 - Conditional Access and SSPR
- [ ] Day 24 - Hybrid Identity
- [ ] Day 25 - Identity Week Self-Test

### Week 6: Monitoring & Backup
- [ ] Day 26 - Log Analytics and Diagnostic Settings
- [ ] Day 27 - Alert Rules and Action Groups
- [ ] Day 28 - Azure Backup
- [ ] Day 29 - Update Management and Azure Arc
- [ ] Day 30 - Final Self-Test and Full Teardown

### Week 7-8: Review & Exam
- [ ] Practice exam #1 taken - score: ____
- [ ] Weak domains identified and reviewed
- [ ] Practice exam #2 taken - score: ____
- [ ] Exam booked - date: ____
- [ ] Exam passed
"""

ci_workflow = """name: Bicep Build Check

on:
  push:
    paths:
      - '**/*.bicep'
  pull_request:
    paths:
      - '**/*.bicep'

jobs:
  build:
    name: Lint and Build Bicep Files
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Bicep CLI
        run: |
          az bicep install
          az bicep version

      - name: Lint every .bicep file
        run: |
          find . -name "*.bicep" | while read -r file; do
            echo "Linting: $file"
            az bicep lint --file "$file" || exit 1
          done

      - name: Build every .bicep file
        run: |
          find . -name "*.bicep" | while read -r file; do
            echo "Building: $file"
            az bicep build --file "$file" --stdout > /dev/null || exit 1
          done
"""

progress_file = base_path / "PROGRESS.md"
if progress_file.exists():
    print("PROGRESS.md already exists - left it alone")
else:
    progress_file.write_text(progress, encoding="utf-8")
    print("PROGRESS.md created")

workflow_dir = base_path / ".github" / "workflows"
workflow_dir.mkdir(parents=True, exist_ok=True)
workflow_file = workflow_dir / "bicep-build.yml"
if workflow_file.exists():
    print(".github/workflows/bicep-build.yml already exists - left it alone")
else:
    workflow_file.write_text(ci_workflow, encoding="utf-8")
    print(".github/workflows/bicep-build.yml created")

# Point to PROGRESS.md from the root README
readme_file = base_path / "README.md"
if readme_file.exists():
    text = readme_file.read_text(encoding="utf-8")
    old_learning_tail = (
        "Also at the repo root: `GLOSSARY.md` for any term you hit that isn't\n"
        "explained inline, `COST-LOG.md` to track real spend session by session,\n"
        "and `TROUBLESHOOTING.md` to log real errors and what fixed them."
    )
    new_learning_tail = (
        "Also at the repo root: `GLOSSARY.md` for any term you hit that isn't\n"
        "explained inline, `COST-LOG.md` to track real spend session by session,\n"
        "`TROUBLESHOOTING.md` to log real errors and what fixed them, and\n"
        "`PROGRESS.md` for the day-by-day checklist and the definition of done\n"
        "for the whole build."
    )
    if old_learning_tail in text and "PROGRESS.md" not in text:
        text = text.replace(old_learning_tail, new_learning_tail)
        readme_file.write_text(text, encoding="utf-8")
        print("Root README updated to link PROGRESS.md")
    elif "PROGRESS.md" in text:
        print("README already links PROGRESS.md")

print()
print("Done.")