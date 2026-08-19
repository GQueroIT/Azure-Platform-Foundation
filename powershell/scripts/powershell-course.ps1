[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Resolve the repository root.
# Priority:
#   1. -RepoRoot supplied by the user
#   2. current Git repository root
#   3. current working directory
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    try {
        $gitRoot = (& git rev-parse --show-toplevel 2>$null).Trim()
    }
    catch {
        $gitRoot = $null
    }

    if (-not [string]::IsNullOrWhiteSpace($gitRoot)) {
        $RepoRoot = $gitRoot
    }
    else {
        $RepoRoot = (Get-Location).Path
    }
}

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
Write-Host "Repository root: $RepoRoot"

function Write-CourseFile {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)]
        [string]$RelativePath,

        [Parameter(Mandatory)]
        [string]$Content
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    $parent = Split-Path $fullPath -Parent

    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    if ((Test-Path $fullPath) -and -not $Force) {
        Write-Host "SKIP  $RelativePath (already exists; use -Force to overwrite)"
        return
    }

    if ($PSCmdlet.ShouldProcess($fullPath, 'Create PowerShell course file')) {
        Set-Content -Path $fullPath -Value $Content -Encoding utf8
        Write-Host "WRITE $RelativePath"
    }
}

# Safety check: run this from the Azure-Platform-Foundation repo root
$expected = @(
    '.git',
    'powershell',
    '01-compute-governance',
    '02-networking',
    '03-storage',
    '04-identity-access',
    '05-monitoring-backup'
)

$missing = $expected | Where-Object { -not (Test-Path (Join-Path $RepoRoot $_)) }

if (@($missing).Count -gt 0) {
    throw "This does not look like the Azure-Platform-Foundation repo root. Missing: $($missing -join ', '). Run this from inside the repo, or use -RepoRoot <path>."
}

$course = @'
# Azure PowerShell Automation Course

This course grows alongside Azure-Platform-Foundation.

The rule is simple:

> Learn the PowerShell concept first, practice it in a safe local exercise, then apply it to the Azure lab I already understand.

The goal is not to memorize cmdlets. The goal is to become able to discover commands, inspect Azure objects, make safe changes, automate repetitive administration, troubleshoot failures, and eventually run unattended automation.

## Course Flow

1. Foundation lessons 01-07
2. Practice drills for each foundation lesson
3. Lab bridges tied to each Azure phase
4. Advanced automation lessons
5. Capstone operations toolkit

## Required Workflow for Every Lesson

### Step 1 - Learn
Read the lesson and run every example manually.

### Step 2 - Local Practice
Complete the practice exercises without Azure first when possible.

### Step 3 - Azure Read-Only Practice
Use Get-* cmdlets to inspect the resources built in the current lab.

### Step 4 - Azure Change Practice
Only after the read-only practice makes sense, perform a controlled change.

### Step 5 - Break/Test
Test one bad input, empty result, wrong name, wrong scope, or permission issue.

### Step 6 - Verify
Confirm the result with a second command or the Azure Portal.

### Step 7 - Document
Record:
- What I tried
- What worked
- What failed
- What fixed it
- How I verified it

## Foundation Order

- 01 Fundamentals
- 02 Variables and data types
- 03 Pipeline and objects
- 04 Control flow
- 05 Functions and parameters
- 06 Connecting to Azure
- 07 Script structure and first automation

Do not rush these. The lab-bridge files assume these concepts gradually become familiar.

## Important Lesson 06 Note

Azure PowerShell contexts can persist across PowerShell sessions depending on context autosave settings. Do not assume that closing a terminal always signs you out.

Use:

```powershell
Get-AzContext
```

at the start of a session and verify the account, tenant, and subscription before making changes.

## Progression

Level 1: Get information  
Level 2: Filter information  
Level 3: Make decisions from information  
Level 4: Change one resource  
Level 5: Change many resources  
Level 6: Build reusable functions  
Level 7: Handle failures safely  
Level 8: Produce logs and reports  
Level 9: Run unattended  
Level 10: Operate the Azure lab through a toolkit

## Microsoft Learn References

