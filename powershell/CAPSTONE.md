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
