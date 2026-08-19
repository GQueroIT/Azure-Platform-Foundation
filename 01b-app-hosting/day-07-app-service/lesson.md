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

## Service Deep Dive

### What It Can't Do
F1/D1 aren't just "no custom domain" tiers - they carry hard daily quotas
that stop the app outright. Free tier gets 60 CPU minutes per day (reset
at midnight UTC), plus a rolling 5-minute CPU quota, plus bandwidth,
memory, and filesystem caps. Cross any of them and the app returns a 403
"Quota Exceeded" page for the rest of that window - a full stop, not a
slowdown. Background processes (WebJobs, health-check pings, even
platform diagnostics) burn this quota even when nobody is visiting the
site, which is exactly why a lab app with near-zero real traffic can
still hit it.

Free tier also has no Always On - idle apps unload after roughly 20
minutes, so the next request pays a cold start. Always On itself doesn't
exist below Basic tier. And SNAT limits apply here too, unrelated to CPU
quota: each App Service worker gets 128 preallocated SNAT ports for
outbound connections to the same address+port combination, and that
limit bites even on paid tiers under real load.

### Nuances Worth Knowing
- A deployment slot swap doesn't move everything, and which settings move
  is easy to get backward. Settings marked "Deployment slot setting"
  (sticky) stay with the slot and don't swap; unmarked settings swap with
  the code. Forgetting to mark a staging-only connection string as sticky
  is a real, common way for the wrong database to end up live in
  production after a swap.
- Not every setting respects stickiness even when marked - a documented
  case found `healthCheckPath` swapping despite being expected to stay
  put, so "sticky" isn't airtight for every property. "Swap with Preview"
  shows exactly what will move before it happens, rather than trusting
  the marking blindly.
- Custom domains, TLS/SSL bindings, scale settings, and Always On itself
  are always slot-specific and never swap, regardless of any setting -
  no marking required or possible.

### Troubleshooting You'll Actually Hit
- **Error:** "Quota Exceeded," app returns 403 and won't load even though
  traffic looks light -> **Cause:** F1/D1's daily or 5-minute CPU quota
  was hit, often from background processes rather than real visits ->
  **Fix:** check the App Service Plan > Quotas blade for which quota
  tripped and its reset countdown; for a lab, wait it out - for anything
  real, move off Free/Shared tier.
- **Symptom:** after a slot swap, production is suddenly pointed at the
  wrong database or config -> **Cause:** a setting that should have been
  marked sticky wasn't, so it swapped along with the code -> **Fix:**
  use "Swap with Preview" before swapping for real, and mark
  environment-specific settings (connection strings, per-slot secrets)
  as sticky consistently in both slots.
- **Symptom:** intermittent failed or slow outbound calls to the same
  external API or database under load -> **Cause:** SNAT port
  exhaustion, same root cause as Day 13's Load Balancer -> **Fix:**
  reuse/dispose HttpClient and connection objects instead of opening new
  ones per call, or route the destination through a service/private
  endpoint, which sidesteps the SNAT limit entirely.

*Checked against: Microsoft Learn's "Azure App Service quotas and
metrics," "Troubleshoot intermittent outbound connection errors," and
"Set up staging environments" docs.*


## Source
<https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/app-service/samples-bicep.md>

## Why This Matters (Business Context)
A small business wants a customer-facing website live without hiring anyone to patch an OS, manage a web server, or handle certificate renewal. App Service is exactly that trade-off - less control than a VM, but someone else owns the patching, scaling, and certificate headaches.
