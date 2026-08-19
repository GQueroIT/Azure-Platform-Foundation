# Day 26 Lesson - Log Analytics and Diagnostic Settings

Cost note: keep diagnostic settings scoped to what you're testing - broad,
long-running log ingestion is the main way this phase can rack up cost.

## What You're Building Today
A Log Analytics workspace, and a diagnostic setting sending one resource's
logs into it.

## New Bicep Concepts
- `scope:` used to attach a diagnostic setting to a resource that isn't
  the one being deployed in this file
- Logs and metrics are two separate arrays inside the same resource

## Annotated Example
```bicep
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-lab'
  location: resourceGroup().location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource diagSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'send-to-law'
  scope: storageAccount   // the resource whose logs you're capturing
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      {
        category: 'StorageRead'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'Transaction'
        enabled: true
      }
    ]
  }
}
```

## Why It's Written This Way
- `scope: storageAccount` is the key line - a diagnostic setting is always
  attached TO something else. Without an explicit `scope`, Bicep would try
  to attach it to the current deployment's default scope, which isn't what
  you want here.
- `retentionInDays: 30` keeps this cheap - Log Analytics bills partly on
  retention, and 30 days is the minimum useful window for a lab you're
  actively working in.
- Available log `category` values are different per resource type - a
  storage account's categories aren't the same as a VM's or an App
  Service's. The portal's JSON view (under diagnostic settings) is the
  fastest way to see exactly which categories a given resource supports.

## Service Deep Dive

### What It Can't Do
Diagnostic settings can't filter within a category - it's the whole log
category or none of it; finer filtering happens after ingestion via a
transformation, not at the diagnostic setting itself. A single
diagnostic setting also can't send to more than one destination of the
same type - one workspace, one storage account, one Event Hub max per
setting; fanning out to two workspaces means creating two separate
diagnostic settings.

Every resource is capped at five diagnostic settings total, regardless
of destinations or categories - hit that cap and the fix is removing an
unused setting, not requesting an increase. For regional destinations
(Storage accounts and Event Hubs specifically), the destination has to
be in the same region as the resource being monitored - a diagnostic
setting can't route logs cross-region to a storage account sitting
somewhere else.

### Nuances Worth Knowing
- Nothing here is instant. Data can take up to 90 minutes to start
  flowing after a diagnostic setting is first configured, even though it
  usually arrives within a few minutes in practice - an empty query five
  minutes after setup is expected, not broken.
- A Log Analytics workspace has a default ingestion rate limit around
  6 GB/minute (uncompressed) - a real, hittable ceiling under a genuine
  spike, separate from the daily cap setting.
- If a resource goes quiet and starts exporting nothing but zero-value
  metrics, Azure incrementally backs off how often it checks it, up to a
  two-hour maximum interval after seven days of inactivity - a
  legitimately idle resource can look like a broken diagnostic setting
  purely because of this backoff behavior, snapping back to normal
  latency the moment real data starts flowing again.
- Sending overlapping log categories from two diagnostic settings on the
  same resource into the same workspace produces duplicate records, not
  merged ones - each setting should own a distinct set of categories, or
  point somewhere else entirely.

### Troubleshooting You'll Actually Hit
- **Symptom:** a Log Analytics query comes back empty right after
  setting up a diagnostic setting -> **Cause:** normal ingestion
  latency, up to 90 minutes -> **Fix:** wait before assuming
  misconfiguration; re-check after enough time has passed.
- **Symptom:** data collection stops mid-day with no obvious cause ->
  **Cause:** either the workspace's daily cap was reached, or the
  ~6 GB/min ingestion rate limit was hit -> **Fix:** run
  `Operation | where OperationCategory == 'Data Collection Status'`
  for the daily cap, or check for an "Ingestion" operation citing a rate
  threshold crossed, then raise the cap or wait for the reset.
- **Symptom:** metrics selected in the diagnostic setting don't show up
  as expected when queried -> **Cause:** metrics routed through a
  diagnostic setting land in the `AzureDiagnostics` table, not a
  dedicated metrics table, and not every metric is exportable this way
  -> **Fix:** query `AzureDiagnostics` specifically, and pull anything
  missing directly via the Metrics REST API instead of assuming the
  diagnostic setting is broken.

*Checked against: Microsoft Learn's "Diagnostic settings in Azure
Monitor" and "Troubleshoot why data is no longer being collected in
Azure Monitor" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-monitoring>
<https://rikhepworth.com/post/2024/05/2024-05-17-configuring-diagnostic-settings-for-azure-services-using-bicep/>

## Why This Matters (Business Context)
A production app goes down at 3am and there's no logging turned on, so troubleshooting starts from zero. Diagnostic settings piping into Log Analytics turn 'we have no idea what happened' into 'here's the exact error and the exact minute it started.'
