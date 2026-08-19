# Day 06b Lesson - VM Lifecycle - Encryption at Host and Moving VMs

## Core Concepts (Read This First)

### Encryption at Host vs Azure Disk Encryption
Two different things with confusingly similar names. **Azure Disk
Encryption** (ADE) is guest-level - it runs BitLocker (Windows) or
DM-Crypt (Linux) inside the VM's OS, using Key Vault to manage the keys.
**Encryption at host** is platform-level - it encrypts the VM's disks
(and the temp/cache disk, which ADE doesn't touch) at the Azure storage
layer itself, outside the guest OS entirely. They're mutually exclusive
on the same VM - encryption at host can't be enabled if ADE is already
active, and vice versa. For most new builds, encryption at host is the
simpler, Microsoft-recommended default, since it needs no in-guest agent
and covers the temp disk ADE misses.

### Moving a VM Isn't Always a Clean Operation
Moving a resource to another resource group, subscription, or region
looks like one generic operation, but VMs have real, named exceptions.
A VM using Azure Disk Encryption can move resource groups only while
deallocated, and can't move subscriptions at all without disabling
encryption first. A VM created from a Marketplace image with a plan
attached can't move subscriptions either - the workaround is
deprovisioning and redeploying fresh in the target subscription, not an
actual move. None of this is a Bicep concern - moving is a CLI/PowerShell/
Portal action against an already-deployed resource, not something you
declare in a template.

## What You're Building Today
Redeploying Day 04's VM with `encryptionAtHost` enabled, and practicing
the resource-move workflow on a throwaway resource.

## New Bicep Concepts
- `securityProfile.encryptionAtHost` - a boolean on the VM resource, not
  a separate resource type
- Feature registration required before this property is usable at all

## Annotated Example
```bicep
resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: 'vm-web-01'
  location: resourceGroup().location
  zones: [ '1' ]
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_DS1_v2'   // must support EncryptionAtHostSupported
    }
    securityProfile: {
      encryptionAtHost: true
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
        managedDisk: { storageAccountType: 'Standard_LRS' }
      }
    }
    networkProfile: {
      networkInterfaces: [ { id: nic.id } ]
    }
  }
}
```

## Why It's Written This Way
- `encryptionAtHost` sits under `securityProfile`, a sibling to
  `hardwareProfile` and `osProfile` - easy to reach for the wrong parent
  object the first time.
- `Standard_B1s` (Day 04's size) doesn't support encryption at host - the
  example switches to `Standard_DS1_v2` specifically because it does.
  Not every VM size supports this property, and Azure won't warn you at
  the Bicep-syntax level - it fails at deployment time instead.
- This property can only be set at VM creation in this repo's flow;
  enabling it on an already-deployed VM is a separate deallocate/update/
  reallocate operation, not a redeploy of this same file.

## Service Deep Dive

### What It Can't Do
Encryption at host isn't usable by default - the `Microsoft.Compute/
EncryptionAtHost` feature has to be registered on the subscription first
(`Register-AzProviderFeature` or the CLI equivalent), and deployments
against an unregistered subscription fail with a clear but easy-to-miss
error naming the exact feature. Legacy VM sizes don't support it at all,
and checking support isn't guesswork - the Resource SKUs API reports an
explicit `EncryptionAtHostSupported` capability per size, which is the
authoritative way to check before picking a size, not trial and error.

Moving VMs has its own hard boundaries: Scale Sets using a Standard SKU
Load Balancer or Standard SKU public IP can't be moved at all. VMs using
scheduled patching can't move resource groups or subscriptions either,
full stop, with maintenance configurations as the only real workaround.

### Nuances Worth Knowing
- Existing VMs must be deallocated and reallocated to actually pick up
  encryption at host - flipping the setting doesn't encrypt anything
  retroactively while the VM keeps running.
- Disabling encryption at host later requires the same deallocate-first
  step, and for a VMSS, disabling only affects instances created *after*
  the change - existing instances need to be individually deallocated,
  updated, and reallocated to actually lose the setting.
- Moving a VM that's part of a VNet only succeeds if the VNet and its
  dependencies move along with it - you can't move a VM alone out of a
  VNet it belongs to into a different subscription.

### Troubleshooting You'll Actually Hit
- **Error:** `The property 'securityProfile.encryptionAtHost' is not
  valid because the 'Microsoft.Compute/EncryptionAtHost' feature is not
  enabled for this subscription` -> **Cause:** the feature was never
  registered on the subscription -> **Fix:**
  `Register-AzProviderFeature -FeatureName "EncryptionAtHost" -ProviderNamespace "Microsoft.Compute"`,
  then wait for registration to complete before redeploying.
- **Symptom:** a move operation fails with no obvious reason tied to
  encryption or Marketplace plans -> **Cause:** one of the other named
  exceptions - scheduled patching, a Standard SKU Load Balancer/public IP
  on a scale set, or a dependent resource not moving alongside the VM ->
  **Fix:** check the specific move-limitations list for VMs before
  assuming a generic move will work; several categories need a documented
  workaround rather than a standard move.
- **Symptom:** encryption at host is enabled in Bicep but a VM created
  from the same template still isn't encrypted -> **Cause:** the chosen
  VM size doesn't support the feature -> **Fix:** confirm
  `EncryptionAtHostSupported: True` for the size via the Resource SKUs
  API before deploying, not after.

*Checked against: Microsoft Learn's "Special cases to move Azure VMs"
and "Enable end-to-end encryption using encryption at host" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/virtual-machines/disks-enable-host-based-encryption-portal>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-limitations/virtual-machines-move-limitations>

## Why This Matters (Business Context)
A compliance auditor asks whether data on a VM's temp disk - the one nobody thinks about - is encrypted at rest, and the honest answer for a VM using only guest-level BitLocker is no. Encryption at host closes that exact gap, at the platform level, without touching the guest OS at all.