- PowerShell learning: https://learn.microsoft.com/powershell/
- Azure PowerShell: https://learn.microsoft.com/powershell/azure/
- Manage Azure resources with PowerShell: https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resources-powershell
- about_Functions: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_functions
- about_Splatting: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_splatting
- Error handling: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_error_handling
- ShouldProcess / WhatIf: https://learn.microsoft.com/powershell/scripting/learn/deep-dives/everything-about-shouldprocess
- Azure Automation managed identity: https://learn.microsoft.com/azure/automation/enable-managed-identity-for-automation
'@

$rubric = @'
# PowerShell Practice Rubric

Use this rubric for every practice file.

## Bronze - I Can Read It

I can explain what every line does.

## Silver - I Can Change It

I can change names, filters, parameters, and output without breaking the script.

## Gold - I Can Build It

I can recreate the solution from a blank file using Get-Help and Get-Command.

## Platinum - I Can Troubleshoot It

I can diagnose:
- wrong resource name
- empty results
- wrong Azure context
- permission problems
- bad parameter values
- non-terminating errors

## Rule

Do not count copy/paste as completion.

A practice is complete when I can explain why the command works and reproduce the main logic without looking at the finished answer.
'@

$p1 = @'
# Practice 01 - Fundamentals

## Goal

Become comfortable discovering PowerShell commands instead of waiting to be told the exact syntax.

## Local Warm-Up

Run:

```powershell
Get-Command Get-*
Get-Command *Process*
Get-Help Get-Process -Examples
Get-Help Get-ChildItem -Full
```

### Questions

1. What is the verb in `Get-ChildItem`?
2. What is the noun?
3. What parameter examples did `Get-Help` show?
4. Find a command that writes data to a file without searching the web.

## Azure Discovery Drill

Without looking up the exact answers first, use `Get-Command` to find cmdlets related to:

- resource groups
- management groups
- role assignments
- policy
- locks
- storage accounts
- virtual networks

Example discovery pattern:

```powershell
Get-Command *Az*Lock*
```

Do not stop at finding the cmdlet. Run:

```powershell
Get-Help <cmdlet> -Examples
```

## Lab Application

For the current Azure lab, identify at least three Get-* cmdlets that can inspect what you built.

Do not make changes yet.

## Challenge

Create `command-notes.md` containing:

| Task | Cmdlet I Found | How I Found It |
|---|---|---|

Add five commands discovered without being given their names.
'@

$p2 = @'
# Practice 02 - Variables and Data Types

## Goal

Stop hardcoding values and learn how data is stored before using it in Azure automation.

## Local Practice

Create:

```powershell
$project = "Azure-Platform-Foundation"
$day = 3
$isLab = $true
$services = @("governance", "compute", "networking")
```

Inspect their types:

```powershell
$project.GetType().Name
$day.GetType().Name
$isLab.GetType().Name
$services.GetType().Name
```

## Hashtable Practice

Build a tag hashtable:

```powershell
$tags = @{
    Environment = "lab"
    Service     = "storage"
    Project     = "az104"
}
```

Practice:

```powershell
$tags.Environment
$tags["Service"]
$tags.Keys
$tags.Values
```

## Azure Application

Create variables for:

- subscription name
- resource group name
- location
- tag name
- tag value

Then use those variables in read-only Azure commands.

## Challenge

Create an array of three resource group names.

Looping is not required yet. Your only goal is to store and inspect the values correctly.

## Stretch

Build a hashtable describing one Azure resource:

```text
Name
ResourceGroup
Location
Purpose
Environment
```

Print a sentence using string interpolation.
'@

$p3 = @'
# Practice 03 - Pipeline and Objects

## Goal

Understand that PowerShell works with objects, not just text.

This is one of the most important lessons in the course.

## Local Practice

Run:

```powershell
Get-Process | Get-Member
```

Then:

```powershell
Get-Process |
    Select-Object Name, Id, CPU |
    Sort-Object CPU -Descending
```

Filter:

```powershell
Get-Process |
    Where-Object { $_.CPU -gt 10 }
```

## Questions

1. What type of object did `Get-Process` return?
2. What properties did you discover with `Get-Member`?
3. What does `$_` represent?
4. What changed when you used `Select-Object`?

## Azure Application

Run:

