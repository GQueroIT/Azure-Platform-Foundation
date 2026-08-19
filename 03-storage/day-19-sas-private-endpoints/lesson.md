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

## Service Deep Dive

### What It Can't Do
Creating a private endpoint doesn't automatically disable the storage
account's public endpoint - those are two separate settings. Deploying a
private endpoint and leaving public network access enabled leaves the
resource reachable both ways at once, which defeats the isolation goal
if the intent was "private only." A private endpoint also doesn't make
DNS resolve correctly by itself - creating it creates a private IP, but
nothing automatically points client DNS lookups at it; that requires a
Private DNS Zone actually linked to the VNet the client sits in.

A SAS token can't be selectively revoked once issued unless it was built
around a stored access policy - a SAS generated directly against account
keys is valid until it expires, full stop; the only way to kill it early
is rotating the account keys themselves, which invalidates every other
SAS issued from those same keys at the same time, not just the one meant
to be revoked.

### Nuances Worth Knowing
- The single most common private endpoint failure isn't actually a
  private-endpoint problem, it's DNS - and it typically shows up as a
  403 "This TCP connection does not allow access" error from the
  resource's firewall, because the client resolved the *public* hostname,
  connected over the public endpoint, and got rejected by the exact
  firewall rule the private endpoint was supposed to make irrelevant.
- If a VNet uses custom DNS servers instead of Azure-provided DNS,
  linking the Private DNS Zone to the VNet isn't enough by itself - the
  custom DNS server also has to forward `privatelink.*` queries
  specifically to Azure's DNS resolver (168.63.129.16), or it never even
  asks Azure DNS about the private zone.
- A private endpoint connection can sit in a Pending state even after
  setup looks complete - this happens for cross-subscription or
  cross-tenant connections, where the resource owner has to manually
  approve the connection before any traffic flows.
- User Delegation SAS tokens are capped at a maximum lifetime of 7 days
  when re-authentication isn't required within that window - unlike
  Account or Service SAS, which can be issued with much longer
  expirations.

### Troubleshooting You'll Actually Hit
- **Error:** "403 - This TCP connection does not allow access to {host}"
  on a resource with a private endpoint configured -> **Cause:** almost
  always DNS resolving the public hostname to the public IP instead of
  the private endpoint's IP, so the firewall rejects the connection as
  if the private endpoint didn't exist -> **Fix:** `nslookup` the
  hostname from a VM inside the VNet - if it returns a public IP, check
  the Private DNS Zone is linked to that specific VNet, and if custom
  DNS is in play, confirm it forwards `privatelink.*` queries to Azure
  DNS.
- **Symptom:** a private endpoint was created and everything else looks
  correct, but traffic doesn't flow -> **Cause:** the connection is
  sitting Pending, which happens by design for cross-subscription/
  cross-tenant private endpoints until the resource owner approves it ->
  **Fix:** check the connection's status on the target resource itself
  and approve it if Pending.
- **Symptom:** DNS resolves to the private IP on one attempt and the
  public IP on the next, intermittently -> **Cause:** commonly multiple
  DNS paths in play at once (a custom forwarder alongside Azure-provided
  DNS, or stale caching from before the zone was linked) -> **Fix:**
  flush the client's DNS cache, and confirm there's exactly one
  consistent resolution path rather than a mix of custom and
  Azure-provided DNS.

*Checked against: Microsoft Learn's "Troubleshoot private endpoint DNS
resolution failure" and "Troubleshoot 403 access denied errors ...
through an approved private endpoint" docs.*


## Source
Private endpoint pattern from <https://shakeeljuancalleghani.medium.com/mastering-azure-bicep-deploy-storage-account-containers-lifecycle-management-policies-and-56d130aae48b>

## Why This Matters (Business Context)
A vendor needs temporary access to one specific file, not the whole storage account and not forever. A SAS token grants exactly that - scoped, time-limited access, no shared password to rotate later. A private endpoint solves a different problem: a database that should never be reachable from the public internet at all, only from inside the company's own network.
