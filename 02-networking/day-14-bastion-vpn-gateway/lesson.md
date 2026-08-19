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

## Service Deep Dive

### What It Can't Do
Basic SKU Bastion (this lesson's build) can't do file upload/download
through the portal at all - that's only available through a native
RDP/SSH client, and only from Standard SKU up. Basic also can't use
custom ports, IP-based connections, or host scaling - it's fixed at two
instances with no way to add more.

The GatewaySubnet has hard, non-negotiable requirements: named exactly
`GatewaySubnet`, sized at least /27, and no NSG, route table, or other
resource attached to it - genuinely can't, not just shouldn't. Azure
refuses or fails the deployment if any of these are violated.
AzureBastionSubnet has its own separate, equally strict requirement:
exactly that name, minimum /26 (not /27 - that changed in November 2021,
so older /27 deployments only still work because they predate the
change), and no other resources or route tables in it either.

Basic SKU VPN Gateway is treated as legacy - current guidance is
VpnGw1 and above, and mixing SKUs (a Basic gateway with a Standard-SKU
public IP) is a real, documented cause of deployment failure, not a
style preference.

### Nuances Worth Knowing
- A brand-new VPN Gateway deployment isn't fast - creating the gateway
  resource itself commonly takes 30-45 minutes even when everything is
  configured correctly, easy to mistake for a stuck deployment given how
  quickly most other resources in this repo deploy.
- Site-to-Site connections are policy-based or route-based, and
  mismatched Security Association settings or "one tunnel per subnet
  pair" expectations between Azure and an on-prem device are a
  documented cause of *intermittent* (not permanent) disconnects - it
  looks unstable rather than broken, which sends people looking in the
  wrong place first.
- A user-defined route accidentally placed on the GatewaySubnet is a
  documented, sneaky cause of "the tunnel shows Connected but traffic
  still doesn't flow correctly for some destinations" - it's allowed to
  exist there in ways that don't block deployment but do quietly break
  specific traffic paths.

### Troubleshooting You'll Actually Hit
- **Error:** Bastion deployment fails validation -> **Cause:** almost
  always the subnet name isn't exactly `AzureBastionSubnet`, or it's
  smaller than /26 -> **Fix:** rename/resize the subnet to match exactly
  - no flexibility here, unlike most subnet naming elsewhere in this
  repo.
- **Error:** VPN Gateway deployment fails or times out -> **Cause:**
  most commonly the GatewaySubnet is undersized (below /27), misnamed,
  or has an NSG/route table attached; a Basic-SKU gateway paired with a
  non-Basic public IP is another frequent cause -> **Fix:** confirm
  GatewaySubnet is named exactly that, sized /27+, has nothing else
  attached, and that gateway/IP SKUs match.
- **Symptom:** a Site-to-Site connection shows Connected but specific
  traffic still doesn't reach its destination -> **Cause:** frequently a
  UDR on the GatewaySubnet quietly overriding the expected path ->
  **Fix:** check for and remove any route table on the GatewaySubnet
  before assuming the VPN configuration itself is wrong.

*Checked against: Microsoft Learn's "Azure Bastion FAQ," "About Azure
Bastion configuration settings," and "Troubleshoot an Azure S2S VPN
connection" docs.*


## Source
<https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.network/azure-bastion/main.bicep>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworkgateways>

## Why This Matters (Business Context)
A company opens RDP directly to the internet on a VM 'just for now' to make admin easier, and it gets brute-forced within days. Bastion exists so there's never a public RDP/SSH port to attack in the first place. VPN Gateway is the same idea for connecting an entire office network to Azure without exposing anything to the open internet.
