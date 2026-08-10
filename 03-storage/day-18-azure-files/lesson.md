# Day 18 Lesson - Azure Files

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

## Source
Structure based on Microsoft.Storage nested resource conventions - see
<https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts/fileservices/shares>

## Why This Matters (Business Context)
A team needs a shared drive that multiple VMs and people can read and write to at once, the way a traditional file server would work, without standing up and patching an actual Windows file server. Azure Files is that shared drive, managed by the platform instead of by someone's on-call rotation.
