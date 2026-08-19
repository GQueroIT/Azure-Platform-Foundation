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
