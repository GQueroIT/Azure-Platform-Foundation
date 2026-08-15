# Day 07 Lesson - App Service

## Core Concepts (Read This First)

### App Service Plan Tiers
The plan (`serverfarms`) determines what the app is actually capable of,
not just how much it costs. Roughly, from bottom to top: **Free (F1)** and
**Shared (D1)** run on infrastructure shared with other customers' apps,
no custom domains or SSL, apps sleep after inactivity. **Basic (B1-B3)**
adds custom domains and SSL, still no autoscale. **Standard (S1-S3)** adds
autoscale and deployment slots. **Premium (P1v3-P3v3)** adds more scale
headroom and VNet integration. **Isolated** runs on fully dedicated
infrastructure (an App Service Environment) for the strictest network
isolation requirements. This lesson deploys F1 deliberately, to keep the
lab free - know going in that F1 can't do most of what production App
Service deployments actually rely on.

### Deployment Slots
Starting at Standard tier, an App Service Plan can host multiple
**deployment slots** for the same app - each slot is a fully live,
separately-addressable instance (e.g. a `staging` slot next to
`production`). You deploy new code to staging, test it against real
traffic patterns, then **swap** staging and production - which is a
near-instant DNS/routing switch, not a redeploy, so there's no downtime
and an easy way to roll back by swapping again. This lesson's F1 plan
can't use slots at all; it's worth knowing the feature exists before you
hit a lab or exam question assuming it.

### Multi-Tenant by Default
Every tier below Isolated runs your app on infrastructure Azure also uses
for other customers' apps - you're logically isolated (your app can't see
or affect theirs) but not physically isolated. This is normal and fine
for the overwhelming majority of workloads; Isolated tier/App Service
Environment exists specifically for the cases (regulatory, extreme
network control) where logical isolation isn't enough.

## What You're Building Today
A Free-tier (F1) App Service web app, in Bicep.

## New Bicep Concepts
- Two resources that always travel together: `serverfarms` (the plan) and
  `sites` (the actual app)
- `kind` property changing what a resource type actually means

## Annotated Example
```bicep
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'asp-demo-free'
  location: resourceGroup().location
  sku: {
    name: 'F1'
    tier: 'Free'
  }
  kind: 'linux'
  properties: {
    reserved: true   // required for Linux plans
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-demo-${uniqueString(resourceGroup().id)}'
  location: resourceGroup().location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
    }
  }
}
```

## Why It's Written This Way
- `Microsoft.Web/serverfarms` is confusingly named - it's the App Service
  Plan (the compute + pricing tier), not a literal server farm. `Microsoft.Web/sites`
  is the actual app that runs on top of it. You almost always deploy both
  together, one plan can host multiple sites.
- `reserved: true` is easy to miss and causes a deployment failure if
  skipped on a Linux plan - it's how ARM distinguishes Linux plans from
  Windows ones under the hood.
- App name has to be globally unique across all of Azure (it's part of a
  `*.azurewebsites.net` URL), which is why `uniqueString()` shows up again
  here just like it did for storage accounts.
- `linuxFxVersion` sets the runtime stack. Format is always `RUNTIME|VERSION`.

## Source
<https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/app-service/samples-bicep.md>

## Why This Matters (Business Context)
A small business wants a customer-facing website live without hiring anyone to patch an OS, manage a web server, or handle certificate renewal. App Service is exactly that trade-off - less control than a VM, but someone else owns the patching, scaling, and certificate headaches.