```powershell
Get-AzResource | Get-Member
```

Then build a report containing only:

```text
Name
ResourceType
ResourceGroupName
Location
```

Next, filter it to only resources in the location used by the current lab.

## Challenge

Without using the Portal, answer:

- How many Azure resources currently exist?
- How many are in the current lab resource group?
- Which resource types are present?

## Stretch

Export the selected inventory to CSV.

Do not automate a change yet. This lesson is about seeing and shaping data.
'@

$p4 = @'
# Practice 04 - Control Flow

## Goal

Make scripts react to the state they discover.

## Local Practice

Create:

```powershell
$cost = 18
```

Write logic:

```text
If cost is 0 -> "No cost"
If cost is less than 20 -> "Within lab range"
Otherwise -> "Investigate"
```

Then rebuild it with `switch` if appropriate.

## Operator Drill

Practice:

- `-eq`
- `-ne`
- `-gt`
- `-lt`
- `-like`
- `-contains`
- `-and`
- `-or`
- `-not`

## Azure Application

Pick a resource from the current lab.

Use PowerShell to determine whether it has a required tag.

Pseudocode:

```text
Get resource
If Service tag exists
    print its value
Else
    print "Missing Service tag"
```

At this point, only report the problem. Do not fix it automatically yet.

## Challenge

Check whether the active Azure context points at the expected subscription.

If not, print a warning and stop your practice script.
'@

$p5 = @'
# Practice 05 - Loops and Repetition

## Goal

Scale from checking one resource to checking many.

## Local Practice

```powershell
$names = @("vm01", "vm02", "vm03")

foreach ($name in $names) {
    Write-Output "Checking $name"
}
```

Then perform the same task with `ForEach-Object`.

## Explain

Write one sentence explaining when you would choose:

- `foreach`
- `ForEach-Object`

## Azure Application

Retrieve every resource in one resource group.

Loop through them and print:

```text
Resource Name
Resource Type
Location
```

## Governance Drill

Loop through every resource and report whether `Service` exists as a tag.

Output should make missing tags obvious.

## Challenge

Count:

- total resources
- resources with Service tag
- resources missing Service tag

Do not modify missing tags yet.
'@

$p6 = @'
# Practice 06 - Functions and Parameters

## Goal

Package repeated logic into reusable tools.

## Local Practice

Create:

```powershell
function Get-Greeting {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    "Hello, $Name"
}
```

Run it correctly and incorrectly.

## Azure Function 1

Create:

```text
Get-LabResourceSummary
```

Parameters:

- ResourceGroupName

Output:

```text
Name
ResourceType
Location
```

## Azure Function 2

Create:

```text
Test-RequiredTag
```

Parameters:

- ResourceGroupName
- TagName

For every resource, return whether the tag exists.

## Challenge

Do not use hardcoded resource group names inside the functions.

## Stretch

Add `[CmdletBinding()]` and use `Write-Verbose` so the function can be run with:

```powershell
Test-RequiredTag -ResourceGroupName "..." -TagName "Service" -Verbose
```
'@

$p7 = @'
# Practice 07 - Script Structure and First Automation

## Goal

Turn individual commands into a script that can be safely reused.

## Required Script Structure

Your script should contain:

1. comment-based help
2. `param()`
3. Azure context verification
4. `try/catch`
5. clear empty-result handling
6. useful output
7. success/failure exit behavior where appropriate

## Project Script

Create:

```text
Get-LabGovernanceReport.ps1
```

Parameters:

- ResourceGroupName
- RequiredTag

The script should report:

- resource name
- type
- location
- whether the required tag exists
- lock count for the resource group

## Failure Tests

Test all of these:

1. valid resource group
2. nonexistent resource group
3. not connected to Azure
4. resource group with no resources
5. required tag that does not exist

## Rule

Use `-ErrorAction Stop` for Az cmdlets whose failure should enter `catch`.

## Verification

Compare the script result to the Azure Portal.

## Stretch

Export the report to CSV using an optional parameter:

```powershell
-OutputPath
```
'@

$gov = @'
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
'@

$net = @'
# Lab Bridge - 02 Networking

Use PowerShell to inspect before you configure.

