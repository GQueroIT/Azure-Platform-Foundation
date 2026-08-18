# Lesson 6 — Connecting to Azure

## Installing the Az module

The Az module is Microsoft's current PowerShell module for managing Azure resources — the older `AzureRM` module is deprecated and shouldn't be used. One-time install, per machine:

```powershell
Install-Module Az -Scope CurrentUser -Repository PSGallery -Force
```

`-Scope CurrentUser` avoids needing admin/sudo — installs into your own profile, not system-wide.

## Connecting

```powershell
Connect-AzAccount
```

This opens a browser window for an interactive login. After signing in, PowerShell holds an authenticated **context** — the combination of account, tenant, and subscription it's currently operating against.

```powershell
Get-AzContext                    # shows what you're currently connected as/to
Get-AzContext -ListAvailable     # every subscription context available to you
Set-AzContext -Subscription "gq1" # switch which subscription commands target
```

Always check `Get-AzContext` at the start of a session before running anything — commands silently run against whatever subscription the context currently points to, which isn't always the one you meant.

## What a "session" means in practice

The authenticated context lives for that terminal session. Close the terminal, and you'll need to `Connect-AzAccount` again next time — same idea as re-authenticating `az login` for the CLI side of this repo. (Newer versions of the Az module have gotten better at persisting context across terminal tabs within the same login session, but don't rely on that — verify with `Get-AzContext` rather than assume you're still connected.)

For anything beyond interactive personal use — a script meant to run unattended — authentication switches to a **service principal** (an application identity instead of a personal login) or a **managed identity** (an identity Azure assigns automatically to a resource like a VM or Function App, so there's no secret to store at all). Not needed for the manual, weekend-driven scripts this repo is building right now — worth knowing the concept exists for when automation moves toward something scheduled or unattended.

## Microsoft Graph — for Entra ID

`Get-AzADUser` and similar exist, but the modern, fuller way to query Entra ID (users, groups, roles) from PowerShell is the **Microsoft Graph PowerShell SDK** — a separate module from Az, talking to the Graph API rather than Azure Resource Manager.

```powershell
Install-Module Microsoft.Graph -Scope CurrentUser -Force
```

```powershell
Connect-MgGraph -Scopes 'User.Read.All'
```

Graph uses **scopes** instead of a subscription context — each scope is a specific permission (`User.Read.All`, `Group.Read.All`, etc.), and you request only what a given script actually needs. If a command fails with a permissions error, it usually means the scope you connected with doesn't cover it — reconnect with the broader scope rather than guessing.

```powershell
Get-MgUser -Top 5
Get-MgUser -UserId "someone@yourtenant.onmicrosoft.com" -Property DisplayName, UserPrincipalName
```

`Find-MgGraphCommand -Command Get-MgUser` will tell you exactly which scopes a given Graph cmdlet needs, if you're not sure what to request.

## Cheatsheet — cmdlets by AZ-104 phase

| Phase | Cmdlets |
|---|---|
| Compute/Governance | `Get-AzVM`, `Get-AzVMSize`, `Get-AzPolicyDefinition`, `Get-AzManagementGroup` |
| Networking | `Get-AzVirtualNetwork`, `Get-AzNetworkSecurityGroup`, `Get-AzLoadBalancer`, `Get-AzApplicationGateway` |
| Storage | `Get-AzStorageAccount`, `Get-AzStorageContainer`, `Get-AzStorageBlob` |
| Identity | `Get-MgUser`, `Get-MgGroup`, `Get-AzRoleAssignment` |
| Monitoring | `Get-AzMetric`, `Get-AzLog`, `Get-AzRecoveryServicesVault` |

## What's next

Lesson 7 puts everything so far together — proper script structure, error handling, and a full worked automation script built line by line.
