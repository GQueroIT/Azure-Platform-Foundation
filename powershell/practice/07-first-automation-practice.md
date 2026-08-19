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