## VNet and Subnet Practice

Report:

```text
VNet
Address Space
Subnet
Subnet Prefix
Resource Group
```

Important lesson: Azure networking cmdlets often return nested objects. Practice accessing child properties instead of treating output as flat text.

## NSG Practice

Build a report:

```text
NSG
Rule
Priority
Direction
Protocol
Source
Destination
Access
```

### Challenge
Identify rules that are unusually broad.

Do not automatically delete or modify them.

## Peering Practice

Report:

```text
VNet A
VNet B
Peering State
Allow Forwarded Traffic
Gateway Transit
```

## Expensive Resource Practice

Build:

```text
Get-ExpensiveNetworkResources.ps1
```

Detect whether the lab still contains resources such as Bastion, VPN Gateway, or Application Gateway after a session.

The first version only reports.

A later version can become part of cleanup automation.

## Troubleshooting Practice

Given a source and destination:

1. inspect VNet/subnet membership
2. inspect NSGs
3. inspect routes where relevant
4. report likely blockers

Capstone:

```text
Get-NetworkHealthReport.ps1
```
'@

$storage = @'
# Lab Bridge - 03 Storage

## Inventory Practice

Report:

```text
Storage Account
Resource Group
Location
SKU
Kind
Minimum TLS Version
Public Network Access
HTTPS Only
```

## Tag Practice

Find storage accounts missing:

```text
Service
Environment
Owner
```

## Security Baseline Practice

Version 1 only reports possible issues.

Examples:

- unexpected public access
- old TLS configuration
- missing tags
- unexpected redundancy

## Data Plane Practice

When working with containers and blobs, note that Azure Resource Manager operations and storage data operations are not the same thing.

Document which commands work against:

```text
control plane
data plane
```

## Automation Upgrade

Build:

```text
Get-StorageBaselineReport.ps1
```

Then later:

```text
Repair-StorageTags.ps1
```

The repair script must support safe preview behavior before modifying resources.
'@

$identity = @'
# Lab Bridge - 04 Identity and Access

This phase introduces Microsoft Graph PowerShell alongside Az PowerShell.

## Core Distinction

Use Az PowerShell primarily for Azure Resource Manager resources and Azure RBAC.

Use Microsoft Graph PowerShell for Microsoft Entra directory objects such as users and groups.

## Practice 1 - Users

Report:

```text
Display Name
User Principal Name
Account Enabled
```

## Practice 2 - Groups

Report:

```text
Group
Group Type
Members
```

## Practice 3 - RBAC

Report Azure role assignments separately from Entra directory roles.

Do not mix the two concepts.

## CSV Practice

Create a small local CSV containing test identities.

Practice:

```powershell
Import-Csv
```

Validate every row before taking action.

## Automation Upgrade

Build:

```text
Get-IdentityAccessReport.ps1
```

Later:

```text
Test-GroupMembershipBaseline.ps1
```

Do not perform bulk user creation until validation, error handling, and logging are comfortable.
'@

$monitor = @'
# Lab Bridge - 05 Monitoring and Backup

## Monitoring Practice

Inventory:

```text
alerts
action groups
diagnostic settings
Log Analytics workspaces
```

## Reporting Practice

Build a health report that combines multiple Azure object types.

This is where functions become important.

Example structure:

```text
Get-LabHealth
    Get-ComputeHealth
    Get-NetworkHealth
    Get-StorageHealth
    Get-BackupHealth
```

## Logs

PowerShell should not replace KQL.

Use the right tool for the layer:

```text
PowerShell -> orchestration and processing
KQL        -> querying log data
```

## Backup Practice

Answer:

```text
Which workloads are protected?
Which are not?
What was the latest backup state?
```

## Automation Upgrade

Build:

```text
Get-PlatformOperationsReport.ps1
```

This becomes one of the capstone scripts.
'@

$a8 = @'
# Advanced 08 - Splatting

## Why

Azure cmdlets become difficult to read when they have many parameters.

Splatting stores command parameters in a hashtable.

## Practice

Start with:

```powershell
$params = @{
    Name     = "example"
    Location = "eastus"
}
```

Inspect the hashtable.

Then use splatting with a harmless local or read-only command before applying it to an Azure create/change command.

