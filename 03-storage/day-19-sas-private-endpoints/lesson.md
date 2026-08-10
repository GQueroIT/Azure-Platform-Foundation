# Day 19 Lesson - SAS Tokens and Private Endpoints

Cost note: private endpoints bill a small hourly charge - delete after
testing, same day.

## What You're Building Today
Understanding SAS token generation (mostly a CLI/portal task, not a Bicep
resource) and deploying a private endpoint for the storage account.

## New Bicep Concepts
- A resource that lives OUTSIDE the storage account but references it -
  private endpoints attach to a subnet, not to the resource they protect

## Annotated Example
```bicep
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-storage'
  location: resourceGroup().location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'pe-storage-connection'
        properties: {
          privateLinkServiceId: storageAccount.id
          groupIds: [ 'blob' ]
        }
      }
    ]
  }
}
```

## Why It's Written This Way
- Notice this resource type is `Microsoft.Network/privateEndpoints`, not
  something under `Microsoft.Storage`. A private endpoint is fundamentally
  a networking object - a network interface with a private IP, sitting in
  your VNet - that happens to point at a storage account (or any
  Private Link-enabled service) via `privateLinkServiceId`.
- `groupIds: [ 'blob' ]` specifies which sub-resource of the storage
  account this endpoint connects to - a single storage account exposes
  separate sub-resources for blob, file, table, and queue, and each needs
  its own private endpoint if you want all of them privately reachable.
- SAS tokens themselves (Shared Access Signatures) aren't something you
  deploy as a Bicep resource - they're generated on demand via Azure CLI
  (`az storage container generate-sas`) or the portal, since a SAS token
  is a signed credential with an expiry, not infrastructure.

## Source
Private endpoint pattern from <https://shakeeljuancalleghani.medium.com/mastering-azure-bicep-deploy-storage-account-containers-lifecycle-management-policies-and-56d130aae48b>