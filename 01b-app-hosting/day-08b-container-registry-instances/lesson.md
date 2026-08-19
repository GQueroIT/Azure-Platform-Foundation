# Day 08b Lesson - Azure Container Registry and Container Instances

## Core Concepts (Read This First)

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
A CI pipeline needs to build and push a container image somewhere private before Container Apps can pull it - ACR is that somewhere. A one-off data migration script that runs for ten minutes once a month doesn't justify standing up a whole Container Apps environment - ACI runs it, bills for those ten minutes, and disappears.
