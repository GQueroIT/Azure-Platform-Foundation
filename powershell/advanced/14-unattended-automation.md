# Advanced 14 - Unattended Automation

## Goal

Move from scripts that require a human login to automation that can run safely on its own.

## Concepts

- service principals
- managed identities
- least privilege
- Azure Automation
- runbooks
- scheduled execution
- logging

## Rule

Do not store personal usernames and passwords in scripts.

## Managed Identity Practice

When this project reaches Azure Automation:

1. create an Automation account
2. enable a managed identity
3. grant only the RBAC permissions required
4. authenticate from the runbook
5. run a read-only inventory script first
6. verify logs
7. only then automate changes

## Candidate Runbook

Start with something low-risk:

```text
Report forgotten expensive lab resources
```

Later:

```text
Stop eligible lab VMs on a schedule
```

Do not begin unattended destructive cleanup until `-WhatIf`, validation, logging, and idempotent logic are already familiar.
