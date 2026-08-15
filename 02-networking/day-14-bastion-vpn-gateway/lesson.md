# Day 14 Lesson - Azure Bastion and VPN Gateway

## Core Concepts (Read This First)

### VPN Gateway Connection Types
The gateway resource in this lesson is the shared foundation both
connection types are built on - the actual "type" comes from the
connection resource layered on top of it, not the gateway itself.
**Site-to-Site** connects an entire on-prem network to a VNet, with a VPN
device on each end maintaining a persistent tunnel - this is how a whole
office gets access to Azure resources. **Point-to-Site** connects
individual devices (a single laptop, no VPN hardware needed on that end)
directly into the VNet - this is how one remote person gets in without
the company needing a site-to-site tunnel just for them.

### Bastion SKU Tiers
Bastion has Basic and Standard tiers. Basic (used in this lesson) covers
straightforward RDP/SSH access through the portal, which is all a lab
needs. Standard adds native client support (connecting via your own
RDP/SSH client instead of only the browser), IP-based connection, and the
ability to scale the host for more concurrent sessions - relevant at
organization scale, not for this build.

Cost note: this is the single most expensive day in the whole build. Both
of these resources bill hourly with no "stop" option like a VM has - test,
document, then delete both before you close the laptop.

## What You're Building Today
An Azure Bastion host and a basic VPN Gateway, both attached to an existing
VNet.

## New Bicep Concepts
- Bastion requires a subnet with an exact, non-negotiable name
- Gateway resources need a dedicated subnet too, also with a required name

## Annotated Example
```bicep
resource bastionPip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-bastion'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource bastion 'Microsoft.Network/bastionHosts@2023-11-01' = {
  name: 'bastion-lab'
  location: resourceGroup().location
  sku: { name: 'Basic' }
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: azureBastionSubnetId   // must be a subnet literally named "AzureBastionSubnet"
          }
          publicIPAddress: {
            id: bastionPip.id
          }
        }
      }
    ]
  }
}

resource vpnGatewayPip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-vpngw'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource vpnGateway 'Microsoft.Network/virtualNetworkGateways@2023-11-01' = {
  name: 'vgw-lab'
  location: resourceGroup().location
  properties: {
    gatewayType: 'Vpn'
    vpnType: 'RouteBased'
    sku: {
      name: 'Basic'
      tier: 'Basic'
    }
    ipConfigurations: [
      {
        name: 'vpnGwIpConfig'
        properties: {
          subnet: {
            id: gatewaySubnetId   // must be a subnet literally named "GatewaySubnet"
          }
          publicIPAddress: {
            id: vpnGatewayPip.id
          }
        }
      }
    ]
  }
}
```

## Why It's Written This Way
- Both Bastion and the VPN Gateway need their own dedicated subnet, and
  Azure enforces exact naming: `AzureBastionSubnet` for Bastion,
  `GatewaySubnet` for the gateway. Get the name wrong and the deployment
  fails outright - this isn't a style convention, it's a hard requirement.
- Both need their own Standard public IP - you cannot share one IP between
  Bastion and a VM, or between Bastion and the gateway.
- `vpnType: 'RouteBased'` is the modern standard (route-based over
  policy-based) and is what almost every current tutorial and the exam
  itself assumes unless a question says otherwise.
- Provisioning a VPN Gateway can take 30-45 minutes even after the Bicep
  deployment "succeeds" - the resource exists but isn't fully ready
  immediately. Budget real time for this specific lab.

## Source
<https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.network/azure-bastion/main.bicep>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworkgateways>

## Why This Matters (Business Context)
A company opens RDP directly to the internet on a VM 'just for now' to make admin easier, and it gets brute-forced within days. Bastion exists so there's never a public RDP/SSH port to attack in the first place. VPN Gateway is the same idea for connecting an entire office network to Azure without exposing anything to the open internet.
