# Day 04 Lesson - VMs and Availability Zones

## Core Concepts (Read This First)

### Availability Zone vs Availability Set
These sound similar and get confused constantly, including on the exam.
An **Availability Set** is a logical grouping within a single Azure
datacenter - it spreads your VMs across separate physical racks (update
domains and fault domains) so a single hardware failure or planned
maintenance doesn't take out every VM at once. It protects you from
failures inside one datacenter. An **Availability Zone** is much bigger
blast-radius protection: each zone is a physically separate datacenter
within the region, with its own independent power, cooling, and
networking. Pinning VMs across multiple zones protects you even if an
entire datacenter goes down.

### SLA Differences
A genuine exam-relevant number worth knowing: a single VM using Premium
SSD gets a 99.9% SLA. VMs in an Availability Set get 99.95%. VMs spread
across Availability Zones get 99.99%. Each jump is a real, meaningfully
different amount of allowed downtime per year - 99.9% allows roughly 8.7
hours of downtime a year; 99.99% allows roughly 52 minutes.

### Not Every Region Supports Zones
Availability Zones require the region to physically have multiple
independent datacenters - not every Azure region does. Before you plan a
zone-based design, check that the target region actually supports zones
rather than assuming it does.

## What You're Building Today
Your first VM in Bicep, pinned to a specific availability zone.

## New Bicep Concepts
- `zones` property (an array of strings, not integers)
- `@secure()` decorator for passwords
- Resource dependencies through property references (implicit `dependsOn`)

## Annotated Example
A VM needs a NIC, and the NIC needs a subnet, so this is a three-resource
chain even for a "simple" VM. Trimmed to the essentials:
```bicep
@secure()
param adminPassword string
param adminUsername string = 'azureuser'

resource nic 'Microsoft.Network/networkInterfaces@2023-11-01' = {
  name: 'vm-nic-01'
  location: resourceGroup().location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: subnetId   // passed in or referenced from an existing VNet
          }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: 'vm-web-01'
  location: resourceGroup().location
  zones: [ '1' ]
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_B1s'
    }
    osProfile: {
      computerName: 'vm-web-01'
      adminUsername: adminUsername
      adminPassword: adminPassword
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
  }
}
```

## Why It's Written This Way
- `zones: [ '1' ]` - notice these are strings, `'1'` not `1`. This is a
  common first mistake. Zone numbers are logical to your subscription, not
  a physical location you can predict.
- `nic.id` inside `networkProfile` is how Bicep figures out deployment
  order without you writing an explicit `dependsOn` - referencing another
  resource's property automatically creates the dependency.
- `@secure()` on `adminPassword` means Azure won't log the value or show it
  in deployment history or the portal. Always use it for anything
  password- or secret-shaped.
- For B1s/B2s cost control (see the blueprint's cost rules), this is also
  exactly the resource you deallocate the moment the session ends -
  `az vm deallocate --resource-group <rg> --name vm-web-01`.

## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines>
<https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.VMSS.AvailabilityZone/>

## Why This Matters (Business Context)
An e-commerce company's checkout service runs on a single VM in a single datacenter. That datacenter has a power event during a big sale, and every transaction is gone until it comes back. Availability zones are the difference between 'one datacenter went down' and 'nothing happened, the other two zones picked up the load.'
