# Lab Notes

1. Searched policy in search bar
   
2. Applying the scope to the resource group so that it can be easier to tear down later. Implementing in bicep writeup later. 
   
3. I clicked on definitions and searched "Allowed locations". In the basics tab, I changed the scope from the subscription which would affect the entire environment, and scoped the policy to the resource group "learn-bicep". The parameter I chose for location is EAST US, then created the policy assignment.

4. I went back to definitions and searched "Require a tag on resources". I chose this because it would be easier to monitor later for cost management. Tags on resources allows for effective cost analysis and scopes resources cost throughout the environment. It is necessary metadata. In the basics tab, I scoped the policy towards the resource group "learn-bicep". Next I assigned the tag "Projects" in the parameters tab and created the policy assignment. 

5. I checked compliance tab for the new policies. Sometimes it takes a while to populate. I waited a bit and refreshed the page. Compliance of the policies were 1 of 2, with "require a resource tag" being out of compliance. It could still be a timing issue. 

6. I began a test of the policies by creating a new resource under the "learn-bicep" resource in a different region that was not "EAST US". I validated the policies are working by attempting to create the resource after applying a tag and it failed. I also tested it with applying EAST US as the location and not assigning a tag. Validation failed. 

7. The tag policy and the location allowed policy are both blocking from creating the resource at the form level. It would not allow deployment if parameters are not met. 

8. There were no costs produced because the resource could not be created due to policy constraints. 

## Learning Experience

Creating the assignment policies taught me that it is important to create scopes for resource groups and subscriptions. Being able to create anything with no scope is the way that costs get driven up, figuring out where the costs are coming from becomes a problem, and monitoring resources also becomes an issue with no way to easily search metadata. The policies are also a layer of security needed to prevent the creation of resources with no visibility. Validating the policies with creating more resources is a great way to check if theyre actually working. During this lab, not being able to create a storage account because all of the policy parameters are not met is a great feature. 