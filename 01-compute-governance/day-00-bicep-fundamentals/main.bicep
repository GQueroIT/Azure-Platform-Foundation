resource storageAccount 'Microsoft.Storage/storageAccounts@2026-04-01' = {
  name: 'fiftytwotoystorage'
  location: 'eastus'
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}
