# Day 29 Lesson - Update Management and Azure Arc

## Straight Talk First
Azure Arc onboarding is NOT a Bicep resource deployment in the normal
sense. You onboard a machine by running the Azure Connected Machine agent
installer (`azcmagent`) directly on that machine, which registers it with
Azure. AFTER it's onboarded, the machine shows up as a
`Microsoft.HybridCompute/machines` resource that you CAN reference or tag
in Bicep - but the actual onboarding step is a script you run on the box,
not a `resource` block you deploy.

## Today's Real Lab
You have a spare machine for this: the RHEL box already running your CCNA
Gauntlet. Onboard it as an Arc-enabled server instead of treating this as
theory-only.

```bash
# Run this ON the RHEL machine itself, not from Bicep/CLI against Azure
sudo dnf install -y azcmagent
sudo azcmagent connect \
  --resource-group <your-rg> \
  --tenant-id <your-tenant-id> \
  --location eastus \
  --subscription-id <your-subscription-id>
```

## New Bicep Concepts (post-onboarding)
Once onboarded, you can reference the Arc machine like any existing
resource:
```bicep
resource arcMachine 'Microsoft.HybridCompute/machines@2023-10-03' existing = {
  name: 'your-rhel-hostname'
}

output arcMachineId string = arcMachine.id
output arcMachineStatus string = arcMachine.properties.status
```

## Why It's Written This Way
- The `existing` keyword shows up one more time here, for the same reason
  it has all build: you're referencing something that was created OUTSIDE
  this Bicep file (in this case, by a CLI agent install, not by Bicep at
  all) so you can read its properties or attach other resources to it,
  like Update Management configuration or a Log Analytics connection.
- Update Management itself, once a machine is Arc-connected, is typically
  configured through Azure Update Manager settings (patch schedules,
  maintenance configurations) which ARE Bicep-deployable
  (`Microsoft.Maintenance/maintenanceConfigurations`) - worth exploring
  once the machine is actually onboarded.

## Source
General Azure Arc onboarding process (azcmagent) - no single Bicep
reference applies to the onboarding step itself, since it isn't a Bicep
operation.