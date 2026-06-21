// =============================================================================
// Business Modernization Portal — Azure infrastructure (Bicep).
//
// Provisions the compute + frontend on Azure:
//   * Log Analytics workspace          (required by the Container Apps env)
//   * Container Apps managed environment
//   * Container App: django            (public ingress, port 8000)
//   * Container App: fastapi           (public ingress, port 8000)
//   * Static Web App (Free)            (hosts the React frontend)
//
// The database is an EXTERNAL managed Postgres (Neon), passed in as a
// connection string — Azure free-trial subscriptions are offer-restricted from
// provisioning Azure Database for PostgreSQL, so the managed DB lives off-Azure
// while compute stays on Azure. Backend images come from GHCR (private, pulled
// with registry creds). Deploy with:
//   az deployment group create -g <rg> -f infra/main.bicep -p ...
// =============================================================================

@description('Azure region for the compute resources.')
param location string = resourceGroup().location

@description('Region for the Static Web App (limited set of regions).')
param swaLocation string = 'westeurope'

@description('Prefix for resource names.')
param namePrefix string = 'bmp'

@secure()
@description('Postgres connection string (libpq form), e.g. postgresql://user:pass@host/db?sslmode=require')
param databaseUrl string

@secure()
@description('Django SECRET_KEY for production.')
param djangoSecretKey string

@description('Full GHCR image ref for the Django service (e.g. ghcr.io/owner/apm-interview-django:sha).')
param djangoImage string

@description('Full GHCR image ref for the FastAPI service.')
param fastapiImage string

@description('GHCR username (owner of the read:packages token).')
param ghcrUsername string

@secure()
@description('GHCR token with read:packages — lets Container Apps pull the private images.')
param ghcrPassword string

// Django reads the URL as-is (it honors ?sslmode). FastAPI/SQLAlchemy needs the
// psycopg driver prefix.
var djangoDbUrl = databaseUrl
var fastapiDbUrl = replace(databaseUrl, 'postgresql://', 'postgresql+psycopg://')

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
      registries: [
        { server: 'ghcr.io', username: ghcrUsername, passwordSecretRef: 'ghcr-password' }
      ]
      secrets: [
        { name: 'database-url', value: djangoDbUrl }
        { name: 'django-secret-key', value: djangoSecretKey }
        { name: 'ghcr-password', value: ghcrPassword }
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
      registries: [
        { server: 'ghcr.io', username: ghcrUsername, passwordSecretRef: 'ghcr-password' }
      ]
      secrets: [
        { name: 'database-url', value: fastapiDbUrl }
        { name: 'ghcr-password', value: ghcrPassword }
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
