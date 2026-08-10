# Day 17 Lesson - Blob Storage and Lifecycle Management

## What You're Building Today
A lifecycle management policy that moves blobs to cheaper tiers over time
and eventually deletes them.

## New Bicep Concepts
- A resource nested under a storage account using `parent`, with the fixed
  name `'default'`
- Rule-based policy structure (`filters` + `actions`, not imperative code)

## Annotated Example
```bicep
resource lifecyclePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    policy: {
      rules: [
        {
          name: 'auto-tier-rule'
          enabled: true
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: [ 'blockBlob' ]
            }
            actions: {
              baseBlob: {
                tierToCool: {
                  daysAfterModificationGreaterThan: 30
                }
                tierToArchive: {
                  daysAfterModificationGreaterThan: 90
                }
                delete: {
                  daysAfterModificationGreaterThan: 365
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

## Why It's Written This Way
- The resource name is always literally `'default'` - a storage account
  only ever has one management policy resource, so there's nothing to
  parameterize about the name itself.
- This is a declarative rules engine, not a script - you're not writing
  "check age, then move it." You're describing conditions (`filters`) and
  outcomes (`actions`), and Azure's platform runs this check on a schedule
  in the background. There's no Bicep-side loop or logic here at all.
- The three actions chain naturally: cool after 30 days, archive after 90,
  delete after 365. Each threshold is evaluated independently against the
  blob's last-modified date, not against each other, so a blob doesn't
  have to pass through cool and archive to reach delete - if you skip
  archive, delete still fires on schedule.
- `filters.blobTypes` can scope this to just block blobs, or you can add a
  `prefixMatch` array to only affect blobs in a specific
  container/folder path.

## Source
<https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-policy-configure>