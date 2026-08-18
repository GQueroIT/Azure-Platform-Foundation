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

## Service Deep Dive

### What It Can't Do
Orchestration mode is a one-way door - once a scale set is created as
Uniform or Flexible, it cannot be converted in place; changing your mind
means recreating the scale set entirely. Uniform mode, despite being the
older and still-default-if-unset mode, genuinely can't do several things
Flexible can: individual instances aren't compatible with standard VM
APIs, Azure Resource Manager tagging, RBAC scoped to the instance, Azure
Backup, or Azure Site Recovery - they're only reachable through the
scale-set-specific API surface. Flexible mode fixes all of that by making
each instance a real, standalone VM resource under the hood, which is
exactly why Microsoft now recommends Flexible for basically everything
new.

A scale set with `capacity: 3` also doesn't scale itself - a bare VMSS
resource with no attached `Microsoft.Insights/autoscaleSettings` resource
just runs a fixed number of instances forever, identical to a fixed count
of individual VMs, until someone manually changes the number.
Autoscaling is a genuinely separate resource you have to deploy on top.

### Nuances Worth Knowing
- **VM instances that Flexible mode creates implicitly (through
  autoscaling, not manually added) don't get default outbound internet
  access** the way a manually created VM would - a documented, deliberate
  security default, not a bug, but a real source of "why can't this
  instance reach the internet" confusion the first time you hit it.
- **Both orchestration modes cap at 1,000 instances per scale set** - not
  a limit you'll come close to in this lab, but worth knowing it exists.
- **A setting called "force strictly even balance across zones" can cause
  scale-in and scale-out operations to fail outright** if Azure can't
  maintain perfectly even distribution across zones at that exact
  moment - it's off by default, but if you ever turn it on expecting
  stricter guarantees, know that it trades that guarantee for occasional
  scaling failures instead of a best-effort rebalance.

### Troubleshooting You'll Actually Hit
- **Symptom:** an instance inside a Flexible-mode scale set can't reach
  the internet or pull an update, even though the VNet/NSG look fine ->
  **Cause:** instances created implicitly through autoscaling don't get
  default outbound access the way manually-created instances do ->
  **Fix:** attach a NAT Gateway, a public IP, or an explicit outbound
  rule on a Standard Load Balancer to the subnet or scale set - don't
  assume default outbound applies here the way it does for a normal VM.
- **Symptom:** trying to switch an existing scale set's
  `orchestrationMode` in Bicep fails or gets rejected -> **Cause:**
  orchestration mode can't be changed after creation -> **Fix:** deploy a
  new scale set with the correct mode and migrate instances/traffic over;
  there's no in-place conversion.
- **Symptom:** an instance stops working and never gets automatically
  replaced -> **Cause:** automatic instance repair isn't on by default -
  it requires both a health probe/extension reporting instance health
  *and* an explicit repair policy configured on the scale set ->
  **Fix:** confirm both pieces are actually configured; having one
  without the other means nothing happens when an instance goes
  unhealthy.

*Checked against: Microsoft Learn's "Orchestration modes for Virtual
Machine Scale Sets" and the Flexible VMSS migration/networking docs.*


## Source
<https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.VMSS.AvailabilityZone/>

## Why This Matters (Business Context)
Traffic to a retail site is flat most of the year and 20x normal during a holiday sale. Provisioning for peak year-round wastes money every other week; provisioning for average traffic means the site falls over during the sale. A scale set is how you pay for average and still survive peak.
