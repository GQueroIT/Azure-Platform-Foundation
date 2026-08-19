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
