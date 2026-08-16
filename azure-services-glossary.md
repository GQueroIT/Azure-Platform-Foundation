# Azure Services Glossary

The services worth actually knowing to administer a real environment - not
every Azure service (there are hundreds), the ones that matter. This goes
beyond the AZ-104 blueprint on purpose: AI and Data are here because
that's where your portfolio phase is headed, not because the exam covers
them.

## How to Read This

Every service is tagged with a tier:

- 🟢 **Foundational** - shows up in nearly every real environment,
  regardless of what the workload actually does. Learn these cold; you'll
  touch them in almost every deployment you ever build.
- 🔵 **Core** - the load-bearing service for its category. Not always
  present, but when you need what it does, this is the answer.
- 💎 **Hidden Gem** - underused relative to how useful it actually is.
  Knowing these exist, and reaching for them at the right moment, is what
  separates "can deploy a VM" from "can design an environment."

A one-liner on why each one earns its spot follows the name - not full
documentation, just enough to know what it's for and when to reach for it.

---

## Foundational (Cross-Cutting)

Not tied to one category - these show up regardless of what you're
building.

- **Resource Group** 🟢 - the container everything else lives in. If you
  can't answer "what resource group does this belong to," you don't
  understand the deployment yet.

- **Managed Identity** (System-assigned / User-assigned) 🟢 - lets a
  resource authenticate to other Azure services without a stored secret
  or password anywhere. The default answer to "how does this app connect
  to that database" should almost always be Managed Identity, not a
  connection string with embedded credentials. **Also know:** workload
  identity federation - an OIDC-based way for external systems (GitHub
  Actions, Kubernetes) to authenticate to Azure with zero stored secrets
  at all. This is the modern answer for CI/CD pipelines authenticating to
  Azure, replacing a service principal secret sitting in a pipeline
  variable.

- **Key Vault** 🟢 - the one place secrets, keys, and certificates
  actually belong. If you find a password in an app setting or a Bicep
  parameter file, it should be in Key Vault instead. **Also know:** Key
  Vault has two competing permission models that exist side by side -
  legacy **Access Policies** and modern **Azure RBAC**. Worth knowing
  both exist before you're stuck debugging "why can't this identity read
  a secret" and the real answer is you're checking the wrong model.

- **Azure Monitor / Log Analytics Workspace** 🟢 - without this, you find
  out something broke when a customer tells you. With it, you find out
  from an alert, ideally before the customer notices. **Also know:**
  **Application Insights** is the application-performance layer inside
  Azure Monitor - request traces, dependency maps, exception tracking.
  Log Analytics tells you infrastructure broke; Application Insights
  tells you why one specific request took 4 seconds. Most real
  observability work lives in App Insights, not raw Log Analytics
  queries.

- **Azure Policy** 🟢 - the difference between "we have a naming
  convention" (a wiki page nobody reads) and "we enforce a naming
  convention" (a policy that blocks anything that doesn't comply).
- **Tags** 🟢 - not a resource type, but a practice that underlies cost
  tracking, ownership, and automation at any real organization. Every
  resource group should answer "whose is this, what's it for, can it be
  deleted" through its tags alone.

- **Azure Resource Manager (ARM) / Bicep** 🟢 - not a resource either,
  it's the deployment engine everything above goes through. Worth
  including because "click it in the portal" and "deploy it as code" are
  fundamentally different skills, and only one of them scales.

---

## Compute

- **Virtual Machines** 🔵 - the baseline: full control over the OS, the
  most expensive to operate correctly (patching, sizing, scaling all fall
  on you), and still the right answer for anything that needs that level
  of control. **Also know:** VM sizes follow a family naming convention
  worth knowing cold - B-series (burstable, cheap, for spiky/light
  workloads), D-series (general purpose), E-series (memory-optimized),
  F-series (compute-optimized). Also **Spot VMs** - the same hardware at
  a steep discount, evictable with short notice when Azure needs the
  capacity back - the real cost lever for batch jobs or anything that can
  tolerate interruption.

