# Lab Bridge - 01 Compute and Governance

Use this file while working through `01-compute-governance`.

The point is not to finish every PowerShell task immediately. Match the task to your current PowerShell level.

## Day 01 - Management Groups and RBAC

### Beginner
- `Get-AzContext`
- inspect subscriptions
- inspect management groups
- inspect role definitions
- inspect role assignments

### Practice Goal
Answer with PowerShell:

```text
What subscription am I targeting?
What management groups exist?
Where is my subscription in the hierarchy?
What custom roles exist?
Who has the Custom VM Operator role?
At what scope?
```

### Automation Upgrade
Build:

```text
Get-GovernanceScopeReport.ps1
```

Do not assign roles automatically until functions and `-WhatIf` make sense.

---

## Day 02 - Azure Policy

### Beginner
Inspect:

```text
policy definitions
policy assignments
policy state/compliance
```

### Practice Goal
Answer:

```text
Which policies are assigned?
At what scope?
What effect do they use?
Which resources are noncompliant?
```

### Automation Upgrade
Build:

```text
Get-PolicyComplianceReport.ps1
```

---

## Day 03 - Locks and Budgets

### Beginner
Inspect locks with PowerShell.

### Practice Goal
Answer:

```text
Which resource groups have locks?
What lock level is applied?
Is it inherited by resources underneath?
```

Microsoft documents `New-AzResourceLock`, `Get-AzResourceLock`, and `Remove-AzResourceLock` for resource lock management.

### Controlled Change Practice
Create a temporary `CanNotDelete` lock with PowerShell.

Verify it.

Remove it.

### Automation Upgrade
Build:

```text
Test-LabResourceProtection.ps1
```

Report whether important lab resource groups have a lock.

---

## Day 03b - Tags and Advisor

### Beginner
Inspect tags on every resource.

### Practice Goal
Report:

```text
Name
Type
Service tag
Environment tag
```

### Automation Upgrade
Build:

```text
Test-LabTagCompliance.ps1
```

Rules:

- detect missing tags
- detect unexpected values
- do not modify anything in version 1

Version 2 may add missing tags after you have learned safe change patterns.

---

## Compute Days

As VMs appear later in this phase, progress through:

1. inventory VMs
2. inspect VM state
3. filter by tags/location
4. start/stop one VM
5. start/stop multiple eligible VMs
6. add `-WhatIf`
7. log every action

Capstone for this phase:

```text
Get-ComputeGovernanceReport.ps1
```
