# Day 18 Lesson - Azure Files

## Core Concepts (Read This First)

### Azure Files vs Blob Storage
Both live under the same storage account, and it's easy to assume they're
interchangeable - they're not. **Blob storage** is object storage:
everything is addressed by a flat name/key, accessed over HTTP/HTTPS, and
has no real concept of "mounting a drive." **Azure Files** is a genuine
network file share over SMB (or NFS) - the protocol Windows/Linux already
use for shared drives - so an existing application expecting a drive
letter or a mounted path can often point at an Azure Files share with
little to no code change. That's the whole reason Azure Files exists
separately from Blob: lift-and-shift compatibility with things that
already expect a traditional file share.

## What You're Building Today
A file share inside your storage account.

## New Bicep Concepts
- Two levels of nested child resources: fileServices, then shares under that

## Annotated Example
```bicep
resource fileServices 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  name: 'default'
  parent: storageAccount
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  name: 'labshare'
  parent: fileServices
  properties: {
    shareQuota: 5   // GB
    enabledProtocols: 'SMB'
  }
}
```

## Why It's Written This Way
- Same pattern as blob lifecycle management: `fileServices` is always
  named `'default'`, since a storage account has exactly one file services
  configuration. Your actual share sits one level deeper, as a child of
  `fileServices`, not of the storage account directly - that's the
  `parent: fileServices` line, not `parent: storageAccount`.
- `shareQuota` sets the maximum size in GB - Azure Files bills for
  provisioned quota on the premium tier, or used capacity on standard,
  so this number is worth keeping small for a lab.
- `enabledProtocols: 'SMB'` is the default and what you want for basic
  Windows/Linux file share mounting. NFS is the other option, used for
  Linux-specific high-performance scenarios you won't need here.

## Service Deep Dive

### What It Can't Do
Azure Files' SMB protocol communicates over TCP port 445, and a large
number of ISPs and corporate networks block that port outbound entirely,
for historical reasons tied to old SMB 1.0 vulnerabilities - this isn't
an Azure-side limitation, but it's a very real, very common blocker for
on-prem or home-network clients trying to mount a share directly over
the internet. There's no way to change which port SMB uses; the
workarounds all avoid a direct SMB connection over the internet in the
first place (private endpoint, VPN/ExpressRoute, or Azure File Sync as a
local cache reachable over port 443).

NFS shares specifically require the Premium tier and can't use the
storage account's public endpoint at all - NFS Azure Files only works
over a private endpoint or service endpoint inside a VNet, the opposite
of SMB's default (publicly reachable unless explicitly restricted). A
file share's quota is a ceiling, not a reservation on Standard tier -
`shareQuota: 5` caps the share at 5 GB, but billing follows actual usage,
not the quota; Premium tier is the opposite, provisioning and billing
for the full quota upfront regardless of actual usage.

### Nuances Worth Knowing
- The standard diagnosis path for "can't mount, works from an Azure VM
  but not from home" is almost always port 445, not credentials or share
  config - the practical first test is a direct TCP connection check
  (`Test-NetConnection -Port 445` or `nc -zv ... 445`) before touching
  anything else.
- Entra ID Kerberos authentication for SMB is a two-layer permission
  model, not one - it needs both a share-level RBAC role assignment (in
  Azure) and correct NTFS folder-level ACLs (set from within Windows).
  Missing either layer blocks access even when the other is perfectly
  configured, and the resulting error doesn't clearly say which layer is
  the problem.
- Standard file shares don't provision performance the way Premium
  does - Premium performance scales directly with the quota set (bigger
  provisioned quota = more IOPS/throughput), so undersizing quota on
  Premium isn't just a capacity risk, it's a performance ceiling too.

### Troubleshooting You'll Actually Hit
- **Error:** "System error 53" or "System error 67" when mounting from
  an on-prem machine -> **Cause:** port 445 is blocked somewhere between
  the client and Azure - an ISP or corporate firewall, not an Azure-side
  failure -> **Fix:** confirm with a direct port test first; if 445 is
  genuinely blocked and can't be opened, route through a private
  endpoint + VPN/ExpressRoute, or use Azure File Sync as a local
  port-443 workaround instead of forcing a direct SMB mount.
- **Symptom:** a user has the correct share-level RBAC role but still
  can't access specific folders -> **Cause:** Entra Kerberos auth needs
  matching NTFS ACLs set from Windows in addition to the RBAC role ->
  **Fix:** verify both the Azure-side role assignment and the
  Windows-side NTFS permissions on the specific folder, not just one or
  the other.
- **Symptom:** connecting works fine from an Azure VM in the same region
  but fails from anywhere else -> **Cause:** consistent with a port-445
  block specific to the client's network -> **Fix:** same as above -
  this pattern (works from Azure, fails externally) is close to a
  diagnostic signature for the port-445 case specifically.

*Checked against: Microsoft Learn's "Troubleshoot Azure Files SMB
connectivity and access issues" doc and Azure Files networking training
material.*


## Source
Structure based on Microsoft.Storage nested resource conventions - see
<https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts/fileservices/shares>

## Why This Matters (Business Context)
A team needs a shared drive that multiple VMs and people can read and write to at once, the way a traditional file server would work, without standing up and patching an actual Windows file server. Azure Files is that shared drive, managed by the platform instead of by someone's on-call rotation.
