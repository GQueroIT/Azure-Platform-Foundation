# Lab Bridge - 04 Identity and Access

This phase introduces Microsoft Graph PowerShell alongside Az PowerShell.

## Core Distinction

Use Az PowerShell primarily for Azure Resource Manager resources and Azure RBAC.

Use Microsoft Graph PowerShell for Microsoft Entra directory objects such as users and groups.

## Practice 1 - Users

Report:

```text
Display Name
User Principal Name
Account Enabled
```

## Practice 2 - Groups

Report:

```text
Group
Group Type
Members
```

## Practice 3 - RBAC

Report Azure role assignments separately from Entra directory roles.

Do not mix the two concepts.

## CSV Practice

Create a small local CSV containing test identities.

Practice:

```powershell
Import-Csv
```

Validate every row before taking action.

## Automation Upgrade

Build:

```text
Get-IdentityAccessReport.ps1
```

Later:

```text
Test-GroupMembershipBaseline.ps1
```

Do not perform bulk user creation until validation, error handling, and logging are comfortable.
