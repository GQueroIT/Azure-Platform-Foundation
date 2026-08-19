# Day 03 – Resource Locks and Budgets

## 1. Objective

### Lab Objective (Portal)

Create a resource lock and a subscription budget alert through the Azure Portal. The purpose of this lab was to practice protecting resources from accidental deletion while also setting up basic cost monitoring.

## 2. Steps Taken (Portal)

### Resource Lock

1. I created a new resource group named `locked-cost-rg` in East US.
2. I opened the **Locks** section of the resource group and confirmed that there were no existing locks.
3. I created a **Delete (CanNotDelete)** lock named `cannot delete`.
4. I added a note explaining that the lock was being used to restrict deletion of the resource group and its resources.
5. I confirmed that the lock was successfully applied at the resource group scope.

### Budget

1. I opened **Cost Management + Billing** and went to **Budgets**.
2. I confirmed that I did not already have a budget configured.
3. I created a monthly budget named `monthly-budget`.
4. I set the budget amount to **$25 per month**.
5. I configured actual-cost alerts at:

   * **50% – $12.50**
   * **75% – $18.75**
   * **90% – $22.50**
6. I added my email as the alert recipient.
7. I saved the budget and confirmed that it appeared under my available budgets.

## 3. Verification

I verified the resource lock by returning to the **Locks** section of `locked-cost-rg` and confirming that the Delete lock appeared at the resource group scope.

I verified the budget by returning to **Cost Management > Budgets** and confirming that `monthly-budget` was created with a $25 monthly limit.

I later tested the lock by creating a storage account inside `locked-cost-rg` and attempting to delete it. Azure prevented me from deleting the storage account because the resource group had the `CanNotDelete` lock. I had to remove the resource group lock before I could delete the storage account.

## 4. Issues & Fixes

I did not run into an unexpected error during the original lab.

During my additional testing, I could not delete the storage account I created inside `locked-cost-rg`. This was expected because the resource group had a `CanNotDelete` lock, which also protected resources inside the group.

To delete the storage account, I removed the lock from the resource group and then deleted the storage account successfully.

## 5. Key Takeaways

A `CanNotDelete` lock is useful when resources still need to be changed and managed but should be protected from accidental deletion. Applying the lock at the resource group level also protects the resources underneath it.

Azure budgets are used for **cost monitoring and alerts**, not as hard spending limits. My $25 budget will notify me as my actual costs reach the thresholds I configured, but Azure will not automatically stop my resources when the budget is reached.

The extra deletion test helped me see how resource locks actually affect resources in practice instead of only reading about their behavior.

## Cost Note

The resource group itself does not create a usage charge. I created a storage account later for testing and deleted it after completing my tests. I also removed the resource group lock when it was necessary to clean up the test resource.
