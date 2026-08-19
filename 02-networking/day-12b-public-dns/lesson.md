# Day 12b Lesson - Public Azure DNS

## Core Concepts (Read This First)

### Azure DNS Isn't a Domain Registrar
Creating a zone named `contoso.com` in Azure DNS doesn't buy or reserve
that domain - Azure DNS only hosts the *records* for a domain someone
already owns through a separate registrar (GoDaddy, Namecheap, whoever).
Making Azure DNS actually authoritative for the domain requires a second
step at the registrar: copying Azure's four assigned name server (NS)
addresses into the domain's NS records there. Until that delegation step
happens, the zone exists in Azure but the rest of the internet has no
idea to ask Azure about it.

### This Is Public, Not Private DNS Zones
Day 12 built a **Private DNS Zone** - resolvable only inside linked
VNets, for internal names. Public Azure DNS zones are the opposite:
globally resolvable, for real internet-facing domains. They're separate
resource types with separate purposes; a lesson or exam question saying
just "Azure DNS" without qualifying it usually means this one.

## What You're Building Today
A public DNS zone with an A record and a CNAME record.

## New Bicep Concepts
- `Microsoft.Network/dnsZones` - the public zone resource, distinct from
  `privateDnsZones` from Day 12
- Record sets as their own child resource type, one per record type

## Annotated Example
```bicep
resource dnsZone 'Microsoft.Network/dnsZones@2023-07-01-preview' = {
  name: 'example-lab.com'
  location: 'global'
  properties: {}
}

resource aRecord 'Microsoft.Network/dnsZones/A@2023-07-01-preview' = {
  name: '${dnsZone.name}/www'
  properties: {
    TTL: 3600
    ARecords: [ { ipv4Address: '20.1.2.3' } ]
  }
}

resource cnameRecord 'Microsoft.Network/dnsZones/CNAME@2023-07-01-preview' = {
  name: '${dnsZone.name}/blog'
  properties: {
    TTL: 3600
    CNAMERecord: { cname: 'example-lab.azurewebsites.net' }
  }
}
```

## Why It's Written This Way
- `location: 'global'` on the zone itself - same pattern as action groups
  from Day 27, since DNS zones aren't tied to a specific Azure region the
  way most resources are.
- Each record type gets its own child resource type
  (`dnsZones/A`, `dnsZones/CNAME`, and so on) rather than one generic
  "record" resource with a type property - worth remembering when
  looking up the exact resource type for a record you haven't used yet
  (MX, TXT, NS).
- A CNAME record can't coexist with any other record type on the exact
  same name - that's a DNS-protocol rule, not a Bicep restriction, and
  it's why `blog` and `www` are separate names in this example rather
  than both pointed at the zone apex.

## Service Deep Dive

### What It Can't Do
Azure DNS doesn't support "vanity name servers" - delegating using name
servers that live inside your own zone rather than Azure's assigned
ones. If a design assumes custom-branded name servers, Azure DNS isn't
the tool for that specific requirement. The zone also can't skip
delegation and still resolve publicly - a zone with perfect records and
no delegation at the registrar simply isn't queried by anyone outside
Azure; it's invisible to the public internet until that step is done.

### Nuances Worth Knowing
- Delegation isn't instant even after it's configured correctly -
  Microsoft's own guidance is to wait at least 10 minutes before trying
  to verify it, and real-world propagation across the wider DNS system
  can take meaningfully longer depending on caching along the way.
- Trailing periods on NS records matter for strict DNS-RFC compliance -
  some registrars append the trailing period automatically if you don't
  include it, others don't, and it's worth checking with the specific
  registrar rather than assuming.
- The SOA (Start of Authority) record is created automatically the
  moment the zone exists - querying it with `nslookup` is the standard
  way to confirm delegation actually succeeded, since a successful SOA
  response proves the outside world is reaching Azure's name servers for
  that zone.

### Troubleshooting You'll Actually Hit
- **Symptom:** DNS records look correct in the Azure portal but nobody
  outside Azure can resolve the domain -> **Cause:** delegation was never
  completed at the registrar - the zone exists but nothing points the
  internet at it -> **Fix:** retrieve the zone's four Azure name servers
  and update the domain's NS records at the registrar; the zone being
  "correct" in Azure means nothing until this step happens.
- **Symptom:** delegation was just updated at the registrar and
  resolution still fails immediately after -> **Cause:** normal
  propagation delay, not a misconfiguration -> **Fix:** wait at least 10
  minutes, then verify with `nslookup` querying the SOA record directly
  against one of Azure's name servers before assuming something's wrong.
- **Symptom:** a CNAME record won't save alongside another record on the
  same name -> **Cause:** DNS itself doesn't allow a CNAME to coexist
  with any other record type at that exact name - not a portal bug or a
  Bicep limitation -> **Fix:** move one of the conflicting records to a
  different name, or use an ALIAS record at the zone apex if that's
  specifically what's needed there.

*Checked against: Microsoft Learn's "Tutorial: Host your domain in Azure
DNS" and "Azure DNS delegation overview" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/dns/dns-delegate-domain-azure-dns>
<https://learn.microsoft.com/en-us/azure/dns/dns-domain-delegation>
<https://learn.microsoft.com/en-us/azure/templates/microsoft.network/dnszones>

## Why This Matters (Business Context)
A company migrating their website to Azure needs their real domain - not an azurewebsites.net URL - pointing at the new environment, and DNS is the literal switch that flips traffic from the old host to the new one. Get the delegation step wrong and customers either can't reach the site at all, or worse, half of them land on the old host and half on the new one during a slow, inconsistent cutover.
