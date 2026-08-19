# Day 01 - RBAC and Management Groups

## 1. Objective

### Lab Objective (Portal)

Create a management group hierarchy and build a custom RBAC role with only the permissions needed to operate virtual machines.

The main goal was to practice how Azure management groups, RBAC roles, scopes, and inheritance work together.

### Bicep Objective

Practice deploying Azure resources with Bicep and PowerShell instead of only using the Azure Portal.

---

## 2. Steps Taken (Portal)

### Management Group Hierarchy

1. I opened Management Groups in the Azure Portal.
2. I created a management group named `az104-training`.
3. I created another management group named `sandbox`.
4. I moved `az104-training` underneath `sandbox`.
5. I then moved my Azure subscription underneath `az104-training`.

My final hierarchy was:

Tenant Root Group
└── sandbox
    └── az104-training
        └── Azure subscription

This helped me see how Azure resources can be organized above the subscription level.

### Custom RBAC Role

I opened Access Control (IAM) on the `az104-training` management group and created a custom role named:

`Custom VM Operator`

I gave the role only three VM permissions:

- `Microsoft.Compute/virtualMachines/read`
- `Microsoft.Compute/virtualMachines/start/action`
- `Microsoft.Compute/virtualMachines/restart/action`

The purpose was to create a role that could view, start, and restart virtual machines without giving the user full control over them.

I set the assignable scope to the `az104-training` management group.

### Role Assignment

After creating the role, I created a role assignment at the `az104-training` management group.

I selected the `Custom VM Operator` role and assigned it to a user.

I then checked the role assignments in IAM and confirmed that the custom role appeared at that scope.

---

## 3. Bicep Translation

I also worked with Bicep to practice deploying Azure resources from code.

Before deploying, I connected PowerShell to Azure using:

`Connect-AzAccount`

I checked the available subscription with:

`Get-AzSubscription`

I then selected the correct subscription using:

`Set-AzContext -SubscriptionId <subscription-id>`

After setting the correct Azure context, I attempted the deployment with:

`New-AzResourceGroupDeployment -Name main -TemplateFile main.bicep`

The deployment asked me for the resource group name, and I used:

`learn-bicep`

---

## 4. Verification

I verified the management group structure in the Azure Portal and confirmed that the subscription was underneath `az104-training`, which was underneath `sandbox`.

I also verified that the `Custom VM Operator` role existed and that the role assignment appeared under Access Control (IAM).

For Bicep, I verified the deployment through the PowerShell deployment results. After fixing my original issue, the deployment returned:

`ProvisioningState : Succeeded`

This confirmed that the Bicep template deployed successfully.

---

## 5. Issues & Fixes

I ran into an error during my first Bicep deployment.

Azure returned:

`InvalidResourceType`

The error showed that Azure could not find the resource type I specified under the `Microsoft.Storage` namespace.

The problem was with the resource type/API version in my Bicep code. After correcting the Bicep resource definition, I ran the same deployment again and it succeeded.

This was useful because I got to see the difference between a PowerShell problem and a Bicep template problem. My Azure connection and subscription context were working, but the actual resource definition inside the template was incorrect.

---

## 6. Key Takeaways

Management groups give me a way to organize and govern multiple Azure subscriptions instead of managing every subscription separately. Anything assigned higher in the hierarchy can affect resources underneath it through inheritance.

RBAC is based on who gets access, what they are allowed to do, and where that access applies. Creating the `Custom VM Operator` role showed me how I can follow least privilege instead of giving someone a broad built-in role when they only need a few specific permissions.

The Bicep portion also gave me more practice troubleshooting deployments. An unsuccessful deployment does not automatically mean PowerShell or my Azure connection is broken. I have to read the actual deployment error and determine whether the problem is authentication, scope, syntax, resource type, API version, or something else.

## Cost Note

The management groups and RBAC configuration did not require me to run a VM or other expensive workload for this lab. The Bicep deployment was mainly used to practice the deployment process and troubleshoot the template.