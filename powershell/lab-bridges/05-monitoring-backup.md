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
