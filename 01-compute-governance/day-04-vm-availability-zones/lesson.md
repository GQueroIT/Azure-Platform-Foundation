# Day 04 Lesson - VMs and Availability Zones

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