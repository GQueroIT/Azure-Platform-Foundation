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
