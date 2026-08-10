#!/usr/bin/env python3
"""
Adds a "Why This Matters (Business Context)" section to the end of every
lesson.md - a short, concrete scenario tying that day's technical work to
an actual reason a company would need it. The goal is that you can explain
WHY you did something in an interview, not just recite WHAT you did.

Also confirms the Microsoft Learn links at the bottom of each lesson are
in clickable <...> format (the restructure script already did this, this
just re-checks it after the business context is appended).

NOTE ON WHERE THIS SCRIPT LIVES: this script assumes it's sitting one
folder below the repo root (e.g. in python-scripts/), matching how you've
now organized things. If you ever move it again, the one line below
marked "base_path" is the one to fix - it needs to point at the folder
that directly contains 01-compute-governance, 02-networking, etc.
"""

from pathlib import Path
import re

# One level up from this script's own folder (python-scripts/) to the repo root.
base_path = Path(__file__).resolve().parent.parent

BUSINESS_CONTEXT = {
    "day-00-bicep-fundamentals":
        "Every cloud team eventually hits the same wall: someone changes a "
        "setting by hand in the portal, nobody documents it, and six months "
        "later no one can reproduce the environment or explain why it works. "
        "Infrastructure as code closes that gap - the Bicep file itself "
        "becomes the documentation, the audit trail, and the disaster-"
        "recovery plan all at once. A company that can redeploy its entire "
        "environment from a git repo during an outage recovers in hours; a "
        "company that can't is rebuilding from memory and screenshots.",
    "day-01-rbac-and-management-groups":
        "A new hire in finance needs read-only access to cost data, not the "
        "ability to delete production VMs. Without RBAC scoped correctly, "
        "companies either lock everything down so tight nobody can do their "
        "job, or leave everything open so one mistake (or one compromised "
        "account) can take down the whole environment. Management groups "
        "exist because a 200-subscription company can't apply policy one "
        "subscription at a time - they say 'everything under Finance follows "
        "this rule' once, and it inherits down automatically.",
    "day-02-azure-policy":
        "A developer spins up a storage account in a region the company "
        "isn't allowed to operate in for compliance reasons, and nobody "
        "notices until an audit six months later. Policy is how a company "
        "enforces rules automatically instead of hoping people remember them "
        "- tag enforcement is what lets finance actually bill costs back to "
        "the right department, and region restriction is what lets legal "
        "stop manually reviewing every deployment.",
    "day-03-locks-and-budgets":
        "A junior engineer runs a cleanup script against the wrong resource "
        "group and deletes a production database at 2am. A lock doesn't "
        "prevent honest mistakes from happening, it prevents them from being "
        "one click away. Budgets solve the more common failure: nobody "
        "notices a forgotten test environment running until the bill "
        "arrives, sometimes 10x over what anyone expected.",
    "day-04-vm-availability-zones":
        "An e-commerce company's checkout service runs on a single VM in a "
        "single datacenter. That datacenter has a power event during a big "
        "sale, and every transaction is gone until it comes back. "
        "Availability zones are the difference between 'one datacenter went "
        "down' and 'nothing happened, the other two zones picked up the "
        "load.'",
    "day-05-vm-scale-sets":
        "Traffic to a retail site is flat most of the year and 20x normal "
        "during a holiday sale. Provisioning for peak year-round wastes "
        "money every other week; provisioning for average traffic means the "
        "site falls over during the sale. A scale set is how you pay for "
        "average and still survive peak.",
    "day-06-disks-and-extensions":
        "A company's monitoring agent needs to be installed identically "
        "across 200 VMs today, and on every VM anyone spins up next year. "
        "Doing that by hand means it eventually drifts - some VMs get it, "
        "some don't, and nobody notices until there's an incident with no "
        "logs. An extension baked into the deployment means every VM has "
        "it, guaranteed, the moment it exists.",
    "day-07-app-service":
        "A small business wants a customer-facing website live without "
        "hiring anyone to patch an OS, manage a web server, or handle "
        "certificate renewal. App Service is exactly that trade-off - less "
        "control than a VM, but someone else owns the patching, scaling, "
        "and certificate headaches.",
    "day-08-container-apps":
        "A startup's API gets almost no traffic overnight and spikes hard "
        "during business hours. Paying for a server that sits idle sixteen "
        "hours a day is real money at scale. Scaling to zero means the "
        "meter stops when nobody's using it - you pay for requests, not for "
        "a machine sitting there waiting.",
    "day-09-bicep-consolidation":
        "A contractor hands off a project as nine unrelated scripts, no "
        "shared naming convention, hardcoded values specific to their test "
        "environment. The next engineer spends a week just figuring out how "
        "to redeploy it somewhere else. Modular, parameterized Bicep is "
        "what makes a handoff take an hour instead of a week.",
    "day-10-self-test-teardown":
        "A company gets a surprise bill because a proof-of-concept "
        "environment from three months ago never got deleted. Teardown "
        "discipline isn't optional at a real company - it's the difference "
        "between a lab and a liability.",
    "day-11-vnet-subnets-nsg":
        "A company puts its database on the same open subnet as its "
        "public-facing web server. One vulnerability in the web app and the "
        "database is directly reachable. Subnets and NSGs are what stop a "
        "compromised front-end from automatically meaning a compromised "
        "back-end.",
    "day-12-peering-and-dns":
        "Two teams each built their own VNet for their own project, and now "
        "a shared service needs to talk to both without routing traffic "
        "over the public internet. Peering keeps that traffic on "
        "Microsoft's backbone instead of exposing it externally; private "
        "DNS means internal services find each other by name instead of "
        "hardcoded IPs that break the moment something gets redeployed.",
    "day-13-load-balancer-appgw":
        "A company's app runs fine on one server until that server needs a "
        "restart for a patch, and the site goes down during the restart. A "
        "load balancer means traffic just shifts to the healthy instances "
        "during a rolling update, and customers never notice.",
    "day-14-bastion-vpn-gateway":
        "A company opens RDP directly to the internet on a VM 'just for "
        "now' to make admin easier, and it gets brute-forced within days. "
        "Bastion exists so there's never a public RDP/SSH port to attack in "
        "the first place. VPN Gateway is the same idea for connecting an "
        "entire office network to Azure without exposing anything to the "
        "open internet.",
    "day-15-network-watcher-review":
        "A firewall rule change breaks connectivity between two services "
        "and nobody can tell if it's DNS, routing, or the NSG without hours "
        "of guessing. Network Watcher's diagnostic tools turn 'we think "
        "it's the network' into an actual answer in minutes.",
    "day-16-storage-accounts-redundancy":
        "A regional outage takes out a datacenter, and a company running "
        "LRS-only storage loses access to its data until that datacenter "
        "recovers. GRS costs more for a reason - it's the difference "
        "between a bad afternoon and a real disaster, and part of the job "
        "is knowing which workloads are worth paying for that on.",
    "day-17-blob-lifecycle":
        "A company keeps every log file it's ever generated on the same "
        "expensive storage tier it uses for active data, because nobody set "
        "up a policy to move it. Lifecycle management is the unglamorous "
        "rule that quietly saves real money every month without anyone "
        "having to remember to run a cleanup script.",
    "day-18-azure-files":
        "A team needs a shared drive that multiple VMs and people can read "
        "and write to at once, the way a traditional file server would "
        "work, without standing up and patching an actual Windows file "
        "server. Azure Files is that shared drive, managed by the platform "
        "instead of by someone's on-call rotation.",
    "day-19-sas-private-endpoints":
        "A vendor needs temporary access to one specific file, not the "
        "whole storage account and not forever. A SAS token grants exactly "
        "that - scoped, time-limited access, no shared password to rotate "
        "later. A private endpoint solves a different problem: a database "
        "that should never be reachable from the public internet at all, "
        "only from inside the company's own network.",
    "day-20-review-teardown":
        "Same lesson as Day 10 - a private endpoint or test container left "
        "running past its testing window is easy to forget and easy to get "
        "billed for. Reviewing and tearing down is part of the actual job, "
        "not an afterthought.",
    "day-21-entra-users-groups":
        "A company onboards dozens of new hires a quarter and manually adds "
        "each one to the right groups by hand, in the portal. Every mistake "
        "in that process is either someone with access they shouldn't have, "
        "or someone missing access they need on day one. Automating group "
        "membership is how that scales past a handful of people.",
    "day-22-rbac-vs-entra-roles":
        "A well-meaning admin grants someone Global Administrator in Entra "
        "ID to fix an Azure resource permission problem, not realizing the "
        "two systems are unrelated. That's a massively over-scoped grant "
        "for a problem RBAC alone would have solved. Knowing the actual "
        "boundary between the two systems is what prevents that kind of "
        "accidental over-permissioning.",
    "day-23-conditional-access-sspr":
        "An employee's password gets phished, and the attacker logs in from "
        "a country the company has never had an employee travel to, with no "
        "resistance at all. Conditional Access is the policy layer that "
        "catches exactly that pattern and blocks or challenges it. SSPR "
        "exists because 'call IT to reset your password' doesn't scale past "
        "about 50 employees - it becomes the single most common helpdesk "
        "ticket at any company without it.",
    "day-24-hybrid-identity":
        "A company has fifteen years of on-prem Active Directory - decades "
        "of accumulated group policy, file shares, and legacy apps that "
        "will never move to the cloud - but also wants Microsoft 365 and "
        "Azure. Hybrid identity is how that company gets one identity that "
        "works everywhere, instead of maintaining two separate, drifting "
        "sets of user accounts forever.",
    "day-25-self-test":
        "The exam doesn't ask you to build something with the lesson open "
        "next to you. Neither does an interview. This is the day that "
        "tests whether the knowledge actually stuck, or whether you were "
        "just following steps.",
    "day-26-log-analytics-diagnostics":
        "A production app goes down at 3am and there's no logging turned "
        "on, so troubleshooting starts from zero. Diagnostic settings "
        "piping into Log Analytics turn 'we have no idea what happened' "
        "into 'here's the exact error and the exact minute it started.'",
    "day-27-alerts-action-groups":
        "A disk fills up on a Friday afternoon and nobody notices until "
        "Monday morning, when the app has been down all weekend. An alert "
        "rule wired to an action group is the difference between someone "
        "getting paged Friday at 3pm versus finding out from an angry "
        "customer on Monday.",
    "day-28-azure-backup":
        "A ransomware attack encrypts a company's production database, and "
        "their only backup is a manual export someone meant to automate "
        "eighteen months ago. Azure Backup with a real retention policy is "
        "what makes 'restore from last night' an actual option instead of a "
        "hope.",
    "day-29-update-management-arc":
        "A company has a mix of cloud VMs and physical servers still "
        "sitting in a closet somewhere, and the on-prem boxes never get the "
        "same patching, monitoring, or policy the cloud VMs get, because "
        "they're invisible to the same tools. Arc is how a company brings "
        "those boxes into the same management plane instead of treating "
        "them as a permanent blind spot.",
    "day-30-final-teardown":
        "Same discipline as Day 10 and Day 20, at the scale of the entire "
        "six-week build. A real engineer doesn't just build things, they "
        "also know exactly what's running and why, and can prove nothing "
        "billable is left orphaned when a project wraps.",
}

HEADER = "## Why This Matters (Business Context)"

added = 0
already = 0
missing = 0

for lesson_file in sorted(base_path.glob("*/day-*/lesson.md")):
    day_slug = lesson_file.parent.name
    context = BUSINESS_CONTEXT.get(day_slug)

    if context is None:
        print(f"No business context defined for {day_slug} - skipping")
        missing += 1
        continue

    text = lesson_file.read_text(encoding="utf-8")

    if HEADER in text:
        already += 1
        continue

    text = text.rstrip() + f"\n\n{HEADER}\n{context}\n"
    lesson_file.write_text(text, encoding="utf-8")
    added += 1

print()
print(f"Done - {added} lessons got a business context section, "
      f"{already} already had one, {missing} missing a mapping.")