#!/usr/bin/env python3
"""
Adds 11 new day folders covering AZ-104 skills-measured objectives that the
original 30-day plan didn't reach: ACR/ACI, App Service certs/custom domain/
backup/VNet integration, VM encryption at host + move, public Azure DNS,
UDRs + ASGs, Storage Explorer/AzCopy + object replication + versioning,
Entra licenses + external users, tags + Advisor, Connection Monitor + alert
processing rules, Backup vault (distinct from Recovery Services vault), and
Site Recovery.

Every new day follows the exact same three-file structure as the original
30 days - lesson.md (Core Concepts -> Bicep example -> Service Deep Dive ->
Source -> Business Context), lab.md (the same Objective/Steps/Verification/
Issues/Takeaways/Cost Note template), and a blank solution.bicep placeholder
- so nothing about the workflow this repo already uses has to change to
absorb them. New days use the same "day-NNb"/"day-NNc" suffix pattern this
repo already established with 01b-app-hosting, inserted next to the existing
day their objective is closest to, rather than renumbering anything after
Day 30.

Content for each day was researched against Microsoft Learn before being
written - see the Source section at the end of each lesson.md for what to
go re-read.

Safe to re-run: skips any day folder that already has a lesson.md, so it
never overwrites real work.

WHERE THIS SCRIPT LIVES: one folder below the repo root (python-scripts/),
matching every other script in this toolchain. This file is fully
self-contained - the day content lives in this same file, not a
separate module - so there's nothing else to download or keep next to it.
"""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if not (REPO_ROOT / "README.md").exists():
    print(f"ERROR: expected repo root at {REPO_ROOT} but no README.md found there.")
    print("This script must live in python-scripts/, one level below the repo root.")
    sys.exit(1)

# --- GAP_DAYS content below, merged in directly so this is a single,
# self-contained file with no second file to keep track of ---

# Content module for Add-ExamGapLabs.py - one entry per new day.
# Each entry: phase folder, day slug, title, lab objective, bicep objective,
# and the full lesson.md body (everything after the H1 title line).

