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

## Service Deep Dive

### What It Can't Do
Notification actions aren't treated equally under the hood - SMS, voice,
and email are all rate limited per phone number/address, but webhooks,
Functions, and Logic App actions aren't rate limited at all. SMS and
voice are capped at one notification every 5 minutes per number; email
is capped at 100 messages per hour per address. Cross a threshold and
Azure doesn't queue the extras for later - they're dropped, with only a
separate notification saying rate limiting kicked in. This is an actual
AZ-104 exam topic: an alert firing every minute for an hour produces
roughly 60 emails but only about 12 SMS messages, purely from these two
different caps.

Metric alerts are also stateful by default - once an alert fires on a
specific metric time series, it won't fire again for that series until
the condition clears (three consecutive evaluations without it being
met) and re-triggers. Deliberate noise reduction, not a bug, but it
means "the alert only notified me once even though the CPU stayed high
for an hour" is expected behavior.

### Nuances Worth Knowing
- If genuinely continuous notifications are needed, that requires
  explicitly making the alert rule stateless (`autoMitigate: false` in
  Bicep/ARM, or unchecking "Automatically resolve alerts" in the
  portal) - the default stateful behavior otherwise suppresses repeat
  notifications on purpose.
- Dynamic thresholds need real history before they mean anything -
  Microsoft's own guidance is a minimum of 3 days and 30 metric samples
  before a dynamic threshold becomes active. A dynamic-threshold alert
  on a resource created minutes ago has nothing to learn from yet.
- Action groups aren't capped per subscription (effectively unlimited),
  but an alert rule's combined properties (query, dimensions,
  description, referenced action groups) can't exceed 64 KB - a large
  KQL query with many dimensions can hit this ceiling and fail at
  creation with a vague "there was a problem with the server" error that
  doesn't obviously point at size as the cause.
- A fired alert visible in the portal but with no SMS/voice/push
  actually delivered is very often an alert processing rule silently
  suppressing that action (e.g. a maintenance-window suppression rule) -
  worth checking before assuming the action group itself is broken.

### Troubleshooting You'll Actually Hit
- **Symptom:** an alert is clearly firing repeatedly in the portal, but
  notifications stopped arriving partway through -> **Cause:** the
  per-recipient rate limit was hit and the excess notifications were
  simply dropped -> **Fix:** confirm this by checking for the rate-limit
  notice sent to that address/number, then reduce alert noise at the
  source or route high-volume notifications through a non-rate-limited
  action type like a webhook instead.
- **Symptom:** a condition stays true for a long stretch but only one
  notification ever arrived -> **Cause:** the metric alert is stateful
  by default and deliberately doesn't re-notify on the same ongoing
  issue -> **Fix:** if repeat notifications are actually wanted,
  explicitly set the rule to stateless (`autoMitigate: false`).
- **Symptom:** creating an alert rule fails with a vague server error ->
  **Cause:** the combined size of the rule's query, dimensions,
  description, and action group references exceeded 64 KB -> **Fix:**
  simplify the query or split an overly broad multi-dimension rule into
  smaller, more targeted rules.

*Checked against: Microsoft Learn's "Create and manage action groups in
Azure Monitor," "Troubleshooting Azure Monitor alerts and
notifications," and "Troubleshoot Azure Monitor metric alerts" docs.*


## Source
<https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/resource-manager-action-groups>

## Why This Matters (Business Context)
A disk fills up on a Friday afternoon and nobody notices until Monday morning, when the app has been down all weekend. An alert rule wired to an action group is the difference between someone getting paged Friday at 3pm versus finding out from an angry customer on Monday.
