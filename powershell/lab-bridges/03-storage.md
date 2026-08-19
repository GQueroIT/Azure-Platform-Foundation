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
