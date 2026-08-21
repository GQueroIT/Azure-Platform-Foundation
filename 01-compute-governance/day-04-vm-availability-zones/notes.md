# Key Takeaways and Observations

## VM Size Availability

One thing I learned while creating the VM is that not every VM size is always available for every deployment. The sizes Azure allows me to select can depend on several factors, including the region, availability zone, operating system/image, architecture, subscription limits, and available Azure capacity.

I also noticed that availability can change. A VM size that I am able to deploy at one point may not necessarily be available later because Azure has a finite amount of physical compute capacity within each region and availability zone. This helped me understand that selecting a VM size is not just about choosing how much CPU and RAM I want. I also have to consider whether that SKU is supported and currently available where I am deploying it.

---

## VM Size Determines More Than CPU and RAM

The VM size or SKU defines the capabilities and limits of the virtual machine. CPU and memory are the most obvious differences, but VM sizes can also affect things such as disk support and performance, network performance, number of NICs, temporary storage, and other supported features.

Because of this, VM sizing is both a performance and architecture decision. I cannot assume that I can select any combination of CPU, memory, storage, and networking independently. The VM series and size establish limits that I have to design within.

---

## Region and Availability Zone

The region determines the geographic Azure location where the VM is deployed. I deployed this VM in East US and specifically selected Availability Zone 1.

I learned that region and zone selection also affect what resources and VM SKUs are available. Availability Zones represent separate physical locations within an Azure region, so placing a VM in Zone 1 means I am specifically requesting capacity from that zone rather than simply requesting capacity somewhere in East US.

This becomes important when designing highly available systems because multiple VMs could be distributed across different availability zones instead of relying on a single zone.

---

## Networking Has to Be Designed With the VM

Creating a VM also means deciding how the machine will communicate with other resources and how administrators will access it.

For this deployment, Azure created a virtual network and subnet for the VM. I selected:

- No public IP address
- No public inbound ports
- A private IP address
- A VNet and subnet for internal communication

This showed me that compute and networking cannot really be treated as completely separate decisions. A VM needs a NIC, IP configuration, subnet, and VNet to communicate.

It also made me think about security differently. A VM does not automatically need a public IP address just because I may eventually need to administer it. Remote administration should be designed intentionally rather than automatically exposing SSH or RDP to the Internet.

---

## Authentication

For the Linux VM, I selected SSH public-key authentication instead of password authentication.

This means authentication is based on a public/private key pair. Azure places the public key on the VM while the private key must be protected by the administrator. This is different from simply authenticating with a username and password.

---

## VM Lifecycle and Cost

After Azure finishes deploying a VM, the VM normally begins running unless another configuration or automation changes its state.

If I no longer need the compute resources, I need to make sure the VM reaches the **Stopped (deallocated)** state. Simply shutting down an operating system and assuming that billing has stopped is not something I should rely on without checking the VM's Azure power state.

Deallocation releases the VM's underlying compute capacity, which stops compute charges for the VM itself.

However, **deallocating a VM does not mean the entire deployment becomes free**.

Resources associated with the VM can continue generating charges independently. For example:

- Managed disks can continue generating storage charges.
- Certain networking resources, such as reserved Standard public IP addresses, can continue generating charges.
- Other attached Azure services can continue generating charges according to their own pricing.

This taught me to think of a VM as a collection of Azure resources rather than one object with one bill. Deallocating the compute resource does not automatically remove or stop billing for every resource supporting the VM.

---

## What I Built

For this lab I deployed a Red Hat Enterprise Linux virtual machine with:

- Region: East US
- Availability Zone: Zone 1
- Architecture: x64
- VM size: Standard F1als v7
- vCPUs: 1
- Memory: 2 GiB
- Authentication: SSH public key
- Public IP: None
- Public inbound ports: None
- Private IP: 172.16.0.4
- VNet/Subnet: Azure-created VNet and subnet
- Tag: Service = virtualmachine

After deployment, I verified that the VM existed successfully and then deallocated it to stop the compute portion of the VM from continuing to generate charges.