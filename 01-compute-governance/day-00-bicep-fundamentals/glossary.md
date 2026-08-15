# Glossary - Azure-Platform-Foundation

Every term used across all 6 phases of this repo, in one place. If a
lesson uses a word you haven't seen defined yet, check here before
searching outside the repo. Organized alphabetically.

## A

**Action Group** - a reusable set of notification/response targets
(email, SMS, webhook, Azure Function, etc) that alerts and budgets point
at, instead of each one defining its own contact list from scratch.

**Actions / notActions** - the two arrays inside a custom RBAC role
definition. `actions` is an allow-list of specific operations (not full
role names). `notActions` carves exceptions out of what `actions` already
granted - it's subtractive, not a separate restriction.

**Alert (metric alert)** - a rule that watches a metric (CPU, response
time, queue length) against a threshold and fires when it's crossed,
usually pointed at an Action Group to decide what happens next.

**Assignable Scopes** - the list on a custom role definition controlling
where that role is allowed to be assigned (a specific resource group, a
subscription, a management group) - not who can receive it, not what
regions it works in.

**Availability Set** - a logical grouping of VMs within a single Azure
datacenter, spread across separate update/fault domains so one hardware
failure or planned maintenance event doesn't take out every VM at once.
Protects against failures inside one datacenter. Compare Availability
Zone.

**Availability Zone** - a physically separate datacenter within an Azure
region, with independent power, cooling, and networking. Spreading VMs
across zones protects against an entire datacenter going down, not just a
single rack. Not every region supports zones.

**Azure Arc** - a service that extends Azure management (policy,
monitoring, tagging) to machines that aren't actually running in Azure -
on-prem servers, other clouds - by installing an agent that registers
them as an Azure resource.

**Azure Bastion** - a managed service that provides RDP/SSH access to VMs
through the Azure portal, without exposing a public RDP/SSH port on the
VM itself. Bills hourly with no pause button.

**Azure Files** - a fully managed file share service, accessible over
SMB/NFS, functioning like a network drive rather than object storage
(compare Blob storage).

**Azure Monitor** - the umbrella platform for collecting metrics, logs,
and alerts across Azure resources. Log Analytics workspaces, alerts, and
diagnostic settings all feed into or are managed under Azure Monitor.

**Azure Policy** - Azure's compliance system: independent of RBAC,
answers "does this comply with the rules?" rather than "is this person
allowed?" See Policy Definition, Policy Assignment, Initiative, Policy
Effect.

## B

**Blob lifecycle management** - a policy on a storage account that
automatically moves blobs between access tiers (Hot/Cool/Archive) or
deletes them based on age, without manual cleanup.

**Budget** - a cost-tracking resource that fires a notification when
spend crosses a threshold. Does NOT stop spending or block deployments by
default - it's an alert, not a cap.

## C

**Conditional Access** - an Entra ID feature that enforces access rules
(require MFA, block legacy auth, require a compliant device) based on
signals like user, location, or device - separate from RBAC, which
governs what you can do once you're in.

**Container App / Container Apps Environment** - a managed service for
running containers without managing the underlying infrastructure,
including the ability to scale to zero (and stop billing) when there's no
traffic. The Environment is the shared boundary multiple Container Apps
can run inside.

**Custom Role** - an RBAC role you define yourself (as opposed to a
built-in role like Contributor), built from `actions`, `notActions`, and
`assignableScopes`.

## D

**Data disk** - an independent, attachable storage resource
(`Microsoft.Compute/disks`) separate from a VM's OS disk. Exists whether
or not it's currently attached, and can be detached and reattached
elsewhere without losing data.

**Decorator** - a line starting with `@` placed above a Bicep `param`
that constrains or annotates it (`@secure()`, `@description()`,
`@allowed()`, `@minLength()`/`@maxLength()`, `@minValue()`/`@maxValue()`).

**Dependency (implicit / explicit)** - how Bicep knows what order to
deploy resources in. Implicit: referencing another resource's property
(like `.id`) automatically creates the dependency. Explicit: `dependsOn`,
used only when there's no property link to create it for free.

**Diagnostic setting** - configuration on an Azure resource that routes
its logs/metrics to a destination - most often a Log Analytics workspace.

## E

**Entra ID** - Microsoft's identity platform (formerly Azure Active
Directory). Manages users, groups, and directory roles - a separate
permission system from Azure RBAC. See RBAC vs Entra roles.

