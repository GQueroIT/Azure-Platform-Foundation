# Day 00 Lesson - Terraform Fundamentals

Read this before Day 01. Every later lesson in this track assumes you know
what's here. You already know Bicep, so this lesson leans on that constantly
- same ideas, different tool.

## What Terraform Actually Is
Like Bicep, Terraform is declarative: you write what you want to exist, not
the steps to create it. The difference is Bicep only ever talks to Azure and
compiles down to ARM JSON behind the scenes. Terraform talks to *any* cloud
through a plugin system called providers, and it keeps its own record of
what it created in a separate file called state. That one difference -
Terraform tracking its own state instead of relying on Azure Resource
Manager as the source of truth - is the biggest conceptual shift from
Bicep, and it's where most real Terraform pain (and most interview
questions about Terraform) comes from.

## Install and Authenticate
Install Terraform from HashiCorp directly, and use the Azure CLI you
already installed for the Bicep track.

For local learning, the simplest auth path is the one you already use for
Bicep:
```bash
az login
```
Terraform's azurerm provider can read your Azure CLI session directly - no
extra setup needed for solo learning.

HashiCorp's own get-started tutorial instead sets up a Service Principal
with explicit environment variables (ARM_CLIENT_ID, ARM_CLIENT_SECRET,
ARM_SUBSCRIPTION_ID, ARM_TENANT_ID). You don't need that yet - az login is
enough for everything in this track. You WILL need the Service Principal
method later, once this gets wired into GitHub Actions, because a CI
pipeline can't open a browser to log you in interactively.

## The Building Blocks
Every Terraform configuration is built from some combination of these:
```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-day00-example"
  location = "eastus"
}

variable "environment" {
  type    = string
  default = "dev"
}

output "resource_group_id" {
  value = azurerm_resource_group.rg.id
}
```
- **terraform block** - settings for Terraform itself, including which
  providers to download. Bicep has no equivalent - it doesn't need to
  "download" Azure support, because Bicep only ever targets Azure.
- **provider block** - configures a specific provider (azurerm here).
  Roughly equivalent to nothing in Bicep - Bicep is implicitly always
  talking to Azure.
- **resource block** - an actual thing getting created:
  `resource "<type>" "<your-name-for-it>" { ... }`. This is the direct
  equivalent of Bicep's resource keyword, just written the other way
  around (type first, then your name, instead of your name first).
- **variable block** - the Terraform equivalent of Bicep's param.
- **output block** - the same idea as Bicep's output, values handed back
  after apply.

## Reading a Resource Block
```hcl
resource "azurerm_storage_account" "storage" {
  name                     = "stday00001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```
- `azurerm_storage_account` - the resource type. Every azurerm resource
  type maps to something in the Azure Resource Manager API, same as a
  Bicep resource type string - it's just named differently and doesn't
  carry an explicit API version in the block itself (the provider version
  in the terraform block controls that under the hood).
- `"storage"` - your symbolic name for this resource inside this
  configuration, same role as Bicep's symbolic resource name.
- Everything inside `{ }` - the resource's arguments. What's required
  varies by resource type, same as Bicep.
- Notice `azurerm_resource_group.rg.name` - referencing another resource's
  attribute directly. This is how Terraform tracks dependencies between
  resources automatically, without you writing dependsOn the way you
  sometimes have to in Bicep.

## The Workflow
This is your new daily loop, and it maps directly onto the Bicep loop you
already know:

| Step             | Bicep                            | Terraform            |
|------------------|-----------------------------------|-----------------------|
| Download tooling | not needed                        | `terraform init`      |
| Check syntax     | `az bicep build`                  | `terraform validate`  |
| Preview changes  | `az deployment group what-if`     | `terraform plan`      |
| Deploy           | `az deployment group create`      | `terraform apply`     |
| Tear down        | manual delete / `az group delete` | `terraform destroy`   |

`terraform init` downloads the provider plugins your terraform block asked
for and sets up the local working directory. Run it once per new
configuration, and again any time you add a new provider or module.

`terraform plan` is the one to slow down and actually read every time, not
just skim. It shows exactly what will be created, changed, or destroyed
before anything happens - same spirit as what-if, but Terraform *requires*
you to see and approve a plan before apply runs, where Bicep's what-if is
something you have to remember to run yourself.

## State
When you run `terraform apply`, Terraform writes what it created into a
file called `terraform.tfstate` in your working directory. This file is
how Terraform knows what it's responsible for - if you delete something in
the Azure Portal by hand, Terraform's state doesn't know that happened,
and the next plan will show a mismatch (this is called "drift," and it's a
real thing you'll hit).

Two things to get right immediately, because they matter for the rest of
your career with this tool, not just this lesson:
- **Never commit terraform.tfstate to git.** It can contain resource
  properties and sometimes secrets in plaintext. This setup script already
  added it to your .gitignore.
- **State is local by default**, meaning it only exists on your machine.
  Real teams store it remotely (in an Azure Storage Account, typically) so
  more than one person - or a CI pipeline - can safely run Terraform
  against the same infrastructure. You'll set this up later in this
  track's remote-state day; for now, local state is fine.

## Why This Matters (Business Context)
Bicep only works if a team is 100% Azure. The moment a company runs
multi-cloud, or even just wants one tool that manages Azure resources
*and* a GitHub team's repo settings *and* a monitoring dashboard, Bicep
can't do that - Terraform can, through the same provider system you just
saw. That's the entire reason Terraform shows up in Platform/IaaS job
postings as often as Bicep does: it's the one IaC skill that isn't locked
to a single vendor, so it's the one hiring managers can be confident
transfers to whatever the company runs next.

## Source
<https://developer.hashicorp.com/terraform/tutorials/azure-get-started>
<https://developer.hashicorp.com/terraform/tutorials/azure-get-started/azure-build>
<https://developer.hashicorp.com/terraform/language>
