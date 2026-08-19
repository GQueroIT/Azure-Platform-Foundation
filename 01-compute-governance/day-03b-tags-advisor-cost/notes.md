# Day 03b – Tags, Azure Advisor, and Deeper Cost Management

## 1. Objective

### Lab Objective (Portal)

Apply tags to a resource group and its resources through the Azure Portal and review the current Azure Advisor recommendations for the subscription.

The goal was to understand how tags can help organize Azure resources and how Azure Advisor can identify areas that may need improvement.

## 2. Steps Taken (Portal)

### Resource and Tags

1. I created a new storage account named `lockedblob` inside my existing `locked-cost-rg` resource group.
2. I opened the **Tags** section of the resource group.
3. I created the tag:

   * **Name:** `Service`
   * **Value:** `storage`
4. I applied the tag and confirmed that it appeared on the resource group.
5. I used `Service = storage` because it gives me a simple way to categorize resources based on the service they belong to.

### Azure Advisor

1. I opened **Azure Advisor** for my subscription.
2. I reviewed the available recommendation categories, including Cost, Security, Reliability, Operational Excellence, and Performance.
3. Most categories did not currently have recommendations that required action.
4. The Reliability category showed three active recommendations.
5. Some of the recommendations were related to the storage account I created, including storage redundancy and TLS support.

## 3. Additional Policy Testing

This was not required by the original lab, but I wanted to understand how tag governance would work when new resources are created.

I created an Azure Policy that could apply the resource group's tag to resources that were missing the tag.

I then created a new storage account inside the resource group to test the policy. This allowed me to see how Azure Policy can be used to keep tagging more consistent instead of depending on someone to manually tag every resource.

I also looked into using Azure Policy to control allowed tag values. One reason I wanted to understand this was to avoid inconsistent values such as `storage`, `Storage`, and `STORAGE` when the organization expects one standard format.

## 4. Verification

I confirmed that `Service = storage` appeared on the resource group.

I also tested the policy behavior with a newly created storage account to see how tag governance could be applied to resources inside the group.

Finally, I opened Azure Advisor and confirmed that it was actively analyzing my subscription. The Reliability section showed recommendations related to resources currently deployed in my environment.

## 5. Issues & Testing

I did not have a major issue completing the required lab.

During my additional testing, I attempted to delete the storage account I created. Azure blocked the deletion because `locked-cost-rg` still had the `CanNotDelete` lock from the previous lab.

This showed me that a lock placed at the resource group level also affects resources underneath that resource group. I removed the lock and was then able to delete the storage account.

## 6. Key Takeaways

Tags are useful for adding information to resources that Azure may not already know, such as the environment, department, owner, cost center, or how I want to categorize a service. Keeping tag names and values consistent also makes filtering and cost reporting easier.

Azure Policy can help enforce tagging standards instead of relying on everyone to remember them manually. My additional testing also helped connect Azure Policy with the resource locks from the previous lab because I was able to see multiple governance controls affecting the same resource.

Azure Advisor gives recommendations based on the resources currently deployed in the subscription. Instead of only looking at an Advisor score, I learned that I can drill into categories such as Reliability and review the specific resources and recommended actions.

## Cost Note

The storage account was only created for testing. After I finished testing the tags, policy behavior, Advisor recommendations, and resource lock behavior, I removed the lock when necessary and deleted the storage account.