**Existing (keyword)** - marks a Bicep resource as a reference to
something already deployed, rather than something to create. Doesn't
provision anything; just lets the file read properties or attach new
resources to it.

**Extension (Bicep)** - the `extension` directive that loads a capability
Bicep doesn't have natively, most notably `extension microsoftGraphV1`,
which unlocks `Microsoft.Graph/*` resource types for managing Entra ID
resources.

**Extension (VM)** - a small agent Azure installs and runs on a VM after
it boots - not part of the OS image, layered on afterward (e.g. Custom
Script Extension, Azure Monitor Agent).

## F

**Fault domain** - a group of hardware (rack, power source) within a
single datacenter that could fail together. Availability Sets spread VMs
across fault domains.

**Flexible orchestration (VMSS)** - the current Microsoft-recommended
mode for VM Scale Sets, where each instance behaves like a standalone VM
(usable with normal VM APIs, Backup, tagging) while still getting
scale-set-level autoscaling and zone-spreading. Compare Uniform
orchestration.

## G

**guid() function** - a Bicep function that generates a deterministic
GUID from its inputs - same inputs, same output every time, which is why
it's used for role assignment names (so redeploying the same assignment
doesn't try to create a duplicate).

## H

**Hybrid identity** - the general concept of connecting an on-prem
Active Directory to Entra ID, so the same identity works in both places.
Password hash sync, pass-through authentication, and federation are the
three main methods.

## I

**Initiative (policy set)** - a bundle of multiple policy definitions
assigned together in one assignment, instead of one definition at a time
- typically used to represent a whole compliance standard.

## L

**Load Balancer** - distributes network traffic across backend VMs/
instances at Layer 4 (TCP/UDP - IP and port only, no awareness of HTTP
content). Compare Application Gateway, which operates at Layer 7.

**Log Analytics workspace** - the storage/query destination for logs and
metrics collected by Azure Monitor. Diagnostic settings and agents send
data here; you query it with KQL (Kusto Query Language).

## M

**Management group** - a container that sits above subscriptions, purely
for governance (RBAC and Policy inheritance) - not billing. See Tenant
Root Group.

**Module (Bicep)** - a way to call another `.bicep` file from within one,
used to split large deployments into reusable pieces or to deploy across
scope boundaries (e.g. a resource-group-scoped file deploying a module at
tenant scope).

## N

**Network Security Group (NSG)** - a set of allow/deny rules
(`securityRules`) applied to a subnet or NIC, evaluated in priority order
(lowest number first, first match wins).

**Network Watcher** - a diagnostic and monitoring service for Azure
networking (connection troubleshooting, packet capture, topology views).

## O

**Orchestration mode (VMSS)** - the deployment model a VM Scale Set uses,
set once at creation and unable to be changed afterward. See Uniform
orchestration, Flexible orchestration.

**OS disk** - the disk holding the operating system, created inline as
part of the VM resource itself - not optional, not a separate top-level
resource the way a data disk is.

## P

**Parameter (param)** - a Bicep input value supplied at deployment time,
the Bicep equivalent of a function argument.

**Parent / child resource** - a resource that only makes sense nested
under another (a role assignment under a role definition's scope, a
backup policy under a vault). Written either with the `parent:` property
or a manually slash-separated name - both compile to the same thing.

**Peering (VNet)** - a direct connection between two VNets over
Microsoft's backbone rather than the public internet. One-directional per
resource - two VNets need two peering resources, one on each side.

**Policy assignment** - turning a policy definition on at a specific
scope, optionally with parameters.

**Policy definition** - the rule itself: the logic describing what to
check and what to do about it (see Policy Effect). Azure ships hundreds
of built-in definitions.

**Policy effect** - what happens when a resource doesn't comply with a
policy: Deny (blocks the deployment), Audit (flags it as non-compliant,
still deploys), Append (adds a field/value automatically), Modify (alters
existing resource properties, often tags), DeployIfNotExists
(auto-deploys a companion resource if one is missing).

**Principal / principalId / principalType** - the identity (`principal`)
being granted a role, its unique ID (`principalId`), and what kind of
identity it is - User, Group, or ServicePrincipal (`principalType`).
Getting `principalType` wrong can make an assignment silently not work.

**Private DNS zone** - a DNS zone resolvable only from within a
connected VNet, letting internal resources find each other by name
instead of hardcoded IPs.