## Azure Application

Take one Azure cmdlet from a completed lab that uses several parameters.

Write it once normally.

Then rewrite it with a splatting hashtable.

## Challenge

Add or remove one optional parameter by changing only the hashtable.

## Why It Matters

This becomes important when scripts later construct parameters conditionally.
'@

$a9 = @'
# Advanced 09 - Safe Automation with WhatIf

## Goal

Never make destructive automation the first version of a script.

PowerShell advanced functions can implement `SupportsShouldProcess`, which provides `-WhatIf` and `-Confirm` behavior.

## Practice

Create a local function that would delete a temporary file.

Wrap the change with:

```powershell
[CmdletBinding(SupportsShouldProcess)]
```

and:

```powershell
$PSCmdlet.ShouldProcess(...)
```

Run it with:

```powershell
-WhatIf
```

before allowing a real deletion.

## Azure Application

Choose a lab action that changes or removes a resource.

Build a wrapper function that:

1. discovers the target
2. validates the target
3. calls `ShouldProcess` immediately around the change
4. supports `-WhatIf`

## Rule

Read-only functions do not need `ShouldProcess`.

Functions that change state should be designed with safety from the beginning.
'@

$a10 = @'
# Advanced 10 - Error Handling and Logging

## Error Handling

Learn the difference between errors that stop execution and errors that continue.

For Az cmdlets used inside `try/catch`, use `-ErrorAction Stop` when failure should be caught.

## Practice

Write a script that intentionally queries a nonexistent Azure resource group.

Handle the failure and produce a clear message.

## Logging

Create structured log records with:

```text
Timestamp
Operation
Target
Status
Message
```

Represent each record as a PowerShell object.

Export the log to CSV.

## Challenge

Run an operation over multiple resources.

One failure should be logged clearly.

Decide whether the remaining resources should continue or whether the script should stop, and explain why.

## Stretch

Add a `-Verbose` mode for troubleshooting without cluttering normal output.
'@

$a11 = @'
# Advanced 11 - Idempotent and State-Aware Automation

## Goal

Stop writing scripts that blindly perform actions.

Ask:

```text
What is the current state?
What is the desired state?
Is a change actually required?
```

## Tag Example

```text
Correct tag already exists -> do nothing
Tag missing -> add it
Tag has wrong value -> update it
```

## Lock Example

```text
Correct CanNotDelete lock exists -> do nothing
No lock -> create it
Wrong lock level -> report or change based on script purpose
```

## VM Example

```text
VM already deallocated -> do nothing
VM running and should be stopped -> stop it
```

## Practice

Take one lab task previously performed manually.

Write pseudocode for current state vs desired state before writing PowerShell.

Then implement version 1 as reporting only.

Only after the report is correct should version 2 make changes.
'@

$a12 = @'
# Advanced 12 - Configuration Files and Input Validation

## Goal

Separate reusable logic from environment-specific values.

## Practice

Create a JSON file containing:

```json
{
  "resourceGroup": "example",
  "location": "eastus",
  "requiredTags": {
    "Environment": "lab",
    "Service": "storage"
  }
}
```

Read it with PowerShell.

## Validation

Before using configuration values:

- confirm required properties exist
- confirm strings are not empty
- validate allowed values
- stop clearly on bad input

## Azure Application

Move environment-specific names out of one existing script and into a configuration file.

The script should still work without editing its code.
'@

$a13 = @'
# Advanced 13 - Script Composition and Modules

## Goal

Stop building giant one-file scripts.

Recommended structure:

```text
powershell/
  scripts/
  functions/
  config/
  reports/
  logs/
```

## Practice

Take two functions from earlier lessons and place them in separate function files.

Dot-source them into a script.

Later, package reusable functions into a module.

## Capstone Module Idea

```text
AzurePlatformFoundation.psm1
```

Possible functions:

```text
Get-LabInventory
Test-LabTags
Test-LabLocks
Get-LabCostResources
Get-NetworkHealth
Get-StorageBaseline
Get-LabHealth
Stop-LabCompute
```

Do not build the module until the underlying functions already work individually.
'@

$a14 = @'
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
'@

$capstone = @'
# Capstone - Azure Platform Operations Toolkit

