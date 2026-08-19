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
