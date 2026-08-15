# Day 05 Lesson - VM Scale Sets

## Core Concepts (Read This First)

### Orchestration Mode: The Decision You Can't Undo Later
Every VM Scale Set is built in one of two orchestration modes, and Azure
won't let you change it after the scale set is created - picking wrong
means recreating the whole thing. **Uniform** mode is the older approach:
every instance is identical, managed through the scale set's own API
rather than normal VM APIs, and individual instances can't use things
like Azure Backup or standard RBAC tagging the way a regular VM can.
**Flexible** mode is Microsoft's current recommendation for basically all
new scale sets - each instance behaves like a real, standalone VM under
the hood (so it works with the normal VM APIs, Backup, tagging,
everything), while still giving you scale-set-level autoscaling and
zone-spreading. If you don't explicitly set `orchestrationMode`, it
defaults to Uniform - worth setting on purpose:

```bicep
properties: {
  orchestrationMode: 'Flexible'
  // ...
}
```

Exam material and a lot of existing documentation (including patterns
you'll see online) still lean on Uniform because it's older and
better-documented - but for anything you'd actually build today, Flexible
is the right default.

### Autoscale Isn't Automatic Just Because You Have a VMSS
Deploying a scale set with `capacity: 3` gives you exactly 3 instances,
permanently, until you manually change that number - it does not scale on
its own. Actual autoscaling requires a separate
`Microsoft.Insights/autoscaleSettings` resource defining rules (e.g. "add
an instance when average CPU > 70% for 5 minutes"), which isn't in this
lesson's example. Worth knowing going in so you don't expect scale-out
behavior that the base VMSS resource alone doesn't provide.

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

## Why This Matters (Business Context)
Traffic to a retail site is flat most of the year and 20x normal during a holiday sale. Provisioning for peak year-round wastes money every other week; provisioning for average traffic means the site falls over during the sale. A scale set is how you pay for average and still survive peak.