GAP_DAYS = [

    # ============================================================
    # 01-compute-governance
    # ============================================================
    {
        "phase": "01-compute-governance",
        "slug": "day-06b-vm-lifecycle-encryption",
        "title": "VM Lifecycle - Encryption at Host and Moving VMs",
        "lab_objective": "Enable encryption at host on a VM through the Portal, and move a resource "
            "into a different resource group. Maps to the Compute domain.",
        "bicep_objective": "Write Bicep that deploys a VM with encryptionAtHost enabled from the start. "
            "Moving a VM is a CLI/PowerShell/Portal operation, not something you deploy - document "
            "the move command instead of writing Bicep for it.",
        "lesson": '''## Core Concepts (Read This First)

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
A compliance auditor asks whether data on a VM's temp disk - the one nobody thinks about - is encrypted at rest, and the honest answer for a VM using only guest-level BitLocker is no. Encryption at host closes that exact gap, at the platform level, without touching the guest OS at all.''',
    },

    {
        "phase": "01-compute-governance",
        "slug": "day-03b-tags-advisor-cost",
        "title": "Tags, Azure Advisor, and Deeper Cost Management",
        "lab_objective": "Apply tags to a resource group and its resources through the Portal, and "
            "review Azure Advisor's current recommendations for the subscription. Maps to the "
            "Identities and Governance domain.",
        "bicep_objective": "Write Bicep that applies a consistent tag object to a resource group "
            "and a resource deployed inside it.",
        "lesson": '''## Core Concepts (Read This First)

### Tags Don't Inherit - a Real, Common Mistake
Tagging a resource group `Environment: Production` does not tag the
resources inside it. Tags are metadata attached to one specific resource,
resource group, or subscription at a time - there's no automatic
flow-down the way RBAC or Policy inherit. The only way to get
inheritance-like behavior is Azure Policy with a `modify` effect copying
the parent's tag onto children as they're created - a policy doing the
work, not a native tag feature.

### Advisor Is Free and Already Running
Azure Advisor isn't something you deploy - it's a built-in recommendation
engine continuously scanning the subscription across four categories
(Cost, Security, Reliability, Performance) and surfacing specific,
actionable findings, like a VM sitting at 3% CPU that should be
downsized. There's no Bicep resource for "Advisor" itself; the lab today
is reviewing what it's already found, not building anything.

## What You're Building Today
A tag object applied consistently to a resource group and a resource
inside it, plus a review of Advisor's current recommendations.

## New Bicep Concepts
- `tags` as a property available on nearly every resource type
- Deploying a `Microsoft.Resources/tags` resource to tag a subscription
  or resource group itself, not just individual resources

## Annotated Example
```bicep
param tags object = {
  Environment: 'Lab'
  Project: 'AZ-104-Prep'
  Owner: 'gabe'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: 'stg${uniqueString(resourceGroup().id)}'
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  tags: tags
}
```

Tagging the resource group itself (a subscription-scoped file):
```bicep
targetScope = 'subscription'

param tags object = {
  Environment: 'Lab'
  Project: 'AZ-104-Prep'
}

resource applyTags 'Microsoft.Resources/tags@2021-04-01' = {
  scope: resourceGroup('rg-lab')
  name: 'default'
  properties: { tags: tags }
}
```

## Why It's Written This Way
- Passing the same `tags` object into every resource keeps tagging
  consistent without retyping key-value pairs on each one - the pattern
  scales the moment a deployment has more than one or two resources.
- Tags applied through Bicep **replace** whatever tags already exist on
  that resource, not merge with them - if a resource already has manual
  tags and you deploy without including them in the object, they're
  gone, not preserved.
- The `Microsoft.Resources/tags` resource's `name` is always literally
  `'default'` - same pattern as the lifecycle policy and file services
  resources from Storage week, one tag document per scope.

## Service Deep Dive

### What It Can't Do
Every resource, resource group, and subscription is capped at 50 tag
name-value pairs - hit the limit and the workaround is folding multiple
values into one tag's value as a JSON string, not requesting a higher
cap. Classic resources (like Cloud Services) don't support tags at all,
and a handful of resource types - Azure IP Groups and Firewall Policies
among them - don't support the PATCH operations tags normally use,
meaning those specific resource types need their own update commands to
change tags rather than the generic tag-update path.

Advisor also can't act on your behalf - it only recommends. Downsizing
that underutilized VM, tightening that open NSG rule, or right-sizing
that storage account is still a manual (or separately automated) action
after Advisor points it out.

### Nuances Worth Knowing
- Tag names are case-insensitive but tag values are case-preserving and
  case-sensitive - `environment: prod` and `Environment: Prod` collide
  on the name but are treated as different values, a real source of
  fragmented cost reports when a team isn't consistent about casing.
- Storage accounts specifically cap tag *names* at 128 characters instead
  of the usual 512 - one of several resource-type-specific exceptions to
  the general tag limits.
- "Hidden tags" (any tag name starting with `hidden-`) don't show up in
  the portal's Tags UI at all, but still exist in the resource's metadata
  and are queryable - a real, if obscure, pattern for metadata that
  shouldn't clutter the normal tagging view.
- Azure Policy can enforce tag inheritance from a resource group down to
  its resources using a `modify` effect - this is the actual mechanism
  behind "inherited tags," not a native tag behavior.

### Troubleshooting You'll Actually Hit
- **Symptom:** a resource group is tagged correctly but cost reports
  filtered by that tag show nothing for the resources inside it ->
  **Cause:** tags don't inherit automatically - the resources themselves
  were never actually tagged -> **Fix:** tag resources directly, or
  assign a tag-inheritance Azure Policy scoped to the resource group so
  new resources pick up the parent tag going forward.
- **Symptom:** redeploying a Bicep file wipes out tags someone added
  manually in the portal -> **Cause:** Bicep's `tags` property replaces
  the full tag set on that resource, it doesn't merge -> **Fix:** read
  the resource's existing tags (via `existing` or `reference()`) and
  merge them into the object being deployed if manual additions need to
  survive a redeploy.
- **Symptom:** a cost report shows the same logical environment split
  across two different-looking tag buckets -> **Cause:** inconsistent
  casing in tag values across resources (`prod` vs `Prod`) -> **Fix:**
  standardize on one casing convention and consider an Azure Policy that
  enforces allowed values for that tag.

*Checked against: Microsoft Learn's "Use tags to organize your Azure
resources" and "Tag resources, resource groups, and subscriptions with
Bicep" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources>
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources-bicep>
<https://learn.microsoft.com/en-us/azure/advisor/advisor-overview>

## Why This Matters (Business Context)
A finance team asks which team owns a $4,000/month resource group and nobody can answer without opening every resource one at a time. Consistent tags turn that into a five-second filter in Cost Management. Advisor is the free second opinion that catches the VM someone forgot to resize six months after a traffic spike ended.''',
    },

    # ============================================================
    # 01b-app-hosting
    # ============================================================
    {
        "phase": "01b-app-hosting",
        "slug": "day-08b-container-registry-instances",
        "title": "Azure Container Registry and Container Instances",
        "lab_objective": "Deploy an Azure Container Registry and run a single container through "
            "Azure Container Instances via the Portal. Maps to the Compute domain.",
        "bicep_objective": "Write Bicep for both the registry and the container group, with the "
            "registry's admin user disabled.",
        "lesson": '''## Core Concepts (Read This First)

### Where ACR and ACI Actually Sit
**Azure Container Registry (ACR)** is storage, not compute - a private
registry holding the container images that Container Apps, AKS, App
Service, and ACI all pull from. It doesn't run anything itself.
**Azure Container Instances (ACI)** is the opposite: pure compute, no
registry involved - a single container (or a small group), run once,
billed by the second, with no environment or orchestration layer sitting
around it the way Container Apps has. ACI is the answer for a one-off
job or a burst task that doesn't need `Microsoft.App/managedEnvironments`
standing up around it just to run one container.

### The Admin User Is a Trap, Not a Feature
Every ACR has a built-in admin account - a single shared username/password
that grants full access to the registry. It's meant for early testing
only, and it's disabled by default in this lesson's example on purpose:
using it in anything beyond a quick proof of concept means every person
or pipeline that needs registry access shares one credential with no
individual audit trail. The real answer is Entra ID identities (managed
identity for pipelines, RBAC roles like AcrPull/AcrPush for people)
instead of the admin account.

## What You're Building Today
An Azure Container Registry with the admin user disabled, and a
single container running in Azure Container Instances.

## New Bicep Concepts
- `Microsoft.ContainerRegistry/registries` - a storage-layer resource,
  no relationship in Bicep to what actually runs the containers
- `Microsoft.ContainerInstance/containerGroups` - one or more containers
  sharing network/storage, the ACI resource type
- `restartPolicy` - controls what ACI does when a container exits

## Annotated Example
```bicep
param acrName string = 'acr${uniqueString(resourceGroup().id)}'

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: resourceGroup().location
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: false
  }
}

resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: 'aci-lab'
  location: resourceGroup().location
  properties: {
    osType: 'Linux'
    restartPolicy: 'OnFailure'
    containers: [
      {
        name: 'nginx'
        properties: {
          image: 'mcr.microsoft.com/oss/nginx/nginx:1.15.5-alpine'
          resources: {
            requests: { cpu: 1, memoryInGB: json('1.5') }
          }
          ports: [ { port: 80, protocol: 'TCP' } ]
        }
      }
    ]
    ipAddress: {
      type: 'Public'
      ports: [ { port: 80, protocol: 'TCP' } ]
    }
  }
}
```

## Why It's Written This Way
- `adminUserEnabled: false` is explicit rather than left to default,
  since leaving it implicit invites someone to flip it on "just for now"
  later without thinking about the shared-credential problem it reopens.
- `restartPolicy: 'OnFailure'` (rather than the default `Always`) matches
  ACI's actual sweet spot - a task that should retry if it genuinely
  fails, but not loop forever if it exits cleanly on purpose.
- This example pulls a public Microsoft-hosted image rather than one from
  the ACR just deployed - wiring ACI to pull from a specific private
  registry (image credentials, `imageRegistryCredentials`) is a
  reasonable next step once both resources exist side by side.

## Service Deep Dive

### What It Can't Do
ACI has no persistence or orchestration story beyond a single container
group - no rolling updates, no revisions, no traffic splitting. That's
the entire reason Container Apps exists as a separate product; reaching
for ACI when the workload needs any of those things is the wrong tool,
not a missing feature to work around. ACR's admin user, once disabled,
can't be selectively scoped - it's an all-or-nothing account, which is
exactly why the real-world guidance is to not use it at all rather than
try to restrict what it can do.

### Nuances Worth Knowing
- ACI's three restart policies genuinely change behavior, not just
  logging: `Always` restarts regardless of exit code (even a clean exit
  0), `OnFailure` only restarts on a non-zero exit or an OOM kill, and
  `Never` leaves it stopped no matter why it exited. Picking `Always` for
  a genuinely run-once job means it never actually finishes on its own.
- Export policy on a Premium-tier ACR can block artifacts from leaving a
  network-restricted registry entirely (blocking import-to-another-registry
  and export-pipeline operations) - but this requires public network
  access to already be disabled first, and any existing export pipelines
  removed before the setting can even be changed.
- The Basic SKU used in this lesson is fine for a lab, but real
  production use typically moves to Standard or Premium for higher
  throughput and features like geo-replication, private endpoints, and
  content trust - none of which Basic supports.

### Troubleshooting You'll Actually Hit
- **Symptom:** a container in ACI keeps restarting even though the
  application logic looks correct -> **Cause:** `restartPolicy: 'Always'`
  restarting on a clean exit (code 0), not just genuine failures ->
  **Fix:** check the exit code via `az container show ... --query
  "containers[0].instanceView.currentState"` before assuming the app
  itself is crashing - if the exit code is 0, the restart policy is the
  actual cause.
- **Symptom:** trying to disable export on an ACR fails or is rejected
  -> **Cause:** public network access wasn't disabled first, or an
  export pipeline still exists on the registry -> **Fix:** disable
  public network access and delete any configured export pipelines
  before setting `exportPolicy` to disabled.
- **Symptom:** a pipeline using the ACR admin account stops working after
  a security review disables it -> **Cause:** exactly the intended
  outcome of disabling a shared credential -> **Fix:** move the pipeline
  to a managed identity or service principal with AcrPush/AcrPull instead
  of re-enabling the admin account.

*Checked against: Microsoft Learn's "Quickstart - Create Registry - Bicep"
doc, the PSRule Azure.ACR.AdminUser rule reference, and Azure Container
Instances restart policy documentation.*

## Source
<https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-bicep>
<https://learn.microsoft.com/en-us/azure/container-instances/container-instances-restart-policy>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.containerinstance/containergroups>

## Why This Matters (Business Context)
A CI pipeline needs to build and push a container image somewhere private before Container Apps can pull it - ACR is that somewhere. A one-off data migration script that runs for ten minutes once a month doesn't justify standing up a whole Container Apps environment - ACI runs it, bills for those ten minutes, and disappears.''',
    },

    {
        "phase": "01b-app-hosting",
        "slug": "day-08c-app-service-advanced",
        "title": "App Service - Certificates, Custom Domains, Backup, and VNet Integration",
        "lab_objective": "Bind a custom domain and a managed certificate to Day 07's App Service, "
            "and enable VNet integration, through the Portal. Maps to the Compute domain.",
        "bicep_objective": "Write Bicep for the certificate/hostname binding resources, and document "
            "VNet integration and backup configuration.",
        "lesson": '''## Core Concepts (Read This First)

### Custom Domain and Certificate Are Two Separate Steps
Adding a custom domain to an App Service and binding a TLS certificate to
it are genuinely two operations, not one - you can have a domain added
with "No binding" and the site still serves over plain HTTP (or fails
HTTPS entirely) until a certificate is explicitly bound to it. The free,
Microsoft-managed certificate option covers the common case at no cost,
but it has real limitations worth knowing before assuming it'll cover
every scenario (see Service Deep Dive).

### VNet Integration Is Outbound Only
App Service VNet integration lets the app reach resources inside a VNet
(a database on a private IP, for instance) - it does not make the app
itself privately reachable, and it doesn't change how the app connects
outbound to third-party APIs on the internet. That's a private
*endpoint* pointed at the app (making it reachable only from inside the
VNet), which is a separate, opposite-direction feature entirely.

## What You're Building Today
A custom domain with a free managed certificate bound to it, and VNet
integration connecting the app to Day 11's VNet.

## New Bicep Concepts
- `Microsoft.Web/sites/hostNameBindings` - a child resource attaching a
  custom domain to the site
- `Microsoft.Web/certificates` and `Microsoft.Web/sites/hostNameBindings`
  working together for the actual TLS binding
- `virtualNetworkSubnetId` on the site resource for VNet integration

## Annotated Example
```bicep
param customDomainName string
param subnetId string

resource hostNameBinding 'Microsoft.Web/sites/hostNameBindings@2023-12-01' = {
  name: '${webApp.name}/${customDomainName}'
  properties: {
    siteName: webApp.name
    hostNameType: 'Verified'
  }
}

resource managedCert 'Microsoft.Web/certificates@2023-12-01' = {
  name: 'cert-${customDomainName}'
  location: resourceGroup().location
  properties: {
    serverFarmId: appServicePlan.id
    canonicalName: customDomainName
  }
  dependsOn: [ hostNameBinding ]
}

resource vnetIntegration 'Microsoft.Web/sites/networkConfig@2023-12-01' = {
  name: '${webApp.name}/virtualNetwork'
  properties: {
    subnetResourceId: subnetId
  }
}
```

## Why It's Written This Way
- The hostname binding has to exist and be verified (DNS pointed at the
  app, ownership TXT record in place) *before* the managed certificate
  resource can succeed - `dependsOn` makes that ordering explicit rather
  than relying on luck with deployment timing.
- `Microsoft.Web/sites/networkConfig` is its own child resource, not a
  property directly on the site - VNet integration is added or removed
  independently of the rest of the app's configuration.
- Backup configuration for App Service isn't shown here as a standalone
  resource type in the same way - it's configured through
  `Microsoft.Web/sites/config` (the `backup` config slot), worth reading
  Microsoft's current schema for directly since it changes more often
  than most resource types in this repo.

## Service Deep Dive

### What It Can't Do
The free App Service Managed Certificate has real, hard limits: no
wildcard certificates, no private DNS support, isn't exportable, isn't
supported at all in an App Service Environment, and only works with A
records pointing at the app's IP (not with a root domain integrated with
Traffic Manager). Free/Shared tier plans can't use custom domains with
TLS at all - that requires Basic tier or above, a hard platform block,
not a soft recommendation. App Service backup similarly needs Standard
tier or higher; it isn't available on Free/Shared/Basic.

A multi-tenant App Service plan also caps custom hostnames per app at
500 - a real ceiling worth knowing if a design assumes unlimited
subdomains on one app instead of a wildcard binding or a second app.

### Nuances Worth Knowing
- Binding an SSL certificate stored in Key Vault (rather than the free
  managed cert) needs its own explicit permission: the App Service
  resource provider's identity needs the **Key Vault Certificate User**
  role on that vault. A certificate that's valid and correctly imported
  can still fail to bind with a vague error if this specific role
  assignment is missing - it's not obvious from the error message alone.
- VNet integration doesn't secure inbound traffic and doesn't by itself
  change how the app reaches the public internet for outbound calls to
  third parties - it specifically opens an outbound path *into* the
  integrated VNet, nothing more.
- App Service certificate purchases (the paid, Azure-issued kind, as
  opposed to the free managed certificate) are capped at 10 purchases per
  Pay-As-You-Go or Enterprise Agreement subscription - a real ceiling for
  an org buying certs directly through Azure rather than importing their
  own.

### Troubleshooting You'll Actually Hit
- **Symptom:** a custom domain shows as added in the portal, but the site
  still fails over HTTPS or shows a certificate mismatch -> **Cause:**
  the domain was added but never had a certificate actually bound to it -
  two separate steps -> **Fix:** go to TLS/SSL bindings specifically and
  add the binding; adding the domain alone doesn't do it.
- **Error:** an SSL binding fails even though the certificate is valid in
  Key Vault and the person's own identity can read it -> **Cause:** the
  App Service platform's own identity, not the person's, lacks the Key
  Vault Certificate User role -> **Fix:** grant that role to the App
  Service resource provider identity on the Key Vault, not just to the
  person configuring it.
- **Error:** can't purchase an App Service certificate through the
  portal -> **Cause:** one of several named blockers - Free/Shared tier
  plan, no valid payment method on the subscription, an unsupported
  subscription offer type (like a student subscription), or the
  10-certificate purchase cap already reached -> **Fix:** check which
  specific blocker applies rather than assuming it's a generic error;
  the fix differs for each one.

*Checked against: Microsoft Learn's "Troubleshoot Domain and TLS/SSL
Certificates," "Install a TLS/SSL Certificate for Your App," and
"Troubleshoot Azure App Service certificates" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate>
<https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration>
<https://learn.microsoft.com/en-us/azure/app-service/manage-backup>

## Why This Matters (Business Context)
A client's marketing team wants the app reachable at their real company domain with a padlock in the browser, not a random azurewebsites.net URL with a certificate warning - that trust signal is the whole reason custom domains and TLS binding exist as a separate, deliberate step rather than an afterthought.''',
    },

    # ============================================================
    # 02-networking
    # ============================================================
    {
        "phase": "02-networking",
        "slug": "day-12b-public-dns",
        "title": "Public Azure DNS",
        "lab_objective": "Create a public DNS zone in Azure DNS, add A/CNAME records, and (if a "
            "domain is available) walk through the delegation steps at the registrar. Maps to "
            "the Networking domain.",
        "bicep_objective": "Write Bicep for a public DNS zone and a couple of record sets inside it.",
        "lesson": '''## Core Concepts (Read This First)

### Azure DNS Isn't a Domain Registrar
Creating a zone named `contoso.com` in Azure DNS doesn't buy or reserve
that domain - Azure DNS only hosts the *records* for a domain someone
already owns through a separate registrar (GoDaddy, Namecheap, whoever).
Making Azure DNS actually authoritative for the domain requires a second
step at the registrar: copying Azure's four assigned name server (NS)
addresses into the domain's NS records there. Until that delegation step
happens, the zone exists in Azure but the rest of the internet has no
idea to ask Azure about it.

### This Is Public, Not Private DNS Zones
Day 12 built a **Private DNS Zone** - resolvable only inside linked
VNets, for internal names. Public Azure DNS zones are the opposite:
globally resolvable, for real internet-facing domains. They're separate
resource types with separate purposes; a lesson or exam question saying
just "Azure DNS" without qualifying it usually means this one.

## What You're Building Today
A public DNS zone with an A record and a CNAME record.

## New Bicep Concepts
- `Microsoft.Network/dnsZones` - the public zone resource, distinct from
  `privateDnsZones` from Day 12
- Record sets as their own child resource type, one per record type

## Annotated Example
```bicep
resource dnsZone 'Microsoft.Network/dnsZones@2023-07-01-preview' = {
  name: 'example-lab.com'
  location: 'global'
  properties: {}
}

resource aRecord 'Microsoft.Network/dnsZones/A@2023-07-01-preview' = {
  name: '${dnsZone.name}/www'
  properties: {
    TTL: 3600
    ARecords: [ { ipv4Address: '20.1.2.3' } ]
  }
}

resource cnameRecord 'Microsoft.Network/dnsZones/CNAME@2023-07-01-preview' = {
  name: '${dnsZone.name}/blog'
  properties: {
    TTL: 3600
    CNAMERecord: { cname: 'example-lab.azurewebsites.net' }
  }
}
```

## Why It's Written This Way
- `location: 'global'` on the zone itself - same pattern as action groups
  from Day 27, since DNS zones aren't tied to a specific Azure region the
  way most resources are.
- Each record type gets its own child resource type
  (`dnsZones/A`, `dnsZones/CNAME`, and so on) rather than one generic
  "record" resource with a type property - worth remembering when
  looking up the exact resource type for a record you haven't used yet
  (MX, TXT, NS).
- A CNAME record can't coexist with any other record type on the exact
  same name - that's a DNS-protocol rule, not a Bicep restriction, and
  it's why `blog` and `www` are separate names in this example rather
  than both pointed at the zone apex.

## Service Deep Dive

### What It Can't Do
Azure DNS doesn't support "vanity name servers" - delegating using name
servers that live inside your own zone rather than Azure's assigned
ones. If a design assumes custom-branded name servers, Azure DNS isn't
the tool for that specific requirement. The zone also can't skip
delegation and still resolve publicly - a zone with perfect records and
no delegation at the registrar simply isn't queried by anyone outside
Azure; it's invisible to the public internet until that step is done.

### Nuances Worth Knowing
- Delegation isn't instant even after it's configured correctly -
  Microsoft's own guidance is to wait at least 10 minutes before trying
  to verify it, and real-world propagation across the wider DNS system
  can take meaningfully longer depending on caching along the way.
- Trailing periods on NS records matter for strict DNS-RFC compliance -
  some registrars append the trailing period automatically if you don't
  include it, others don't, and it's worth checking with the specific
  registrar rather than assuming.
- The SOA (Start of Authority) record is created automatically the
  moment the zone exists - querying it with `nslookup` is the standard
  way to confirm delegation actually succeeded, since a successful SOA
  response proves the outside world is reaching Azure's name servers for
  that zone.

### Troubleshooting You'll Actually Hit
- **Symptom:** DNS records look correct in the Azure portal but nobody
  outside Azure can resolve the domain -> **Cause:** delegation was never
  completed at the registrar - the zone exists but nothing points the
  internet at it -> **Fix:** retrieve the zone's four Azure name servers
  and update the domain's NS records at the registrar; the zone being
  "correct" in Azure means nothing until this step happens.
- **Symptom:** delegation was just updated at the registrar and
  resolution still fails immediately after -> **Cause:** normal
  propagation delay, not a misconfiguration -> **Fix:** wait at least 10
  minutes, then verify with `nslookup` querying the SOA record directly
  against one of Azure's name servers before assuming something's wrong.
- **Symptom:** a CNAME record won't save alongside another record on the
  same name -> **Cause:** DNS itself doesn't allow a CNAME to coexist
  with any other record type at that exact name - not a portal bug or a
  Bicep limitation -> **Fix:** move one of the conflicting records to a
  different name, or use an ALIAS record at the zone apex if that's
  specifically what's needed there.

*Checked against: Microsoft Learn's "Tutorial: Host your domain in Azure
DNS" and "Azure DNS delegation overview" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/dns/dns-delegate-domain-azure-dns>
<https://learn.microsoft.com/en-us/azure/dns/dns-domain-delegation>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/dnszones>

## Why This Matters (Business Context)
A company migrating their website to Azure needs their real domain - not an azurewebsites.net URL - pointing at the new environment, and DNS is the literal switch that flips traffic from the old host to the new one. Get the delegation step wrong and customers either can't reach the site at all, or worse, half of them land on the old host and half on the new one during a slow, inconsistent cutover.''',
    },

    {
        "phase": "02-networking",
        "slug": "day-13b-udr-asg",
        "title": "User-Defined Routes and Application Security Groups",
        "lab_objective": "Create a route table forcing traffic through a virtual appliance NIC, "
            "and group VMs into application security groups referenced by an NSG rule, through "
            "the Portal. Maps to the Networking domain.",
        "bicep_objective": "Write Bicep for a route table with a UDR, and an NSG rule that "
            "references ASGs instead of raw IP ranges.",
        "lesson": '''## Core Concepts (Read This First)

### NSGs Decide "Allowed," Routes Decide "Where"
Easy to conflate, genuinely separate questions. An NSG answers "is this
traffic allowed through at all." A route table answers "once it's
allowed, which direction does it actually travel." A design that forces
traffic through a firewall appliance for inspection depends entirely on
routing, not NSG rules - the NSG could allow the traffic perfectly and it
still won't reach the firewall unless a route says to send it there
first.

### ASGs Replace IP Addresses With Roles
An Application Security Group doesn't do anything by itself - it's a
label. You add VM NICs to it, then reference the ASG (instead of a raw
IP address or range) as the source or destination in an NSG rule. The
payoff: "allow AsgWeb to reach AsgDb on 1433" reads as an actual policy
statement and keeps working automatically as VMs are added or removed
from the group, instead of a rule needing to be hand-edited every time
the IP addresses behind it change.

## What You're Building Today
A route table sending subnet traffic through a virtual appliance's NIC,
and NSG rules that reference application security groups instead of IP
ranges.

## New Bicep Concepts
- `Microsoft.Network/routeTables` and its child `routes` collection
- `Microsoft.Network/applicationSecurityGroups` - referenced by ID inside
  an NSG rule's source/destination, not associated with a subnet like an
  NSG is

## Annotated Example
```bicep
resource routeTable 'Microsoft.Network/routeTables@2023-11-01' = {
  name: 'rt-spoke'
  location: resourceGroup().location
  properties: {
    routes: [
      {
        name: 'force-through-firewall'
        properties: {
          addressPrefix: '0.0.0.0/0'
          nextHopType: 'VirtualAppliance'
          nextHopIpAddress: '10.0.0.4'   // private IP of the NVA's NIC
        }
      }
    ]
  }
}

resource asgWeb 'Microsoft.Network/applicationSecurityGroups@2023-11-01' = {
  name: 'asg-web'
  location: resourceGroup().location
}

resource asgDb 'Microsoft.Network/applicationSecurityGroups@2023-11-01' = {
  name: 'asg-db'
  location: resourceGroup().location
}

resource nsgRule 'Microsoft.Network/networkSecurityGroups/securityRules@2023-11-01' = {
  name: '${nsg.name}/allow-web-to-db'
  properties: {
    priority: 200
    direction: 'Inbound'
    access: 'Allow'
    protocol: 'Tcp'
    sourceApplicationSecurityGroups: [ { id: asgWeb.id } ]
    destinationApplicationSecurityGroups: [ { id: asgDb.id } ]
    sourcePortRange: '*'
    destinationPortRange: '1433'
  }
}
```

## Why It's Written This Way
- `nextHopType: 'VirtualAppliance'` plus an explicit `nextHopIpAddress`
  is what actually redirects traffic - `nextHopType` alone without the IP
  isn't enough for this hop type.
- The NIC on the virtual appliance receiving forwarded traffic needs
  "Enable IP forwarding" turned on - a setting on the NIC resource, not
  on the route table - or the appliance drops traffic that isn't
  addressed directly to itself.
- ASGs are referenced by `id`, not embedded inline, because they're
  independent resources a NIC gets added to separately (via the NIC's IP
  configuration) - the NSG rule and the ASG membership are two different
  places in the config, on purpose.

## Service Deep Dive

### What It Can't Do
A subnet can only have one route table associated at a time - no
stacking two route tables the way NSGs can layer at subnet and NIC
level. All network interfaces in a given ASG have to live in the same
virtual network as the first NIC added to it - you can't mix NICs from
different VNets into one ASG. And if an NSG rule references ASGs as both
source and destination, both ASGs' NICs have to be in that same single
VNet too - a rule can't bridge ASGs across VNets even indirectly.

### Nuances Worth Knowing
- A route with `nextHopType: 'None'` deliberately drops matching
  traffic - Azure's own default system routes use this for reserved
  address ranges outside the VNet, and it's also how you'd build an
  explicit blackhole route on purpose.
- Network Watcher's Next Hop tool exists specifically to answer "what
  will actually happen to this traffic" - given a source VM and a
  destination IP, it reports the real next hop type in effect, which is
  the fastest way to confirm whether a UDR is actually being applied the
  way you think it is.
- A single NSG rule can reference up to 10 ASGs in its source or
  destination - useful to know before assuming a rule needs to be split
  across multiple rules for a design with several role groups.
- 0.0.0.0/0 forced through a virtual appliance is powerful but has real
  documented edge cases with services like Azure Route Server and
  certain Private Link/IPv6 traffic - a catch-all route isn't always as
  total as it looks.

### Troubleshooting You'll Actually Hit
- **Symptom:** two VMs in different subnets of the same VNet can't reach
  each other, and NSG rules all look correct -> **Cause:** likely a
  routing issue, not a security-rule issue - a UDR overriding the
  default VNet-local route -> **Fix:** run Network Watcher's Next Hop
  tool between the two VMs; if the next hop type is `VirtualAppliance` or
  `None` instead of `VnetLocal`, a route table is redirecting or dropping
  the traffic before the NSG is even the relevant layer to check.
- **Symptom:** traffic forced through a virtual appliance never arrives,
  even though the route table and NSG both look correct -> **Cause:**
  the appliance's NIC doesn't have IP forwarding enabled, so it silently
  discards traffic not addressed to itself -> **Fix:** enable IP
  forwarding on that specific NIC - a setting easy to miss since it's
  not part of the route table configuration at all.
- **Error:** an NSG rule referencing two ASGs fails to save or apply
  incorrectly -> **Cause:** the ASGs' member NICs aren't all in the same
  VNet, which the rule requires when ASGs sit on both sides -> **Fix:**
  confirm every NIC in both referenced ASGs actually lives in the one
  VNet before building the rule.

*Checked against: Microsoft Learn's "Azure virtual network traffic
routing," "Application security groups overview," and "Network security
groups and application security groups" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview>
<https://learn.microsoft.com/en-us/azure/virtual-network/application-security-groups>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/routetables>

## Why This Matters (Business Context)
A security team wants all outbound traffic inspected by a firewall before it leaves the network, and NSGs alone can't force that path - only routing can. ASGs are the difference between an NSG rule that says '10.0.1.4, 10.0.1.7, 10.0.1.12 through 10.0.1.19 can reach the database' (which breaks the moment a new web server gets a different IP) and one that says 'the web tier can reach the database,' which just keeps working.''',
    },

    # ============================================================
    # 03-storage
    # ============================================================
    {
        "phase": "03-storage",
        "slug": "day-19b-storage-tools-replication",
        "title": "Storage Explorer, AzCopy, Object Replication, and Blob Versioning",
        "lab_objective": "Use Storage Explorer to browse a storage account and AzCopy to copy "
            "blobs between containers, then configure blob versioning and an object replication "
            "policy between two accounts through the Portal. Maps to the Storage domain.",
        "bicep_objective": "Write Bicep enabling blob versioning and change feed on a source "
            "account, and an object replication policy pointing at a destination account.",
        "lesson": '''## Core Concepts (Read This First)

### Storage Explorer and AzCopy Solve Different Problems
**Storage Explorer** is a GUI (desktop app or the in-portal version) for
browsing, uploading, and managing blobs, files, queues, and tables
interactively - the visual tool for "let me look at what's actually in
this account." **AzCopy** is a command-line tool built specifically for
moving large amounts of data fast, with resumable, parallelized transfers
- the tool for "migrate a few hundred GB from on-prem into this
account," not something you'd reach for to check one file's metadata.
Both are named explicitly in the exam objective as the tools for this
job - neither is optional to at least recognize by name and use case.

### Object Replication Needs Two Other Features Turned On First
Object replication (copying blobs from one account to another,
asynchronously, as they change) isn't a standalone switch - it requires
**blob versioning** enabled on both the source and destination accounts,
and **change feed** enabled specifically on the source. Skip either
prerequisite and the replication policy can't be created at all, not
just created and silently non-functional.

## What You're Building Today
Blob versioning and change feed enabled on a source account, and an
object replication policy copying a container's blobs to a second
account.

## New Bicep Concepts
- `isVersioningEnabled` and `changeFeed.enabled` as properties on the
  storage account's blob service, not the account itself
- `Microsoft.Storage/storageAccounts/objectReplicationPolicies` -
  deployed on the *destination* account, referencing the source by ID

## Annotated Example
```bicep
resource sourceBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: sourceStorageAccount
  properties: {
    isVersioningEnabled: true
    changeFeed: { enabled: true }
  }
}

resource destBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: destStorageAccount
  properties: {
    isVersioningEnabled: true
  }
}

resource replicationPolicy 'Microsoft.Storage/storageAccounts/objectReplicationPolicies@2023-01-01' = {
  name: destStorageAccount.name
  parent: destStorageAccount
  properties: {
    sourceAccount: sourceStorageAccount.name
    destinationAccount: destStorageAccount.name
    rules: [
      {
        sourceContainer: 'source-container'
        destinationContainer: 'dest-container'
      }
    ]
  }
  dependsOn: [ sourceBlobService, destBlobService ]
}
```

## Why It's Written This Way
- Both `blobServices` resources have to deploy and take effect before the
  replication policy - `dependsOn` makes that explicit, since the
  policy's creation genuinely fails if versioning isn't already active on
  both sides.
- The replication policy resource is named after the *destination*
  account and deployed as its child, even though it describes a
  relationship spanning two accounts - a real, slightly unintuitive
  Azure API design choice worth remembering rather than re-deriving each
  time.
- Change feed is enabled only on the source in this example, matching
  the actual requirement - the destination doesn't need it, only
  versioning.

## Service Deep Dive

### What It Can't Do
Object replication only works between General Purpose v2 or Premium
block blob accounts - both source and destination have to match one of
those types, and it only replicates block blobs, not append or page
blobs. It isn't supported on accounts with a hierarchical namespace
enabled (Data Lake Storage Gen2) at all. And once an account has an
active replication policy, blob versioning can't be disabled on it
without first deleting the replication policy - the dependency runs both
directions.

AzCopy and Storage Explorer aren't backup tools by design - copying data
with AzCopy doesn't preserve point-in-time recovery the way a real backup
policy would, and neither tool replaces the Backup/lifecycle features
from earlier storage days.

### Nuances Worth Knowing
- Object replication is one-way per policy - replicating in both
  directions between two accounts needs two separate policies, one per
  direction, and mixing that up carelessly can create replication loops.
- Deletions replicate too, not just new/changed blobs - a blob deleted at
  the source disappears at the destination as well, which matters if the
  destination was meant to be an independent, delete-resistant copy;
  pairing replication with soft delete at the destination is the real
  safety net there, not the replication policy alone.
- Replication is asynchronous and has a measurable, documented SLA
  (99% of objects replicated within 15 minutes for same-continent
  source/destination pairs under Priority Replication) rather than being
  instantaneous - a design assuming near-real-time consistency between
  the two accounts will be wrong by design, not by bug.
- Configuring an object replication policy requires at least Contributor
  scoped to the storage account (or higher) - a real, specific
  permission requirement beyond generic storage access.

### Troubleshooting You'll Actually Hit
- **Error:** creating an object replication policy fails outright ->
  **Cause:** blob versioning isn't enabled on both accounts, or change
  feed isn't enabled on the source - the three prerequisites (versioning
  x2, change feed x1) genuinely block policy creation, not just
  functionality -> **Fix:** enable versioning on both accounts and
  change feed on the source first, then create the policy.
- **Error:** trying to disable blob versioning on an account fails or is
  rejected -> **Cause:** an active object replication policy still
  depends on it -> **Fix:** delete the replication policy first, then
  disable versioning if that's genuinely still the goal.
- **Symptom:** a blob deleted at the source also disappeared from what
  was assumed to be an independent destination copy -> **Cause:**
  replication propagates deletes by design, it isn't a one-way backup ->
  **Fix:** enable soft delete (or immutability) at the destination
  account specifically if the goal is protection against accidental
  deletion, since replication alone won't provide that.

*Checked against: Microsoft Learn's "Object replication overview" and
"Configure object replication" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/storage/blobs/object-replication-overview>
<https://learn.microsoft.com/en-us/azure/storage/blobs/object-replication-configure>
<https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10>

## Why This Matters (Business Context)
A company needs a read-optimized copy of its blob data in a second region so users there don't pay cross-region latency on every request - object replication keeps that copy current automatically instead of someone running a manual sync job. AzCopy is the tool that actually moves the terabytes of existing data there in the first place, since dragging files through a browser upload doesn't scale past a folder or two.''',
    },

    # ============================================================
    # 04-identity-access
    # ============================================================
    {
        "phase": "04-identity-access",
        "slug": "day-21b-entra-licenses-external-users",
        "title": "Entra ID Licenses and External (Guest) Users",
        "lab_objective": "Assign a license to a group in Entra ID (group-based licensing), and "
            "invite an external guest user, through the Portal. Maps to the Identities and "
            "Governance domain.",
        "bicep_objective": "No Bicep resource type exists for license assignment or B2B "
            "invitations - document why, same as Conditional Access and SSPR from Day 23.",
        "lesson": '''## Straight Talk First
Neither license assignment nor B2B guest invitations have a Bicep
resource type, and neither is in the Microsoft Graph Bicep extension's
supported list from Day 21 (Groups, Applications, Service Principals,
App Role Assignments, OAuth2 permission grants, Federated Identity
Credentials - licenses and invitations aren't on that list). Both are
configured through the portal, Microsoft Graph PowerShell, or direct
Graph API calls - a real gap the same way Conditional Access and SSPR
were on Day 23, and for the same underlying reason: this is Entra ID
directory-management territory, not an ARM resource.

## What Actually Configures This
- **Group-based licensing**: assign a product license (Microsoft 365,
  Entra ID P1/P2, etc.) to a *group* instead of individual users - every
  current and future member inherits the license automatically, and it's
  removed automatically the moment someone leaves the group. Configured
  in the Entra admin center or via Microsoft Graph PowerShell
  (`Set-MgGroupLicense` and related cmdlets).
- **External/guest users (B2B collaboration)**: inviting someone outside
  the tenant to collaborate without creating them a full local account -
  configured under External Identities > External collaboration settings,
  or via the Graph invitation API/PowerShell for bulk or automated
  invites.

## Why This Matters For the Exam
AZ-104 tests understanding of *what* group-based licensing and external
users are, how they behave, and what governs them - not Bicep syntax for
either, since none exists. Expect scenario questions ("a user was removed
from a group, what happens to their license") more than deployment
questions.

## What To Actually Do Today
1. In the portal, create (or reuse) an Entra security group, assign it a
   license under Licenses > group-based licensing, and confirm at least
   one member shows the license as "inherited (group)" rather than
   "direct."
2. Under External Identities, invite a guest user with an email address
   you control, and confirm the invitation email actually arrives and
   the guest object appears with `userType: Guest`.

## Service Deep Dive

### What It Can't Do
Group-based licensing can't assign a license to a user in an unsupported
usage location - Entra ID needs a usage location set on the user before
group licensing can apply, and if it's missing or unsupported for that
specific license SKU, the assignment fails silently in the background,
recorded as an error state on that user rather than surfaced immediately.
External users specifically can only be added to groups that are
"assigned" type or Security groups - not to groups mastered on-premises
via Entra Connect, since on-prem-sourced groups aren't something Entra ID
directly manages membership for.

### Nuances Worth Knowing
- License errors from group-based licensing don't interrupt anything or
  alert in real time - they're recorded silently on the user object
  within the group and have to be actively checked (M365 Admin Center >
  Billing > Licenses > that product > Users, filtered to error states) to
  even discover they exist.
- A common, specific license error: two products assigned to the same
  user (one directly, one via a group) contain conflicting service plans
  that can't coexist - resolving that conflict is always a manual
  administrator decision, not something Entra resolves automatically.
- B2B guest invitations can fail with "insufficient privileges" even for
  an account that was inviting guests successfully yesterday - a
  documented pattern usually traced to changed external collaboration
  settings or a role assignment change, not a broken account.
- Guest objects aren't visible in the organization's global address list
  by default - a deliberate default, not a bug, and there's a separate
  explicit step to make guests visible there if that's actually wanted.
- Role-assignable groups (letting a group itself hold an Entra directory
  role) require an Entra ID P1 license or higher - a real licensing
  prerequisite, not just a feature toggle.

### Troubleshooting You'll Actually Hit
- **Symptom:** a user in a licensed group doesn't actually show the
  license applied -> **Cause:** commonly a missing or unsupported usage
  location on that user, or a conflicting service plan from another
  license -> **Fix:** check the product's Users list in the M365 Admin
  Center for that user's specific error state rather than assuming the
  group assignment itself is broken - the group did its job; the
  individual assignment hit a business-logic error.
- **Symptom:** guest invitations suddenly fail with "insufficient
  privileges," despite no obvious account changes -> **Cause:** most
  commonly a change to External collaboration settings (guest invites
  restricted to certain roles, or a domain allow/deny list change) rather
  than the inviting account itself losing permission -> **Fix:** check
  External Identities > External collaboration settings for recent
  changes before assuming a role assignment problem.
- **Symptom:** an external user can't be added to a specific group ->
  **Cause:** the group is mastered on-premises via Entra Connect, and
  external users can only join assigned/Security groups managed natively
  in Entra ID -> **Fix:** use a cloud-native assigned group for external
  user membership instead.

*Checked against: Microsoft Learn's "Identify and resolve license
assignment problems" and "Troubleshoot B2B collaboration issues" docs.*

## Source
<https://learn.microsoft.com/en-us/entra/fundamentals/licensing-groups-resolve-problems>
<https://learn.microsoft.com/en-us/entra/external-id/troubleshoot>
<https://learn.microsoft.com/en-us/entra/fundamentals/licensing-group-advanced>

## Why This Matters (Business Context)
A company onboards fifty new hires in one department at once - assigning fifty individual licenses by hand is exactly the kind of manual, error-prone task group-based licensing exists to eliminate. A vendor needs temporary access to review a shared document without becoming a full employee in the directory - that's precisely the scenario B2B guest access is built for, instead of creating (and later remembering to delete) a real local account for someone who was never actually staff.''',
    },

    # ============================================================
    # 05-monitoring-backup
    # ============================================================
    {
        "phase": "05-monitoring-backup",
        "slug": "day-27b-connection-monitor-alert-processing",
        "title": "Connection Monitor and Alert Processing Rules",
        "lab_objective": "Set up a Connection Monitor test between two VMs through the Portal, "
            "and create an alert processing rule suppressing notifications during a maintenance "
            "window. Maps to the Monitor domain.",
        "bicep_objective": "Write Bicep for an alert processing rule with a scheduled suppression "
            "window. Document Connection Monitor's prerequisites rather than deploying the full "
            "multi-resource setup.",
        "lesson": '''## Core Concepts (Read This First)

### Connection Monitor vs Connection Troubleshoot vs Alert Processing Rules
Three different tools this repo has now touched, worth actually
separating. Day 15's **Connection Troubleshoot** is a one-time check -
"is this working right now." **Connection Monitor** (today) is the
continuous version - it runs the same kind of test on a schedule,
indefinitely, and alerts when results degrade, so problems get caught
before someone reports them rather than only when someone happens to
run a manual check. **Alert processing rules** are a different concern
entirely - not testing anything, just controlling what happens *after*
an alert (from any source, not just Connection Monitor) fires: adding or
suppressing which action groups actually get notified.

### Suppression Rules Solve a Real Maintenance-Window Problem
Disabling alert rules manually before planned maintenance and
re-enabling them after has real, practical failure modes: it only works
cleanly if an alert rule's scope exactly matches the maintenance scope,
it's easy to forget to re-enable, and it does nothing for alerts that
aren't generated by a rule at all (like Azure Service Health events).
Alert processing rules solve this at the notification layer instead - the
alert still fires and still gets recorded, it just doesn't reach anyone
during the defined window.

## What You're Building Today
An alert processing rule suppressing action groups for a resource group
during a scheduled maintenance window.

## New Bicep Concepts
- `Microsoft.AlertsManagement/actionRules` - the resource type behind
  alert processing rules, despite the friendlier portal name
- `schedule.recurrences` for a repeating (not just one-time) suppression
  window

## Annotated Example
```bicep
resource suppressionRule 'Microsoft.AlertsManagement/actionRules@2021-08-08' = {
  name: 'suppress-during-maintenance'
  location: 'global'
  properties: {
    scopes: [ resourceGroup().id ]
    conditions: []
    schedule: {
      effectiveFrom: '2026-08-01T00:00:00'
      effectiveUntil: '2026-12-31T00:00:00'
      timeZone: 'UTC'
      recurrences: [
        {
          recurrenceType: 'Weekly'
          startTime: '02:00:00'
          endTime: '04:00:00'
          daysOfWeek: [ 'Sunday' ]
        }
      ]
    }
    status: 'Enabled'
    type: 'Suppression'
  }
}
```

## Why It's Written This Way
- `type: 'Suppression'` removes action groups from any alert matching the
  scope/conditions during the schedule - the alert still fires and still
  shows up in the portal's fired-alerts list, it just doesn't notify
  anyone while suppressed. `type: 'AddActionGroups'` is the other mode,
  for the opposite case (routing extra notifications somewhere during a
  specific window).
- `scopes: [ resourceGroup().id ]` applies this broadly to everything in
  the resource group - narrowing to specific resources means listing
  their individual resource IDs instead.
- `location: 'global'` matches the same pattern as action groups
  themselves from Day 27's original lesson - this resource type isn't
  regional either.

## Service Deep Dive

### What It Can't Do
Connection Monitor needs an actual agent on the *source* side of any
test - the Network Watcher extension for Azure VMs, or the Log Analytics
agent for on-premises/hybrid sources - it isn't a purely control-plane
diagnostic the way IP Flow Verify is. Alert processing rule filters
apply against whatever fields actually exist in the alert's JSON
payload - a filter that looks correct but doesn't match anything in the
real payload structure won't scope the rule the way it visually appears
to; a documented real-world case saw a rule with a specific server
excluded still suppress that server's alerts, because the exclusion
filter didn't actually match the payload's field as expected.

### Nuances Worth Knowing
- Connection Monitor is explicitly the successor to two older,
  now-retired-in-spirit tools - Connection Monitor (classic) and Network
  Performance Monitor - unifying what used to be separate products into
  one, working across Azure, on-premises, and multi-cloud sources alike.
- An alert processing rule's suppression schedule supports
  `effectiveFrom`/`effectiveUntil` bounding the overall window on top of
  the recurrence pattern itself - useful for "suppress every Sunday
  2-4am, but only through the end of this migration project," not just
  an indefinitely repeating rule.
- Alert processing rules apply within a single subscription - a rule
  created in one subscription doesn't reach resources living in another,
  even if they're logically part of the same environment.

### Troubleshooting You'll Actually Hit
- **Symptom:** an alert processing rule was scoped with a specific
  resource excluded, but that resource's alerts are still being
  suppressed along with everything else -> **Cause:** the filter didn't
  actually match the field it was intended to exclude in the real alert
  payload -> **Fix:** check the actual JSON payload structure the alert
  generates and confirm the filter targets the field that's really there,
  rather than assuming the portal's filter UI guarantees a correct match.
- **Symptom:** Connection Monitor shows no data at all for a test
  involving an on-premises source -> **Cause:** the Log Analytics agent
  (the required piece for non-Azure sources) was never installed or
  isn't reporting -> **Fix:** confirm the agent is installed and healthy
  on the source machine before assuming the test configuration itself is
  wrong.
- **Symptom:** an expected maintenance-window suppression didn't apply,
  and notifications went out anyway -> **Cause:** commonly a scope or
  time-zone mismatch - the rule's `timeZone` and the actual maintenance
  window's local time not lining up the way assumed -> **Fix:** double
  check the rule's configured time zone explicitly rather than assuming
  it matches server or personal local time.

*Checked against: Microsoft Learn's "Alert processing rules for Azure
Monitor alerts" doc and Azure Network Watcher's Connection Monitor
overview.*

## Source
<https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-processing-rules>
<https://learn.microsoft.com/en-us/azure/network-watcher/connection-monitor-overview>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.alertsmanagement/actionrules>

## Why This Matters (Business Context)
A team gets paged at 3am every Sunday because a scheduled maintenance job restarts a service that trips an alert nobody actually needs to see - alert processing rules are how that gets fixed without touching the alert rule itself or risking someone forgetting to re-enable it Monday morning. Connection Monitor is what catches a degrading link between two sites before a customer notices, instead of after.''',
    },

    {
        "phase": "05-monitoring-backup",
        "slug": "day-28b-backup-vault",
        "title": "Backup Vault (Distinct From Recovery Services Vault)",
        "lab_objective": "Create a Backup vault and configure operational backup for a blob "
            "storage account through the Portal. Maps to the Monitor (backup) domain.",
        "bicep_objective": "Write Bicep for the Backup vault and a blob backup policy.",
        "lesson": '''## Core Concepts (Read This First)

### Two Different Vault Resource Types, on Purpose
Day 28 built a **Recovery Services vault**
(`Microsoft.RecoveryServices/vaults`) - the original, broad vault
covering Azure VMs, Azure Files, SQL on VM, SAP HANA, and (as part of the
same underlying service) Azure Site Recovery. **Backup vault**
(`Microsoft.DataProtection/backupVaults`) is a newer, separate resource
type introduced for workloads Azure Backup added more recently - Azure
managed disks, Blob Storage, and Azure Database for PostgreSQL. Neither
replaces the other; a real environment commonly uses both side by side,
picking the vault type based on which workload is being protected.

### Operational vs Vaulted Backup
Backup vault workloads split into two backup styles with genuinely
different mechanics. **Operational backup** (what disk and blob backup
through Backup vault actually are) works via snapshots and change
tracking - fast, and billed only for the incremental storage delta, but
data isn't transferred into long-term vault storage the way Recovery
Services vault backups are. **Vaulted backup** (a newer option, also
available for some Backup-vault workloads) does move data into
durable vault storage for longer retention, closer in spirit to how
Recovery Services vault has always worked.

## What You're Building Today
A Backup vault with a blob storage backup policy protecting a storage
account.

## New Bicep Concepts
- `Microsoft.DataProtection/backupVaults` - a completely separate
  resource namespace from `Microsoft.RecoveryServices`
- Managed identity required on the vault for it to actually perform
  backup/restore operations against the protected resource

## Annotated Example
```bicep
resource backupVault 'Microsoft.DataProtection/backupVaults@2023-05-01' = {
  name: 'bv-lab'
  location: resourceGroup().location
  identity: { type: 'SystemAssigned' }
  properties: {
    storageSettings: [
      {
        datastoreType: 'VaultStore'
        type: 'LocallyRedundant'
      }
    ]
  }
}

resource backupPolicy 'Microsoft.DataProtection/backupVaults/backupPolicies@2023-05-01' = {
  name: 'blob-backup-policy'
  parent: backupVault
  properties: {
    objectType: 'BackupPolicy'
    datasourceTypes: [ 'Microsoft.Storage/storageAccounts/blobServices' ]
  }
}
```

## Why It's Written This Way
- `identity: { type: 'SystemAssigned' }` is required, not optional - the
  vault performs backup/restore by acting *as* that managed identity
  against the storage account, which needs its own explicit RBAC role
  assignment on the storage account (a separate deployment step, not
  shown here) before backups actually work.
- `datastoreType: 'VaultStore'` picks the durable, long-term-retention
  storage style rather than the pure snapshot-only operational path -
  worth deliberately choosing based on the actual retention requirement,
  not defaulting blindly.
- This resource lives under `Microsoft.DataProtection`, a completely
  different provider namespace than Day 28's `Microsoft.RecoveryServices`
  - a real signal that these are architecturally separate services under
  the hood, not variations of the same one.

## Service Deep Dive

### What It Can't Do
Backup vault doesn't do full, application-consistent VM backups the way
Recovery Services vault does - disk backup through Backup vault is
crash-consistent snapshots of OS and data disks, not the same guarantee
as a proper VM-level backup. It also doesn't support Azure Site Recovery
at all - ASR lives exclusively under Recovery Services vault; there's no
Backup-vault equivalent. Disk backup specifically caps at 200 total
snapshots per disk and 180 snapshots per backup policy - a real,
retention-limiting ceiling: hourly backups (24/day) cap out around 7
days of retention purely from the snapshot count limit, not a
configuration choice.

### Nuances Worth Knowing
- Restoring from a disk backup through Backup vault can only create a
  *new* disk - there's no "replace the existing disk in place" restore
  option the way some other backup tools offer.
- On-demand backups and restores through Backup vault are meaningfully
  faster than the equivalent Recovery Services vault operations for VM
  backups, precisely because operational backup works at the snapshot
  layer rather than transferring data into vault storage first.
- The vault's managed identity needing its own RBAC role assignment on
  the protected resource is a real, separate step that's easy to
  forget - a vault and policy can both deploy successfully and backups
  still fail if that role assignment was never added, and the resulting
  error can take up to 30 minutes to reflect after the role assignment
  is finally corrected.
- Blob backup is itself a form of operational backup that doesn't "store"
  data inside the vault in the traditional sense, even though the vault
  resource is still required to manage and orchestrate the backup/restore
  operations.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Backup vault and policy both deploy successfully, but
  backup jobs fail immediately -> **Cause:** the vault's managed identity
  was never granted the RBAC role it needs on the target resource
  (storage account or disk) -> **Fix:** assign the required role (varies
  by datasource type, documented per workload) to the vault's system-
  assigned identity, scoped to the resource being protected, and allow
  up to 30 minutes for the role assignment to actually take effect.
- **Symptom:** disk backup retention can't be extended as far as
  expected for a frequent backup schedule -> **Cause:** the 200-snapshot-
  per-disk / 180-per-policy ceiling limits how much history hourly or
  even daily backups can actually hold -> **Fix:** reduce backup
  frequency if longer retention matters more than granularity, since the
  snapshot count cap doesn't flex based on how the schedule is
  configured.
- **Symptom:** someone expects to configure Site Recovery from inside a
  Backup vault and can't find the option -> **Cause:** Site Recovery is
  exclusively a Recovery Services vault capability -> **Fix:** use the
  Recovery Services vault from Day 28 for anything involving Site
  Recovery; Backup vault has no equivalent.

*Checked against: Microsoft Learn's "Configure and manage backup for
Azure Blobs" doc and community documentation comparing Recovery Services
vault and Backup vault.*

## Source
<https://learn.microsoft.com/en-us/azure/backup/blob-backup-configure-manage>
<https://learn.microsoft.com/en-us/azure/backup/backup-managed-disks>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.dataprotection/backupvaults>

## Why This Matters (Business Context)
A team accidentally deletes a batch of blobs from a storage account backing a customer-facing app, and without operational backup through a Backup vault, that data is gone the moment soft delete's retention window passes. Knowing there are two different vault types - and which one actually protects which workload - is the difference between assuming something is backed up and it actually being backed up.''',
    },

    {
        "phase": "05-monitoring-backup",
        "slug": "day-28c-site-recovery",
        "title": "Azure Site Recovery and Failover",
        "lab_objective": "Enable Azure-to-Azure replication for a VM into a secondary region, and "
            "run a test failover, through the Portal. Maps to the Monitor (backup) domain.",
        "bicep_objective": "Document why Site Recovery's replication configuration is primarily a "
            "Portal/PowerShell workflow rather than a single clean Bicep deployment, and write "
            "Bicep for the vault itself.",
        "lesson": '''## Straight Talk First
Site Recovery's actual replication configuration - enabling protection on
a specific VM, mapping its network/storage to the target region - spans
several interdependent Recovery Services vault sub-resources
(replication fabrics, protection containers, replication policies,
protected items) that are genuinely awkward to hand-write in Bicep and
are overwhelmingly configured through the Portal, PowerShell, or the
Site Recovery-specific CLI extension in real practice. This lesson builds
the vault itself in Bicep (the same pattern as Day 28's Recovery Services
vault) and documents the rest as a Portal/PowerShell workflow, the same
honest approach Day 23 took with Conditional Access.

## Core Concepts (Read This First)

### Replication, Failover, and Reprotection Are Three Different Steps
Enabling replication doesn't fail anything over by itself - it just
starts continuously copying the VM's disk changes to the target region,
building up recovery points over time. **Failover** is the separate,
deliberate action of actually bringing up a VM in the target region from
those recovery points. **Reprotection** is the step after a failover
that starts replicating the now-running target-region VM back toward the
original region, so a future failback is possible - without
reprotection, failover is one-way with no easy path home.

### Recovery Point Choice Matters at Failover Time
Failover isn't "just use whatever's most recent" by default - Site
Recovery offers several recovery point options (Latest, Latest processed,
Latest multi-VM processed, and app-consistent variants for VMs in a
replication group), and they trade off recency against consistency
guarantees. "Latest" gives the lowest possible data loss but pulls
directly from whatever's been sent, which stops being an option the
moment the source region itself goes down mid-transfer - at that point
"Latest processed" (the newest recovery point Site Recovery had already
fully processed before the outage) is what's actually available.

## What You're Building Today
The Recovery Services vault Site Recovery will use (same resource type as
Day 28's backup vault, now serving a second purpose), plus a documented,
Portal-driven walkthrough of enabling Azure-to-Azure replication and
running a test failover.

## New Bicep Concepts
- Nothing new at the resource-type level - Site Recovery reuses Day 28's
  `Microsoft.RecoveryServices/vaults`, since the same vault type serves
  both Backup and Site Recovery
- Recognizing when a task is intentionally left as a documented manual
  workflow rather than forced into Bicep for its own sake

## Annotated Example
```bicep
resource vault 'Microsoft.RecoveryServices/vaults@2023-04-01' = {
  name: 'rsv-dr-lab'
  location: resourceGroup().location
  sku: { name: 'Standard' }
  properties: {}
}
```

The actual Azure-to-Azure replication setup, done through the Portal:
1. In the vault, go to Site Recovery > Enable Replication.
2. Select the source VM and the target region.
3. Choose (or accept default) target resource group, VNet, and storage.
4. Set a replication policy (recovery point retention window, app-
   consistent snapshot frequency).
5. Once initial replication finishes, run **Test Failover** into an
   isolated test network - this is the safe, non-disruptive way to
   validate the setup without touching production traffic.

## Why It's Written This Way
- The vault itself is trivial Bicep - identical in shape to Day 28's,
  since it's literally the same resource type. Everything that makes
  Site Recovery specifically complicated (fabric mapping, replication
  policies tied to specific regions and networks) sits one layer above
  what's realistic to template generically for a lab this size.
- Test Failover exists specifically so failover can be validated without
  affecting the real, currently-running production VM - it spins up an
  isolated copy for testing, then tears it down, leaving actual
  production replication untouched throughout.

## Service Deep Dive

### What It Can't Do
Site Recovery has hard, documented churn limits per disk based on disk
size - a disk generating more data-change traffic than its size supports
triggers a specific "Data change rate beyond supported limits" event, and
the practical fix is a bigger disk (which comes with a higher churn
allowance), not a setting to raise the limit directly. It also can't
create an application-consistent recovery point for a Storage Spaces
Direct configuration - a documented, named gap with no direct fix, only
a workaround using custom pre/post scripts for Linux app-consistency
where applicable.

### Nuances Worth Knowing
- A recovery plan (grouping multiple VMs for coordinated failover)
  requires every VM in it to have at least one recovery point before a
  planned failover can run - a VM with zero recovery points blocks the
  whole plan, not just itself.
- Recovery points created before a Tier/SKU change on the source
  eventually become invalid for failover - triggering a failover against
  one of those specifically fails with a `BookmarkNotFound` error, and
  because pruning old recovery points is a background job, a stale,
  now-unusable recovery point can still visibly appear in the portal for
  a while after the change that invalidated it.
- Failing over shuts down the source VM (when reachable) specifically to
  minimize data loss - Site Recovery waits for pending writes to flush to
  disk before the failover proceeds, which is exactly why "Latest" (the
  lowest possible RPO option) depends on the source being reachable long
  enough for that shutdown to happen cleanly.
- After a failover, reprotection is a separate, explicit action - nothing
  automatically starts replicating the new production VM back toward the
  original region on its own.

### Troubleshooting You'll Actually Hit
- **Error:** an event fires reporting the data change rate on a disk
  exceeds Site Recovery's supported limits -> **Cause:** the disk's churn
  (rate of data change) is higher than its current size supports -
  smaller disks have proportionally lower churn allowances -> **Fix:**
  check Replicated items > VM > Events for the specific disk and its
  actual churn number, then increase that disk's size to raise its
  supported churn ceiling.
- **Error:** a failover attempt fails with `BookmarkNotFound` -> **Cause:**
  the selected recovery point predates a Tier/SKU change on the source
  and is no longer valid, even though it may still be visibly listed ->
  **Fix:** select a recovery point created after the Tier/SKU change, or
  wait for the automatic pruning job to clear the stale one from the
  list.
- **Symptom:** a planned failover for a recovery plan won't run at all
  -> **Cause:** at least one VM in the plan has zero recovery points ->
  **Fix:** confirm every VM in the recovery plan has at least one valid
  recovery point before attempting the planned (not disaster/unplanned)
  failover path, which specifically requires it.

*Checked against: Microsoft Learn's "Troubleshoot replication of Azure
VMs with Azure Site Recovery" and "About failover and failback in Azure
Site Recovery" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/site-recovery/azure-to-azure-troubleshoot-replication>
<https://learn.microsoft.com/en-us/azure/site-recovery/site-recovery-failover>
<https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep>

## Why This Matters (Business Context)
A regional Azure outage takes down the datacenter hosting a company's production VMs, and without Site Recovery already configured and tested, "fail over to another region" is a multi-day scramble instead of a rehearsed, minutes-long process. Test Failover exists precisely so that rehearsal happens on a random Tuesday afternoon, not for the first time during the actual outage.''',
    },
]


