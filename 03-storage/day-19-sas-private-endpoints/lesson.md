# Day 19 Lesson - SAS Tokens and Private Endpoints

## Core Concepts (Read This First)

### Service Endpoint vs Private Endpoint
This lesson builds a private endpoint, but the exam expects you to know
there's a second, older option: a **service endpoint**. A service
endpoint extends your VNet's identity to the storage account - traffic
stays on the Azure backbone instead of the public internet, but it still
travels to the storage account's *public* IP, and no private IP is
created anywhere. A **private endpoint** goes further: it creates an
actual private IP address inside your VNet that represents the storage
account, so traffic never touches a public IP at all, and it's specific
to one resource (even one sub-resource, via `groupIds`) rather than an
entire service type. Service endpoints are simpler and free; private
endpoints are more isolated and cost a small hourly charge - Microsoft's
current guidance leans toward private endpoints where the added isolation
is worth that cost.

### SAS Token Types
Not all SAS tokens are the same scope. An **Account SAS** grants access
across multiple storage services within the account (blob, file, queue,
table) at once. A **Service SAS** scopes down to one specific service
(e.g. just blob). A **User Delegation SAS** is the most secure option -
it's secured with Entra ID credentials instead of the storage account's
own access keys, so it can be revoked by revoking Entra permissions
without having to rotate the account's keys (which would break every
other SAS token issued from those keys at the same time).

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

## Why This Matters (Business Context)
A vendor needs temporary access to one specific file, not the whole storage account and not forever. A SAS token grants exactly that - scoped, time-limited access, no shared password to rotate later. A private endpoint solves a different problem: a database that should never be reachable from the public internet at all, only from inside the company's own network.