**Private endpoint** - a network interface with a private IP that
connects privately to a specific Azure service, so that service is
reachable only from inside your network, not the public internet.

## R

**RBAC (Role-Based Access Control)** - Azure's permission system for
resources: who can do what to a VM, storage account, resource group,
etc. Separate from Entra ID's directory roles. RBAC is additive:
permissions from every role assigned across every applicable scope
combine, they don't override each other.

**Recovery Services vault** - the container resource for Azure Backup
and Site Recovery configuration - holds backup policies and tracks
protected items.

**Redundancy (LRS / ZRS / GRS)** - how many copies of storage data Azure
keeps and where. LRS = 3 copies, one datacenter. ZRS = spread across
availability zones in one region. GRS = replicated to a second region
entirely. Each step up costs more.

**Resource group** - a container that holds related Azure resources
together, usually resources that share a lifecycle (deployed and deleted
as a unit).

**Resource lock** - a setting that prevents a resource from being deleted
(`CanNotDelete`) or deleted/modified at all (`ReadOnly`), regardless of
what RBAC role the person acting has. Locks override RBAC on purpose, and
inherit downward from resource group to everything inside it.

**Role assignment** - the act of granting a specific role (built-in or
custom) to a specific principal at a specific scope.

**Role definition** - the role itself, either built-in (Contributor,
Reader, Owner) or custom, describing what actions it permits.

## S

**SAS token (Shared Access Signature)** - a signed, time-limited
credential that grants scoped access to a storage resource, without
sharing the storage account's actual keys.

**Scope (Bicep)** - where a resource or deployment actually applies -
resource group, subscription, management group, or tenant. Most
resources default to resource group scope. Set per-file with
`targetScope`, or overridden per-resource with the `scope` property.

**Security group (Entra)** - a group object in Entra ID used to collect
users for access assignment (RBAC or Entra roles), as opposed to a
Microsoft 365 group.

**Self-Service Password Reset (SSPR)** - lets users reset their own
password without contacting IT, based on pre-registered verification
methods.

**Service principal** - an identity used by an application or automated
process (rather than a human) to authenticate to Azure.

**SKU** - short for "stock keeping unit" - in Azure this almost always
means the pricing tier / size of a resource (e.g. `Standard_LRS`,
`B1s`).

**Standard vs Premium disk** - Standard (HDD or SSD) is cheaper, lower
performance. Premium SSD is the default for performance-sensitive
workloads and requires certain VM sizes. Ultra Disk sits above Premium
for the heaviest, most configurable workloads.

**Subscription** - the billing and access-management boundary in Azure -
everything you deploy lives inside a subscription, and it's the unit
most budgets and a lot of RBAC/policy are scoped to.

## T

**targetScope** - a Bicep declaration at the top of a file that sets what
scope the whole file deploys to (resource group, subscription,
management group, or tenant). Defaults to resource group if not set.

**Tenant** - the top-level container representing an organization's
Entra ID directory. A subscription lives inside exactly one tenant.

**Tenant Root Group** - the single management group automatically created
at the top of every tenant's hierarchy. Cannot be deleted or moved; its
ID is the same as the tenant ID. Every subscription lands here by default
unless moved under a custom management group.

## U

**Uniform orchestration (VMSS)** - the older VM Scale Set mode where
every instance is identical and managed through the scale set's own API
rather than standard VM APIs. Compare Flexible orchestration, now the
Microsoft-recommended default for new scale sets.

**Update Management** - patch scheduling and compliance tracking for
VMs and Arc-connected machines, configured through Azure Update Manager
once a machine is onboarded.

**Upgrade policy (VMSS)** - controls whether changing a scale set's VM
model automatically starts replacing running instances (`Automatic`) or
waits for you to trigger it (`Manual`).

## V

**Variable (var)** - a Bicep value computed inside the file itself, not
passed in at deployment time (compare `param`).

**VM Scale Set (VMSS)** - a group of VM instances managed as one unit,
able to scale the instance count up or down, either manually or via
autoscale rules.

**VNet (Virtual Network)** - an isolated network within Azure that your
resources live inside, with its own IP address range, subnets, and
routing.

**VNet peering** - see Peering (VNet).

## W

**What-if** - `az deployment group what-if` (or the sub/mg/tenant
equivalents) - previews exactly what a deployment would create, change,
or delete before it actually runs, without making any changes.