Build this gradually. Do not wait until the end to start.

Every phase contributes one or more functions.

## Target Functions

```powershell
Get-LabInventory
Get-GovernanceScopeReport
Get-PolicyComplianceReport
Test-LabTagCompliance
Test-LabResourceProtection
Get-ComputeGovernanceReport
Get-NetworkHealthReport
Get-StorageBaselineReport
Get-IdentityAccessReport
Get-PlatformOperationsReport
```

## Later Change Functions

```powershell
Set-LabTag
Set-LabResourceLock
Stop-LabCompute
Remove-LabEnvironment
```

Any function that changes or removes resources should be designed for safe preview and explicit validation.

## Capstone Requirements

The toolkit should eventually:

- verify Azure context
- accept parameters instead of hardcoded resource names
- use functions
- use object output
- handle empty results
- handle errors
- support verbose troubleshooting
- log important actions
- avoid storing credentials
- support safe preview on destructive operations
- operate against the real Azure-Platform-Foundation environment

## Final Test

From a new PowerShell session, I should be able to use the toolkit to answer:

```text
What is deployed?
Where is it?
Who has access?
Which policies apply?
Which resources are missing tags?
Which resources are protected by locks?
Which VMs are running?
What networking resources exist?
Which storage accounts violate my baseline?
What resources may still be generating cost?
What needs my attention?
```

That is the point where PowerShell has moved from "a language I am studying" to "a tool I use to operate Azure."
'@

$files = @{
    'powershell/COURSE.md' = $course
    'powershell/PRACTICE-RUBRIC.md' = $rubric

    'powershell/practice/01-fundamentals-practice.md' = $p1
    'powershell/practice/02-variables-practice.md' = $p2
    'powershell/practice/03-pipeline-objects-practice.md' = $p3
    'powershell/practice/04-control-flow-practice.md' = $p4
    'powershell/practice/05-loops-practice.md' = $p5
    'powershell/practice/06-functions-practice.md' = $p6
    'powershell/practice/07-first-automation-practice.md' = $p7

    'powershell/lab-bridges/01-compute-governance.md' = $gov
    'powershell/lab-bridges/02-networking.md' = $net
    'powershell/lab-bridges/03-storage.md' = $storage
    'powershell/lab-bridges/04-identity-access.md' = $identity
    'powershell/lab-bridges/05-monitoring-backup.md' = $monitor

    'powershell/advanced/08-splatting.md' = $a8
    'powershell/advanced/09-safe-automation-whatif.md' = $a9
    'powershell/advanced/10-error-handling-logging.md' = $a10
    'powershell/advanced/11-idempotent-state-aware-automation.md' = $a11
    'powershell/advanced/12-configuration-and-validation.md' = $a12
    'powershell/advanced/13-script-composition-and-modules.md' = $a13
    'powershell/advanced/14-unattended-automation.md' = $a14

    'powershell/CAPSTONE.md' = $capstone
}

foreach ($entry in $files.GetEnumerator()) {
    Write-CourseFile -RelativePath $entry.Key -Content $entry.Value -WhatIf:$WhatIfPreference
}

# Keep a clean location for the user's own scripts.
$scriptsReadme = @'
# Scripts

This folder contains scripts I personally build while progressing through the PowerShell course and Azure labs.

Rules:

- Do not save copied Microsoft examples here as if they are my own work.
- Scripts should solve a task from the Azure-Platform-Foundation project.
- Prefer parameters over hardcoded environment values.
- Read-only/reporting scripts come before change scripts.
- Destructive scripts should eventually support safe preview behavior.
- Document failures and fixes.
'@

Write-CourseFile -RelativePath 'powershell/scripts/README.md' -Content $scriptsReadme -WhatIf:$WhatIfPreference

Write-Host ""
Write-Host "PowerShell course scaffold complete."
Write-Host "Start with: powershell/COURSE.md"
Write-Host "Then use: powershell/practice/01-fundamentals-practice.md"
Write-Host ""
Write-Host "Suggested Git commands:"
Write-Host "  git status"
Write-Host "  git add powershell"
Write-Host '  git commit -m "Add project-scoped PowerShell automation course"'