LAB_TEMPLATE = """# {day_num} - {title}

## 1. Objective

### Lab Objective (Portal)
{lab_objective}

### Bicep Objective
{bicep_objective}

## 2. Steps Taken (Portal)
What you clicked through in the Azure portal, in order.

## 3. Bicep Translation
The Bicep code you wrote to reproduce the same build. Paste the final
version here or link to the file in ../bicep/.

## 4. Verification
How you confirmed it actually deployed correctly (portal check, az cli
query, test connection, etc).

## 5. Issues & Fixes
Anything that broke, the error message, and what fixed it. This section
is worth more than it looks - it's what you'll actually remember.

## 6. Key Takeaways
2-3 sentences on what this lab taught you and how it connects to the
exam objective.

## Cost Note
What ran, for how long, and whether it's been deallocated/deleted.
"""

SOLUTION_TEMPLATE = "// {slug} - your Bicep code for this day goes here\n"

added = 0
skipped = 0

for day in GAP_DAYS:
    phase_dir = REPO_ROOT / day["phase"]
    if not phase_dir.exists():
        print(f"WARNING: phase folder {day['phase']} not found - skipping {day['slug']}")
        continue

    day_dir = phase_dir / day["slug"]
    lesson_path = day_dir / "lesson.md"

    if lesson_path.exists():
        print(f"SKIP: {day['phase']}/{day['slug']} already has a lesson.md")
        skipped += 1
        continue

    day_dir.mkdir(parents=True, exist_ok=True)

    day_num_label = day["slug"].split("-", 2)[1] if day["slug"].startswith("day-") else day["slug"]
    lesson_text = f"# Day {day_num_label} Lesson - {day['title']}\n\n" + day["lesson"] + "\n"
    lesson_path.write_text(lesson_text, encoding="utf-8")

    lab_text = LAB_TEMPLATE.format(
        day_num=f"Day {day_num_label}",
        title=day["title"],
        lab_objective=day["lab_objective"],
        bicep_objective=day["bicep_objective"],
    )
    (day_dir / "lab.md").write_text(lab_text, encoding="utf-8")

    (day_dir / "solution.bicep").write_text(
        SOLUTION_TEMPLATE.format(slug=day["slug"]), encoding="utf-8"
    )

    print(f"Added {day['phase']}/{day['slug']}")
    added += 1

print()
print(f"Done - {added} new day folders created, {skipped} already existed and were left alone.")