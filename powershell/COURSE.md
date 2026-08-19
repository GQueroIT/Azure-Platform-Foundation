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
