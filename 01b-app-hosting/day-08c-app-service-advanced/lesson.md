# Day 08c Lesson - App Service - Certificates, Custom Domains, Backup, and VNet Integration

## Core Concepts (Read This First)

### Custom Domain and Certificate Are Two Separate Steps
Adding a custom domain to an App Service and binding a TLS certificate to
it are genuinely two operations, not one - you can have a domain added
with "No binding" and the site still serves over plain HTTP (or fails
HTTPS entirely) until a certificate is explicitly bound to it. The free,
Microsoft-managed certificate option covers the common case at no cost,
but it has real limitations worth knowing before assuming it'll cover
every scenario (see Service Deep Dive).

### VNet Integration Is Outbound Only
App Service VNet integration lets the app reach resources inside a VNet
(a database on a private IP, for instance) - it does not make the app
itself privately reachable, and it doesn't change how the app connects
outbound to third-party APIs on the internet. That's a private
*endpoint* pointed at the app (making it reachable only from inside the
VNet), which is a separate, opposite-direction feature entirely.

## What You're Building Today
A custom domain with a free managed certificate bound to it, and VNet
integration connecting the app to Day 11's VNet.

## New Bicep Concepts
- `Microsoft.Web/sites/hostNameBindings` - a child resource attaching a
  custom domain to the site
- `Microsoft.Web/certificates` and `Microsoft.Web/sites/hostNameBindings`
  working together for the actual TLS binding
- `virtualNetworkSubnetId` on the site resource for VNet integration

## Annotated Example
```bicep
param customDomainName string
param subnetId string

resource hostNameBinding 'Microsoft.Web/sites/hostNameBindings@2023-12-01' = {
  name: '${webApp.name}/${customDomainName}'
  properties: {
    siteName: webApp.name
    hostNameType: 'Verified'
  }
}

resource managedCert 'Microsoft.Web/certificates@2023-12-01' = {
  name: 'cert-${customDomainName}'
  location: resourceGroup().location
  properties: {
    serverFarmId: appServicePlan.id
    canonicalName: customDomainName
  }
  dependsOn: [ hostNameBinding ]
}

resource vnetIntegration 'Microsoft.Web/sites/networkConfig@2023-12-01' = {
  name: '${webApp.name}/virtualNetwork'
  properties: {
    subnetResourceId: subnetId
  }
}
```

## Why It's Written This Way
- The hostname binding has to exist and be verified (DNS pointed at the
  app, ownership TXT record in place) *before* the managed certificate
  resource can succeed - `dependsOn` makes that ordering explicit rather
  than relying on luck with deployment timing.
- `Microsoft.Web/sites/networkConfig` is its own child resource, not a
  property directly on the site - VNet integration is added or removed
  independently of the rest of the app's configuration.
- Backup configuration for App Service isn't shown here as a standalone
  resource type in the same way - it's configured through
  `Microsoft.Web/sites/config` (the `backup` config slot), worth reading
  Microsoft's current schema for directly since it changes more often
  than most resource types in this repo.

## Service Deep Dive

### What It Can't Do
The free App Service Managed Certificate has real, hard limits: no
wildcard certificates, no private DNS support, isn't exportable, isn't
supported at all in an App Service Environment, and only works with A
records pointing at the app's IP (not with a root domain integrated with
Traffic Manager). Free/Shared tier plans can't use custom domains with
TLS at all - that requires Basic tier or above, a hard platform block,
not a soft recommendation. App Service backup similarly needs Standard
tier or higher; it isn't available on Free/Shared/Basic.

A multi-tenant App Service plan also caps custom hostnames per app at
500 - a real ceiling worth knowing if a design assumes unlimited
subdomains on one app instead of a wildcard binding or a second app.

### Nuances Worth Knowing
- Binding an SSL certificate stored in Key Vault (rather than the free
  managed cert) needs its own explicit permission: the App Service
  resource provider's identity needs the **Key Vault Certificate User**
  role on that vault. A certificate that's valid and correctly imported
  can still fail to bind with a vague error if this specific role
  assignment is missing - it's not obvious from the error message alone.
- VNet integration doesn't secure inbound traffic and doesn't by itself
  change how the app reaches the public internet for outbound calls to
  third parties - it specifically opens an outbound path *into* the
  integrated VNet, nothing more.
- App Service certificate purchases (the paid, Azure-issued kind, as
  opposed to the free managed certificate) are capped at 10 purchases per
  Pay-As-You-Go or Enterprise Agreement subscription - a real ceiling for
  an org buying certs directly through Azure rather than importing their
  own.

### Troubleshooting You'll Actually Hit
- **Symptom:** a custom domain shows as added in the portal, but the site
  still fails over HTTPS or shows a certificate mismatch -> **Cause:**
  the domain was added but never had a certificate actually bound to it -
  two separate steps -> **Fix:** go to TLS/SSL bindings specifically and
  add the binding; adding the domain alone doesn't do it.
- **Error:** an SSL binding fails even though the certificate is valid in
  Key Vault and the person's own identity can read it -> **Cause:** the
  App Service platform's own identity, not the person's, lacks the Key
  Vault Certificate User role -> **Fix:** grant that role to the App
  Service resource provider identity on the Key Vault, not just to the
  person configuring it.
- **Error:** can't purchase an App Service certificate through the
  portal -> **Cause:** one of several named blockers - Free/Shared tier
  plan, no valid payment method on the subscription, an unsupported
  subscription offer type (like a student subscription), or the
  10-certificate purchase cap already reached -> **Fix:** check which
  specific blocker applies rather than assuming it's a generic error;
  the fix differs for each one.

*Checked against: Microsoft Learn's "Troubleshoot Domain and TLS/SSL
Certificates," "Install a TLS/SSL Certificate for Your App," and
"Troubleshoot Azure App Service certificates" docs.*

## Source
<https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate>
<https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration>
<https://learn.microsoft.com/en-us/azure/app-service/manage-backup>

## Why This Matters (Business Context)
A client's marketing team wants the app reachable at their real company domain with a padlock in the browser, not a random azurewebsites.net URL with a certificate warning - that trust signal is the whole reason custom domains and TLS binding exist as a separate, deliberate step rather than an afterthought.
