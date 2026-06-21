// =============================================================================
// Business Modernization Portal — Azure infrastructure (Bicep).
//
// Provisions everything needed to run the stack on Azure:
//   * Log Analytics workspace          (required by the Container Apps env)
//   * Container Apps managed environment
//   * Azure Database for PostgreSQL    (Flexible Server, Burstable B1ms)
//   * Container App: django            (public ingress, port 8000)
//   * Container App: fastapi           (public ingress, port 8000)
//   * Static Web App (Free)            (hosts the React frontend)
//
// Backend images are pulled from GHCR (public) — no Azure Container Registry,
// so nothing to pay for the registry. Deploy with:
//   az deployment group create -g <rg> -f infra/main.bicep -p ...
// =============================================================================

@description('Azure region for most resources.')
param location string = resourceGroup().location

@description('Region for the Static Web App (limited set of regions).')
param swaLocation string = 'westeurope'

@description('Prefix for resource names.')
param namePrefix string = 'bmp'

@description('PostgreSQL administrator login.')
param postgresAdminLogin string = 'portal'

@secure()
@description('PostgreSQL administrator password.')
param postgresAdminPassword string

@secure()
@description('Django SECRET_KEY for production.')
param djangoSecretKey string

@description('Full GHCR image ref for the Django service (e.g. ghcr.io/owner/apm-interview-django:sha).')
param djangoImage string

@description('Full GHCR image ref for the FastAPI service.')
param fastapiImage string

var dbName = 'portal'
var pgName = toLower('${namePrefix}-pg-${uniqueString(resourceGroup().id)}')

// --- Observability -----------------------------------------------------------
resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

// --- Container Apps environment ---------------------------------------------
resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${namePrefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

// --- PostgreSQL Flexible Server ---------------------------------------------
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: pgName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7, geoRedundantBackup: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
  }
}

resource postgresDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgres
  name: dbName
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}

// Allow access from other Azure services (Container Apps). The 0.0.0.0/0.0.0.0
// rule is Azure's special "Allow public access from Azure services" entry.
resource postgresAzureRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: postgres
  name: 'AllowAzureServices'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
}

// Connection strings (TLS required by Azure -> ?sslmode=require).
var pgHost = postgres.properties.fullyQualifiedDomainName
var djangoDbUrl = 'postgresql://${postgresAdminLogin}:${postgresAdminPassword}@${pgHost}:5432/${dbName}?sslmode=require'
var fastapiDbUrl = 'postgresql+psycopg://${postgresAdminLogin}:${postgresAdminPassword}@${pgHost}:5432/${dbName}?sslmode=require'

// --- Container App: Django ---------------------------------------------------
resource djangoApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-django'
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        corsPolicy: { allowedOrigins: ['*'], allowedMethods: ['*'], allowedHeaders: ['*'] }
      }
      secrets: [
        { name: 'database-url', value: djangoDbUrl }
        { name: 'django-secret-key', value: djangoSecretKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'django'
          image: djangoImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'DATABASE_URL', secretRef: 'database-url' }
            { name: 'DJANGO_SECRET_KEY', secretRef: 'django-secret-key' }
            { name: 'DJANGO_DEBUG', value: '0' }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 2 }
    }
  }
  dependsOn: [postgresDb]
}

// --- Container App: FastAPI --------------------------------------------------
resource fastapiApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-fastapi'
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        corsPolicy: { allowedOrigins: ['*'], allowedMethods: ['*'], allowedHeaders: ['*'] }
      }
      secrets: [
        { name: 'database-url', value: fastapiDbUrl }
      ]
    }
    template: {
      containers: [
        {
          name: 'fastapi'
          image: fastapiImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'DATABASE_URL', secretRef: 'database-url' }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 2 }
    }
  }
  dependsOn: [postgresDb]
}

// --- Static Web App (frontend) ----------------------------------------------
resource web 'Microsoft.Web/staticSites@2024-04-01' = {
  name: '${namePrefix}-web'
  location: swaLocation
  sku: { name: 'Free', tier: 'Free' }
  properties: {
    // Deployed from GitHub Actions via token (no repo link configured here).
    allowConfigFileUpdates: true
  }
}

// --- Outputs -----------------------------------------------------------------
output djangoUrl string = 'https://${djangoApp.properties.configuration.ingress.fqdn}'
output fastapiUrl string = 'https://${fastapiApp.properties.configuration.ingress.fqdn}'
output staticWebAppName string = web.name
output staticWebAppHostname string = web.properties.defaultHostname
output postgresHost string = pgHost
output postgresServerName string = postgres.name
