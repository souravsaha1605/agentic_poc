// Purpose: Declare the learning Azure infrastructure
// Learn: Understand parameters, resource relationships and deployment side effects.
// Run: Follow azure_execution/cloud_shell/README.md. Review parameters and Azure what-if before deployment; this creates billable resources.

param location string = resourceGroup().location
@minLength(3)
@maxLength(12)
param prefix string = 'ai103lab'
var suffix = uniqueString(resourceGroup().id)
resource logs 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${prefix}-logs-${suffix}'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}
resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-insights-${suffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}
resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv${take(suffix, 13)}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    accessPolicies: []
  }
}
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${prefix}-plan-${suffix}'
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: { reserved: true }
}
resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: '${prefix}-app-${suffix}'
  location: location
  kind: 'app,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      appCommandLine: 'python -m gunicorn --pythonpath src --bind 0.0.0.0:8000 --workers 2 --timeout 120 academy.api:application'
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'API_LIVE'
          value: 'false'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: insights.properties.ConnectionString
        }
      ]
    }
  }
}
output appName string = app.name
output principalId string = app.identity.principalId
output vaultUri string = vault.properties.vaultUri
output appUrl string = 'https://${app.properties.defaultHostName}'