- **VM Scale Sets** 🔵 - VMs that scale as a group instead of one at a
  time. The answer whenever "one VM" needs to become "however many VMs
  the current load actually needs."

- **App Service** 🔵 - the default for "I have a web app, I don't want to
  manage a server." Patching, scaling, and SSL are handled for you at the
  cost of some control.

- **Azure Container Apps** 🔵 - containers without managing a Kubernetes
  cluster, with the ability to scale to zero. The right level of control
  for most containerized workloads that don't specifically need
  Kubernetes itself.

- **Azure Kubernetes Service (AKS)** 🔵 - full Kubernetes, when you
  genuinely need it (complex multi-service architectures, existing
  Kubernetes tooling, specific orchestration requirements). Reach for
  this after confirming Container Apps can't do the job, not before.
  **Also know:** node pools split into system pools (run Kubernetes'
  own core services) and user pools (run your actual workloads), and the
  cluster autoscaler adds/removes nodes automatically based on what's
  actually scheduled.

- **Azure Functions** 🔵 - serverless compute, billed per execution
  instead of per hour a server sits running. The default for "run this
  code when X happens" - a file lands in storage, a message arrives, a
  timer fires - rather than a whole always-on app for something
  event-driven. **Also know:** **Durable Functions** layers stateful
  orchestration on top - chaining multiple function calls together,
  fan-out/fan-in patterns, and long-running workflows that plain
  Functions can't express on their own.

- **Azure Container Registry** 🟢 - the private registry your container
  images live in before Container Apps, AKS, or App Service pull them.
  Effectively mandatory the moment you're running containers at all.

- **Azure Container Instances (ACI)** 💎 - a single container, run once,
  billed by the second, gone when it's done. Overlooked because Container
  Apps gets all the attention, but genuinely the right tool for a
  one-off job or a burst task that doesn't need an environment stood up
  around it.

- **Azure Batch** 💎 - large-scale parallel/batch compute (think:
  processing 10,000 files across 200 VMs, then tearing them all down).
  Rarely mentioned, exactly right for workloads shaped like that.

---

## Networking

- **Virtual Network (VNet)** 🟢 - the network boundary everything else
  lives inside. Nothing meaningfully private happens in Azure without one.

- **Network Security Group (NSG)** 🟢 - the basic allow/deny firewall at
  the subnet or NIC level. The first line of network defense on almost
  every deployment.

- **Load Balancer** 🔵 - Layer 4 traffic distribution across VMs or
  instances. The answer when you need multiple identical backends to look
  like one endpoint, and don't need to understand HTTP to route correctly.

- **Application Gateway** 🔵 - Layer 7 traffic distribution: URL-based
  routing, SSL termination, and an optional Web Application Firewall
  (WAF). The answer when Load Balancer's "just IP and port" isn't enough.

- **Azure Firewall** 🔵 - a managed, stateful firewall for an entire VNet
  (or hub in a hub-and-spoke design), not just one subnet. Centralizes
  outbound/inbound policy instead of managing NSGs everywhere separately.

- **Azure Bastion** 🔵 - RDP/SSH into a VM through the portal, with no
  public IP on the VM itself. The default answer to "how do I manage this
  VM" that isn't "open port 3389/22 to the internet and hope."

- **VPN Gateway / ExpressRoute** 🔵 - connecting on-prem networks to
  Azure. VPN Gateway goes over the public internet (encrypted); ExpressRoute
  is a private, dedicated circuit (faster, more expensive, no internet in
  the path at all). Real companies with real datacenters need one of these.

- **Private Link / Private Endpoint** 💎 - gives a PaaS service (a
  storage account, a database) a private IP inside your VNet, so traffic
  never touches the public internet at all. Massively underused relative
  to how much it improves an environment's actual security posture -
  most people default to public endpoints with firewall rules instead.

- **Azure Front Door** 💎 - global Layer 7 load balancing and CDN in one,
  routing users to the closest healthy backend across regions. The tool
  for "we have this app deployed in three regions, how do users
  automatically hit the nearest healthy one" - a surprisingly common gap
  in people's mental model of what Azure can do.

