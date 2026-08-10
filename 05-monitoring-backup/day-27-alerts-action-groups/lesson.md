# Day 27 Lesson - Alert Rules and Action Groups

## What You're Building Today
An action group (who gets notified) and a metric alert rule (what triggers
the notification).

## New Bicep Concepts
- Action groups use `location: 'global'` regardless of where anything else
  lives
- An alert rule references the action group by ID inside its own
  `actions` array

## Annotated Example
```bicep
param notifyEmail string

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: 'ag-lab-alerts'
  location: 'global'
  properties: {
    groupShortName: 'labalerts'
    enabled: true
    emailReceivers: [
      {
        name: 'primary-contact'
        emailAddress: notifyEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

resource cpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'alert-high-cpu'
  location: 'global'
  properties: {
    severity: 3
    enabled: true
    scopes: [ vm.id ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighCPU'
          metricName: 'Percentage CPU'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}
```

## Why It's Written This Way
- `groupShortName` is limited to 12 characters and shows up in the actual
  SMS/notification text, so it's meant to be a compact label, not a
  description.
- `evaluationFrequency` (how often the rule checks) and `windowSize` (how
  much data it looks back over) use ISO 8601 duration format -
  `PT5M` means 5 minutes, `PT15M` means 15 minutes. This format shows up
  across a lot of Azure Monitor resources, worth recognizing on sight.
- The `criteria.allOf` array lets one alert rule check multiple
  conditions at once (all of them have to be true to fire) - here there's
  only one, but the structure is built for more.
- `severity` runs 0 (critical) to 4 (verbose) - it doesn't change alert
  behavior on its own, but downstream automation and dashboards often
  filter or sort by it.

## Source
<https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/resource-manager-action-groups>

## Why This Matters (Business Context)
A disk fills up on a Friday afternoon and nobody notices until Monday morning, when the app has been down all weekend. An alert rule wired to an action group is the difference between someone getting paged Friday at 3pm versus finding out from an angry customer on Monday.
