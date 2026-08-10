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

## Source
<https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-monitoring>
<https://rikhepworth.com/post/2024/05/2024-05-17-configuring-diagnostic-settings-for-azure-services-using-bicep/>