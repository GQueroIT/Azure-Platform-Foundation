# Day 07 Lesson - App Service

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