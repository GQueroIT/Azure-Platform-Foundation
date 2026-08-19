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
