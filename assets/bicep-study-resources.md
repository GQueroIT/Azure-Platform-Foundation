# Bicep Study Resources

Every lesson in this repo (in each day's lesson.md) is built from these sources.
Listed by topic so you can go deeper on any day that needs it.

## Fundamentals (syntax, params, variables, outputs, modules)
- [Bicep file structure and syntax](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/file)
- [Parameters in Bicep files](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/parameters)
- [Variables in Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/variables)
- [Outputs in Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/outputs)

## RBAC and Role Assignments
- [Use Bicep to create Azure RBAC resources](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-rbac)
- [Quickstart: Assign an Azure role using Bicep](https://learn.microsoft.com/en-us/azure/role-based-access-control/quickstart-role-assignments-bicep)
- [Microsoft.Authorization/roleAssignments reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.authorization/roleassignments)

## Azure Policy
- [Quickstart: Create policy assignment using Bicep](https://learn.microsoft.com/en-us/azure/governance/policy/assign-policy-bicep)

## Budgets
- [Quickstart - Create a budget with Bicep](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/quick-create-budget-bicep)
- [Microsoft.Consumption/budgets reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.consumption/budgets)

## Virtual Machines and Scale Sets
- [Microsoft.Compute/virtualMachines reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines)
- [Azure.VMSS.AvailabilityZone (PSRule)](https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.VMSS.AvailabilityZone/)

## App Service and Container Apps
- [App Service Bicep samples](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/app-service/samples-bicep.md)
- [Microsoft.App/containerApps reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/containerapps)

## Networking (VNets, Peering, NSGs)
- [Create virtual network resources by using Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-virtual-networks)
- [Microsoft.Network/virtualNetworks/virtualNetworkPeerings reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworks/virtualnetworkpeerings)
- [Azure.NSG.AnyInboundSource (PSRule)](https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.NSG.AnyInboundSource/)

## Bastion and VPN Gateway
- [Azure Bastion Bicep quickstart template](https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.network/azure-bastion/main.bicep)
- [Microsoft.Network/virtualNetworkGateways reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworkgateways)

## Storage and Lifecycle Management
- [Configure a lifecycle management policy](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-policy-configure)
- [Microsoft.Storage/storageAccounts/managementPolicies reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts/managementpolicies)

## Identity - Microsoft Graph Bicep Extension
- [Bicep templates for Microsoft Graph resources (overview)](https://learn.microsoft.com/en-us/graph/templates/overview-bicep-templates-for-graph)
- [Announcing GA of Bicep templates for Microsoft Entra ID resources](https://devblogs.microsoft.com/identity/bicep-templates-for-microsoft-entra-id-resources-is-ga/)
- [Create and Deploy Microsoft Graph Resources with Bicep (quickstart)](https://learn.microsoft.com/en-us/graph/templates/bicep/quickstart-create-bicep-interactive-mode)

## Monitoring - Log Analytics, Diagnostics, Alerts
- [Create monitoring resources by using Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/scenarios-monitoring)
- [Resource Manager template samples for action groups](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/resource-manager-action-groups)

## Backup
- [Microsoft.RecoveryServices/vaults reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.recoveryservices/vaults)
- [Microsoft.RecoveryServices/vaults/backupPolicies reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.recoveryservices/vaults/backuppolicies)
- [Quickstart to create a Recovery Services vault using Bicep](https://learn.microsoft.com/en-us/azure/site-recovery/quickstart-create-vault-bicep)

## General Reference
- [Microsoft.* resource type reference index](https://learn.microsoft.com/en-us/azure/templates/)
- [Azure Verified Modules (production-grade examples once you're past basics)](https://azure.github.io/Azure-Verified-Modules/)