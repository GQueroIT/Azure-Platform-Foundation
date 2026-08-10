# Glossary

Every term used across the lessons so far, defined plainly. Alphabetical -
use Ctrl+F, don't read it top to bottom.

**API version** - the date-stamped version of a resource type's schema,
written after the `@` in a resource declaration (e.g.
`Microsoft.Storage/storageAccounts@2025-06-01`). Azure changes what
properties a resource type supports over time; the API version pins which
version of that schema you're using.

**ARM (Azure Resource Manager)** - the underlying service that actually
creates, updates, and deletes every resource in Azure. Bicep doesn't talk
to Azure directly - it compiles into ARM's native JSON format, which is
what actually gets sent and processed.

**Availability Zone** - a physically separate datacenter within an Azure
region, with its own power and cooling. Spreading resources across zones
means one datacenter failing doesn't take everything down.

**Bicep** - a declarative language for describing Azure resources. You
write what you want to exist; Bicep (via ARM) figures out how to make it
true. Compiles down to ARM JSON.

**Conditional Access** - an Entra ID feature that evaluates sign-in
context (location, device, risk level) and allows, blocks, or challenges
access based on rules you define. Not a Bicep-deployable resource.

**Consumption plan** - a pricing model where you're billed based on
actual usage (requests, execution time) rather than for a server sitting
there running. Container Apps and Azure Functions both support this.

**Deallocate vs. Delete** - deallocating a VM stops compute billing but
keeps the VM (and its disk) intact so you can start it again later;
deleting removes it entirely. Deallocating is what you do between study
sessions; deleting is what you do when a lab is fully done.

**Diagnostic setting** - configuration that tells a resource where to send
its logs and metrics (usually a Log Analytics workspace). Without one, a
resource's activity mostly isn't being recorded anywhere you can query.

**Entra ID** - Microsoft's identity platform (formerly Azure Active
Directory). Manages users, groups, and directory roles - a separate
system from Azure RBAC, even though both use the word "role."

**Existing (keyword)** - added after a resource declaration to reference
a resource that already exists, instead of creating a new one. Doesn't
deploy anything by itself.

**Hybrid identity** - a setup where an on-prem Active Directory and Entra
ID are synced together, so the same user account works in both places.

**Idempotent / idempotency** - running the same deployment twice produces
the same end result as running it once - it doesn't create a second copy
or error out. This is a core property of how Bicep/ARM deployments are
supposed to behave.

**Load Balancer** - distributes incoming network traffic across multiple
backend resources (usually VMs), so no single instance is a single point
of failure.

**Managed disk** - a virtual hard disk Azure manages for you (storage,
replication, encryption handled automatically), attached to a VM as its
OS disk or an extra data disk.

**Managed identity** - an identity Azure automatically manages for a
resource (like a VM or web app), so that resource can authenticate to
other Azure services without you storing a password or secret anywhere.

**Management group** - a container above subscriptions used to apply
policy or RBAC to many subscriptions at once, instead of one at a time.

**Module (Bicep)** - a way to call another `.bicep` file from within one,
so a large deployment can be split into smaller, reusable pieces.

**NSG (Network Security Group)** - a set of allow/deny rules that filters
network traffic in or out of a subnet or network interface.

**Output (Bicep)** - a value returned after a deployment finishes, often
used to pass information (like a resource ID) into the next step or
module.

**Parameter (Bicep)** - a value supplied when you deploy a Bicep file,
similar to a function argument. Lets the same file be reused for
different environments or configurations.

**Private DNS zone** - a DNS zone that only resolves within a linked
virtual network, used so internal resources can find each other by name
without that name being publicly resolvable.

**Private endpoint** - a network interface with a private IP address that
connects privately to a specific Azure service (like a storage account),
so that service is reachable only from inside your network, not the
public internet.

**RBAC (Role-Based Access Control)** - Azure's permission system for
resources - who can do what to a VM, storage account, resource group,
etc. Separate from Entra ID's directory roles.

**Redundancy (LRS / ZRS / GRS)** - how many copies of your data Azure
keeps and where. LRS = 3 copies, one datacenter. ZRS = spread across
availability zones in one region. GRS = replicated to a second region
entirely. Each step up costs more.

**Resource group** - a container that holds related Azure resources
together, usually resources that share a lifecycle (deployed and deleted
as a unit).

**Resource lock** - a setting that prevents a resource from being deleted
(`CanNotDelete`) or from being deleted or modified at all (`ReadOnly`),
regardless of who has RBAC permissions to do so.

**SAS token (Shared Access Signature)** - a signed, time-limited
credential that grants scoped access to a storage resource, without
sharing the storage account's actual keys.

**Scope (Bicep)** - where a resource or deployment actually applies -
resource group, subscription, management group, or tenant. Most
resources default to resource group scope.

**Service principal** - an identity used by an application or automated
process (rather than a human) to authenticate to Azure.

**SKU** - short for "stock keeping unit" - in Azure this almost always
means the pricing tier / size of a resource (e.g. `Standard_LRS`, `B1s`).

**SSPR (Self-Service Password Reset)** - lets users reset their own
password without contacting IT, based on pre-registered verification
methods.

**Subscription** - the billing and access-management boundary in Azure -
everything you deploy lives inside a subscription, and it's the unit most
budgets and a lot of RBAC/policy are scoped to.

**targetScope** - a Bicep declaration at the top of a file that sets what
scope the whole file deploys to (resource group, subscription,
management group, or tenant). Defaults to resource group if not set.

**Tenant** - the top-level container representing an organization's
Entra ID directory. A subscription lives inside exactly one tenant.

**VMSS (Virtual Machine Scale Set)** - a group of identical VMs managed
as one unit, able to automatically scale the number of instances up or
down.

**VNet (Virtual Network)** - an isolated network within Azure that your
resources live inside, with its own IP address range, subnets, and
routing.

**VNet peering** - a direct network connection between two VNets, routed
over Microsoft's backbone instead of the public internet.
