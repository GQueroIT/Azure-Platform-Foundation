# Day 06 Lesson - Managed Disks and VM Extensions

## Core Concepts (Read This First)

### Disk Tiers
Managed disks come in four performance tiers, and the exam expects you to
know the shape of the tradeoff even if not exact IOPS numbers:
**Standard HDD** (cheapest, spinning disk, fine for infrequent access or
backups), **Standard SSD** (better latency than HDD, still
budget-friendly, fine for lightly used production workloads),
**Premium SSD** (the default for anything performance-sensitive,
requires certain VM sizes to use), and **Ultra Disk** (highest
performance, configurable IOPS/throughput independent of size, used for
the heaviest database workloads). This lesson's data disk uses
`Standard_LRS`, deliberately the cheapest option, since the point here is
learning disk attachment, not performance tuning.

### OS Disk vs Data Disk
The OS disk is created inline as part of the VM resource itself - it's
not optional, and it holds the operating system. A data disk is its own
independent top-level resource (`Microsoft.Compute/disks`) that exists
whether or not it's attached to anything, and gets attached by
referencing it in the VM's `storageProfile.dataDisks` array. This
independence matters: you can detach a data disk from one VM and reattach
it to another without losing the data, which isn't true of an OS disk.

### What an Extension Actually Is
A VM extension is a small agent Azure installs and runs on the VM after
it boots - not part of the OS image itself, but layered on afterward. The
Custom Script Extension in this lesson just runs a shell/PowerShell
command, but the same mechanism is how things like the Azure Monitor
Agent, antimalware agents, or disk encryption get installed consistently
across a fleet of VMs without anyone manually logging into each one.

## What You're Building Today
Attaching a data disk to yesterday's VM, then running a VM extension on it.

## New Bicep Concepts
- Child resources (a resource nested under another resource's name)
- `dataDisks` array on a VM's storage profile
- The `parent` property as an alternative to nested naming

## Annotated Example
```bicep
resource dataDisk 'Microsoft.Compute/disks@2024-03-02' = {
  name: 'vm-web-01-datadisk'
  location: resourceGroup().location
  properties: {
    creationData: {
      createOption: 'Empty'
    }
    diskSizeGB: 32
  }
  sku: {
    name: 'Standard_LRS'
  }
}

// Attaching it means adding a reference under the VM's storageProfile.dataDisks
// (shown here as a patch concept - in practice you add this array when you
// first declare the VM, or redeploy the VM resource with it added)

resource vmExtension 'Microsoft.Compute/virtualMachines/extensions@2024-07-01' = {
  parent: vm
  name: 'CustomScript'
  location: resourceGroup().location
  properties: {
    publisher: 'Microsoft.Azure.Extensions'
    type: 'CustomScript'
    typeHandlerVersion: '2.1'
    autoUpgradeMinorVersion: true
    settings: {
      commandToExecute: 'echo hello from the extension'
    }
  }
}
```

## Why It's Written This Way
- `parent: vm` is the modern way to write a child resource - it tells
  Bicep "this resource lives underneath the `vm` resource," and Bicep
  handles building the correct nested resource name for you. The older
  style writes the full slash-separated name by hand
  (`name: '${vm.name}/CustomScript'`) - you'll see both in the wild, they
  compile to the same thing.
- `Microsoft.Compute/disks` is its own top-level resource type - a data
  disk exists independently of the VM until you actually attach it via the
  VM's `dataDisks` array. This is different from the OS disk, which is
  created inline as part of the VM.
- Extensions run arbitrary scripts against the VM after it boots. This is
  your first real taste of "infrastructure as code doing configuration,"
  not just provisioning - the same idea scales up to real config
  management tools later.

## Source
<https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines>

## Why This Matters (Business Context)
A company's monitoring agent needs to be installed identically across 200 VMs today, and on every VM anyone spins up next year. Doing that by hand means it eventually drifts - some VMs get it, some don't, and nobody notices until there's an incident with no logs. An extension baked into the deployment means every VM has it, guaranteed, the moment it exists.
