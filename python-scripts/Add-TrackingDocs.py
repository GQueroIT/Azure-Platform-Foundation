#!/usr/bin/env python3
"""
Creates three repo-root reference docs: GLOSSARY.md, COST-LOG.md, and
TROUBLESHOOTING.md.

GLOSSARY.md is pre-filled with every term used across the lessons so far,
defined plainly - this is reference content, not experiential, so it's
written now rather than left blank.

COST-LOG.md and TROUBLESHOOTING.md are templates you fill in as you
actually work - real spend and real errors, not something that can be
pre-written honestly.

Assumes it lives one folder below the repo root, same as the other
scripts in python-scripts/.
"""

from pathlib import Path

base_path = Path(__file__).resolve().parent.parent

glossary = """# Glossary

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
"""

cost_log = """# Cost Log

Real spend, logged after each session. Not an estimate - what the
subscription actually shows. Check Cost Management + Billing in the
portal, or `az consumption usage list`, and record what you find.

This becomes a real artifact you can point to: "built and tore down the
full AZ-104 hands-on build for $X total" is a concrete, specific claim
that means something in an interview. A vague "I did some Azure labs"
doesn't.

## Log

| Date | Day | What Ran | Deallocated/Deleted? | Cost This Session | Running Total |
|------|-----|----------|----------------------|--------------------|----------------|
|      |     |          |                       |                    |                |

## Notes
- Log every session, even a $0.00 one - the pattern matters as much as
  the number.
- If a number looks wrong (way higher than expected), that's worth
  investigating immediately, not just recording. See TROUBLESHOOTING.md.
- Week 3 (Networking, Days 11-15) is the week most likely to spike this
  log - Bastion and VPN Gateway bill hourly with no "pause" option.
"""

troubleshooting = """# Troubleshooting Log

Real errors you actually hit, and what fixed them. Don't pre-fill this -
it's only useful if it's true.

## How to Read an Azure Error (general, applies everywhere)
Azure CLI and deployment errors almost always follow the same shape:
a `code` (a short category, like `InvalidTemplateDeployment` or
`ResourceNotFound`) and a `message` (a plain-English explanation, usually
telling you exactly what's wrong). Read the full `message` before
searching anything online - it's more specific to your actual situation
than a generic search result will be.

If a deployment fails with a generic top-level error, look for an
`inner error` or run `az deployment operation group list` against that
deployment name - the real cause is often one level deeper than the
first message shown.

Common categories worth recognizing on sight:
- **Naming conflicts** - something with that name already exists, often
  globally (storage accounts, App Service names)
- **Quota/permission errors** - your subscription doesn't allow that VM
  size/region, or your account lacks a specific permission
- **Schema errors** - a property that doesn't exist on that resource
  type, or is spelled/cased wrong
- **Dependency errors** - something referenced (a subnet, a role
  definition) doesn't exist yet or isn't in the state your Bicep assumes

## Log

| Date | Day | Error Message (short) | What I Tried | What Fixed It | Root Cause |
|------|-----|------------------------|---------------|-----------------|--------------|
|      |     |                        |               |                 |              |

By week 3-4 this table is genuinely one of the more valuable things in
this repo - it's proof of real hands-on struggle, not just clean
successes, and it's exactly the kind of detail that makes a portfolio
believable.
"""

files_to_create = {
    "GLOSSARY.md": glossary,
    "COST-LOG.md": cost_log,
    "TROUBLESHOOTING.md": troubleshooting,
}

for filename, content in files_to_create.items():
    file_path = base_path / filename
    if file_path.exists():
        print(f"{filename} already exists - left it alone")
        continue
    file_path.write_text(content, encoding="utf-8")
    print(f"{filename} created")

# Point to them from the root README
readme_file = base_path / "README.md"
if readme_file.exists():
    text = readme_file.read_text(encoding="utf-8")
    old_learning = """## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from, and `assets/validation-guide.md` for
how to check your Bicep before deploying it. Every lesson also ends with a
"Why This Matters" section tying that day's work to a real business
reason - it's worth reading even after you've built the lab."""

    new_learning = """## Learning Resources
See `bicep-study-resources.md` at the repo root for every source the lesson
content in this repo is drawn from, and `assets/validation-guide.md` for
how to check your Bicep before deploying it. Every lesson also ends with a
"Why This Matters" section tying that day's work to a real business
reason - it's worth reading even after you've built the lab.

Also at the repo root: `GLOSSARY.md` for any term you hit that isn't
explained inline, `COST-LOG.md` to track real spend session by session,
and `TROUBLESHOOTING.md` to log real errors and what fixed them."""

    if old_learning in text and "GLOSSARY.md" not in text:
        text = text.replace(old_learning, new_learning)
        readme_file.write_text(text, encoding="utf-8")
        print("Root README updated to link the new docs")
    elif "GLOSSARY.md" in text:
        print("README already links the new docs")

print()
print("Done.")