- **Azure DNS / Private DNS Zones** 🟢 - hosting your own domains, and
  giving internal resources resolvable names instead of hardcoded IPs.
  Quietly foundational the moment anything internal needs to find
  anything else by name.

- **Traffic Manager** 💎 - DNS-level global traffic routing (as opposed
  to Front Door's proxy-level routing). Older, simpler, and still the
  right choice when you need DNS-based failover without Front Door's full
  feature set and cost.

- **Route Table / User Defined Routes (UDR)** 🔵 - NSGs control *whether*
  traffic is allowed through; route tables control *where it actually
  goes*. Easy to miss because NSGs get all the attention, but any design
  routing traffic through a firewall or network appliance depends on
  UDRs to force that path.

- **NAT Gateway** 💎 - gives every VM in a subnet outbound internet
  access through one shared, predictable IP, without assigning a public
  IP to each VM individually. The clean answer to "these VMs need
  outbound internet but should never be reachable from it."

- **Network Watcher** 🔵 - Azure's built-in network diagnostics: packet
  capture, connection troubleshooting, topology views. The tool for
  turning "we think it's a network problem" into an actual answer instead
  of a guess.

- **Azure Virtual WAN** 💎 - hub-and-spoke networking managed as one
  service, for when manually building and peering VNets stops scaling.
  Worth knowing exists before you're hand-wiring peering relationships
  across dozens of VNets that a Virtual WAN hub would manage for you.

- **DDoS Protection** 🔵 - a layer people forget exists until it's needed.
  Basic protection is free and automatic; Standard adds active mitigation
  tuned to your specific traffic patterns, worth it for anything
  genuinely internet-facing and business-critical.

---

## Storage

- **Storage Account** 🟢 - the namespace holding Blob, Files, Queue, and
  Table storage. Some form of this is in almost every environment,
  usually several.

- **Managed Disks** 🔵 - the disks backing every VM's OS and data
  volumes. Not optional if you're running VMs at all; the performance
  tier you pick here is a real cost/performance decision, not a default
  to ignore.

- **Azure Backup / Recovery Services Vault** 🔵 - the difference between
  "we have backups" and "we assume we have backups." Should exist for
  anything that would actually hurt to lose.

- **Azure Data Lake Storage Gen2** 🔵 - Blob storage with a real
  hierarchical filesystem layered on top, built for analytics workloads
  that need to organize and query large volumes of raw data. The storage
  layer underneath most of the Data section below.

- **Azure NetApp Files** 💎 - enterprise-grade, extremely high-performance
  file storage (NFS/SMB) for workloads Azure Files genuinely can't keep
  up with - large databases, SAP, high-throughput analytics. Rarely
  reached for because most people don't know their storage performance
  ceiling until they hit it.

- **Azure File Sync** 💎 - syncs an on-prem Windows file server with an
  Azure Files share, effectively turning the cloud into the source of
  truth while keeping a local, fast cache on-prem. The answer to "we
  want to move our file server to the cloud without ripping the office
  network out from under everyone" - a genuinely common ask most people
  don't know has a named product behind it.

- **Static website hosting (Blob Storage)** 💎 - a storage account can
  serve a static website directly - HTML/CSS/JS, no web server required
  - for close to free. Consistently overlooked because it's a feature
  bolted onto a storage account rather than a product with its own name,
  but it's the cheapest real hosting option that exists in Azure.

---

## Data

- **Azure SQL Database** 🔵 - managed relational SQL Server, no OS or
  patching to manage. The default answer for "we need a real relational
  database" unless there's a specific reason to run SQL Server on a VM
  instead. **Also know:** **Azure SQL Managed Instance** is a distinct
  product, not just a bigger SQL Database - near-total SQL Server
  compatibility (cross-database queries, SQL Agent, linked servers) for
  migrating an existing on-prem SQL Server with minimal changes. The two
  get confused constantly, including on exams - SQL Database is
  cloud-native and simpler; Managed Instance exists specifically for
  compatibility with what you already have.

- **Azure Cosmos DB** 🔵 - globally distributed, multi-model NoSQL
  database with single-digit-millisecond latency guarantees. The answer
  when the data doesn't fit a relational shape, or needs to be
  read/written from multiple regions at once with strong consistency
  guarantees most databases can't offer.

- **Azure Database for PostgreSQL / MySQL** 🔵 - the managed open-source
  equivalents to Azure SQL Database, for teams standardized on Postgres
  or MySQL instead of SQL Server.

- **Microsoft Fabric** 🔵 - the current unified platform for data
  engineering, warehousing, and analytics (folding in what used to be
  separate Synapse Analytics and Power BI experiences). The direction
  Microsoft's whole data platform story has consolidated toward - worth
  knowing this is the current umbrella name before you go looking for the
  older, separate product names.

- **Azure Data Factory** 🔵 - orchestrates moving and transforming data
  between sources (ETL/ELT pipelines). Still usable standalone, and also
  the pipeline engine underneath Fabric's data integration story. If a
  project needs to move data from A to B on a schedule, this is usually
  how.

- **Azure Databricks** 💎 - Apache Spark-based big data processing and
  machine learning, run as a managed Azure service. Overkill for small
  data, and the right answer the moment "data" stops fitting comfortably
  in a single database.

- **Event Hubs** 💎 - ingests massive streams of events (think: millions
  of IoT device messages per second) for real-time processing downstream.
  The unglamorous backbone behind a lot of "real-time dashboard" and
  "streaming analytics" stories nobody thinks to ask about until they
  need to actually build one.

- **Azure Cache for Redis** 💎 - a managed in-memory cache, used to take
  load off a database by serving frequently-requested data from memory
  instead of hitting the database every time. The fix for "our database
  is getting hammered by the same read queries over and over" that a lot
  of people reach for a bigger database SKU to solve instead.

- **Microsoft Purview** 💎 - data governance and cataloging: what data
  exists, where it lives, who owns it, and how sensitive it is, across
  everything from Azure to on-prem to other clouds. Rarely mentioned in
  beginner material, increasingly the actual job the moment an
  organization has more than a handful of data sources and needs to
  answer "where is our sensitive data" with something better than tribal
  knowledge.

---

## AI

**A note on naming before anything else:** this space has renamed itself
more than any other part of Azure - Azure AI Studio became Azure AI
Foundry, which is now becoming Microsoft Foundry, and Azure OpenAI Service
now largely lives inside that platform rather than standing fully alone.
The concepts below are stable even as the product names keep moving -
confirm the current name in the Azure portal or Microsoft Learn when you
actually get to this phase of your build, rather than trusting any name
here (or anywhere else) to still be current by then.

- **Microsoft Foundry** (formerly Azure AI Studio, then Azure AI Foundry)
  🔵 - the unified platform for building with AI models: a large model
  catalog (OpenAI's models plus open-source alternatives), a managed
  agent runtime, evaluation tools, and observability, all under one
  resource with shared identity and networking. This is where "Azure
  OpenAI" work happens today rather than as a fully separate product.

- **Azure AI Search** (also referenced as Foundry IQ) 🔵 - the
  retrieval/search layer behind most real "AI that knows our company's
  data" applications (retrieval-augmented generation, or RAG). Without
  something like this, a language model only knows what it was trained
  on, not your actual documents or data.

- **Azure Machine Learning** 🔵 - for training, tuning, and hosting your
  own custom models, as distinct from Foundry's focus on consuming
  existing large models. Reach for this when the job is "build a model
  from our own data," not "call an existing model."

- **Azure AI Document Intelligence** (formerly Form Recognizer) 💎 -
  extracts structured data (fields, tables, key-value pairs) out of
  scanned documents, invoices, and forms. The unglamorous, extremely
  practical service behind a lot of real "automate this paperwork"
  business cases - easy to overlook next to flashier generative AI
  services.

- **Azure AI Vision / Language / Speech** 💎 - pre-built, ready-to-call
  AI capabilities (image analysis, text analytics, speech-to-text and
  back) that don't require training or hosting a model at all. Worth
  knowing these exist as an off-the-shelf option before reaching for a
  custom model or a large language model to solve something a
  purpose-built API already solves more cheaply.

- **Azure AI Content Safety** 💎 - screens text and images for harmful
  content before they reach a user or get fed into a model. The piece
  most people forget to design in until something goes wrong in
  production - worth building in from the start of any AI-facing project,
  not bolted on after.

---

## Identity & Governance

Not one of the five categories originally asked for, but a real gap to
leave out - this is arguably as foundational as networking. Everything
above authenticates against this layer.

- **Microsoft Entra ID** 🟢 - the identity backbone every other service
  in this glossary ultimately depends on. Users, groups, service
  principals, and app registrations all live here. Worth its own line
  rather than being assumed in the background.

- **Privileged Identity Management (PIM)** 💎 - just-in-time role
  activation instead of standing admin access - someone requests
  Owner for two hours to do a task, instead of holding Owner permanently
  "just in case." A genuine hidden gem for any security-conscious
  environment, and a real gap in most people's mental model of RBAC,
  which tends to stop at "who has what role" without asking "for how
  long, and why always-on."

- **Azure Lighthouse** 💎 - delegated, cross-tenant management - lets one
  organization manage resources in another tenant's subscription without
  guest accounts or switching directories. Relevant the moment you manage
  more than one customer or organization's Azure environment, which is
  the exact shape of a lot of consulting and MSP work.

## Cross-Environment Tooling

The biggest blind spot in any resource-by-resource list: tools that
operate *across* everything else instead of being one more thing you
deploy. These are what separate "I can deploy individual resources" from
"I can actually operate an environment."

- **Azure Resource Graph** 💎 - runs KQL queries across your entire
  environment's resources at once - "every storage account with public
  access enabled," "every VM without a backup policy," in one query
  instead of clicking through resource groups one at a time. Most people
  never learn this exists, and it's one of the highest-leverage tools in
  this entire list once you do.

- **Azure Advisor** 🔵 - a free, built-in recommendations engine scanning
  your environment for cost, security, reliability, and performance
  improvements. Worth checking periodically the same way you'd check
  email - it surfaces real problems (like an underutilized VM sitting at
  3% CPU) before they become expensive habits.

- **Cost Management + Budgets** 🟢 - the budget resource from Day 03 is
  one piece of a larger tool - Cost Management itself gives you cost
  breakdowns by resource, tag, or service, and cost forecasting, not just
  a threshold alert.

- **Azure Automation / Update Manager** 💎 - scheduled patching across a
  fleet of VMs, plus runbooks for operational automation (start/stop VMs
  on a schedule, cleanup tasks) that would otherwise be manual work
  someone has to remember to do.

---

## Also Worth Knowing (Beyond the Five Requested Categories)

Not compute, networking, storage, data, or AI on their own, but they show
up constantly in real architectures, and by name in your own portfolio
project plan (Automated Backup System, Customer Inquiry Manager) - worth
a mention rather than a silent omission.

- **Logic Apps** 🔵 - low-code workflow automation connecting Azure and
  third-party services (send an email when a file lands, post to Teams
  when an alert fires). The glue between services that don't otherwise
  know about each other.

- **Event Grid** 💎 - routes events between Azure services (a blob was
  created, a VM changed state) to whatever should react to them - often
  the thing that actually triggers a Function or a Logic App in the first
  place.

- **Azure Service Bus** 💎 - reliable message queuing between
  application components, built for guaranteed delivery and ordering in
  a way Event Grid isn't designed for. The answer when "make sure this
  message is processed exactly once, in order" actually matters.
  
- **Azure API Management** 💎 - a managed front door for your own APIs:
  rate limiting, authentication, versioning, and a developer portal,
  without building all of that yourself. The step between "we have an
  API" and "we have an API other teams or customers can actually depend
  on."