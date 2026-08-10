# Day 05 Lesson - VM Scale Sets

## What You're Building Today
A small VM Scale Set (VMSS) spread across availability zones.

## New Bicep Concepts
- `sku.capacity` - how many instances, set right on the SKU block
- Zone-spreading a whole scale set instead of one VM

## Annotated Example
```bicep
resource vmss 'Microsoft.Compute/virtualMachineScaleSets@2024-07-01' = {
  name: 'vmss-web'
  location: resourceGroup().location
  zones: [ '1', '2', '3' ]
  sku: {
    name: 'Standard_B2s'
    tier: 'Standard'
    capacity: 3
  }
  properties: {
    upgradePolicy: {
      mode: 'Manual'
    }
    virtualMachineProfile: {
      osProfile: {
        computerNamePrefix: 'vmssweb'
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
      }
      networkProfile: {
        networkInterfaceConfigurations: [
          {
            name: 'vmss-nic'
            properties: {
              primary: true
              ipConfigurations: [
                {
                  name: 'ipconfig1'
                  properties: {
                    subnet: {
                      id: subnetId
                    }
                  }
                }
              ]
            }
          }
        ]
      }
    }
  }
}
```

## Why It's Written This Way
- With a single VM, `sku` describes the VM size. With a VMSS, `sku` ALSO
  carries `capacity` - how many instances to run. This trips people up
  coming from single-VM Bicep.
- `zones: [ '1', '2', '3' ]` on a VMSS spreads new instances across all
  three zones as it scales, rather than pinning to one. That's the whole
  point of doing this at the scale-set level instead of one VM at a time.
- Notice there's no single `osDisk` or `networkInterfaces` block the way a
  single VM has - VMSS nests everything one level deeper under
  `virtualMachineProfile`, since it's describing a template for instances,
  not one concrete machine.
- `upgradePolicy.mode: 'Manual'` is the safe default while you're learning
  - it means changing the model doesn't automatically start replacing
  running instances.

## Source
<https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.VMSS.AvailabilityZone/>