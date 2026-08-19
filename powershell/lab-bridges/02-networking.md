# Lab Bridge - 02 Networking

Use PowerShell to inspect before you configure.

## VNet and Subnet Practice

Report:

```text
VNet
Address Space
Subnet
Subnet Prefix
Resource Group
```

Important lesson: Azure networking cmdlets often return nested objects. Practice accessing child properties instead of treating output as flat text.

## NSG Practice

Build a report:

```text
NSG
Rule
Priority
Direction
Protocol
Source
Destination
Access
```

### Challenge
Identify rules that are unusually broad.

Do not automatically delete or modify them.

## Peering Practice

Report:

```text
VNet A
VNet B
Peering State
Allow Forwarded Traffic
Gateway Transit
```

## Expensive Resource Practice

Build:

```text
Get-ExpensiveNetworkResources.ps1
```

Detect whether the lab still contains resources such as Bastion, VPN Gateway, or Application Gateway after a session.

The first version only reports.

A later version can become part of cleanup automation.

## Troubleshooting Practice

Given a source and destination:

1. inspect VNet/subnet membership
2. inspect NSGs
3. inspect routes where relevant
4. report likely blockers

Capstone:

```text
Get-NetworkHealthReport.ps1
```
