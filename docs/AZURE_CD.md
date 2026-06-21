# Azure CD — runbook

This project ships a full **Continuous Deployment** pipeline to Azure:

| Part            | Service                                | Defined in            |
| --------------- | -------------------------------------- | --------------------- |
| Frontend        | Azure **Static Web Apps** (Free)       | `infra/main.bicep`    |
| Django backend  | Azure **Container Apps** (image from GHCR) | `infra/main.bicep` |
| FastAPI backend | Azure **Container Apps** (image from GHCR) | `infra/main.bicep` |
| Database        | **Neon** managed Postgres (`DATABASE_URL`) | external (see note) |
| Pipeline        | GitHub Actions + **OIDC** (no secrets) | `.github/workflows/cd.yml` |

> **Why Neon and not Azure Database for PostgreSQL?** Azure **free-trial**
> subscriptions are offer-restricted from provisioning managed PostgreSQL in
> every region (`LocationIsOfferRestricted`). So the DB runs on **Neon** (free,
> serverless, can be hosted on Azure infra) and is passed in as a connection
> string. Compute + frontend stay on Azure. With a Pay-As-You-Go subscription
> you can switch back to Azure PostgreSQL by adding the resource to the Bicep.

The workflow ([`cd.yml`](../.github/workflows/cd.yml)) runs after CI passes on `main`
(or manually) and: builds prod images → pushes to GHCR → deploys the Bicep infra →
applies `db/init.sql` → publishes the frontend to Static Web Apps.

> **Infrastructure-as-Code:** everything is declared in [`infra/main.bicep`](../infra/main.bicep).
> Nothing is clicked together by hand — the pipeline provisions and updates it.

---

## Prerequisites

- An **Azure subscription** (the free account works; a card is required for verification,
  but Static Web Apps Free + Container Apps free grant cost ≈ $0 for a light demo).
- **Azure CLI** (`az`) installed locally for the one-time setup below.
- This repo on GitHub (public, so GHCR images and Actions minutes are free).

---

## 1. One-time Azure setup (local `az`)

```bash
az login

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
REPO="CDenisUa/apm-interview"          # owner/repo

# Register the resource providers we use
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Web

# --- Passwordless GitHub -> Azure auth (OIDC) ---
APP_ID=$(az ad app create --display-name "apm-interview-cd" --query appId -o tsv)
az ad sp create --id "$APP_ID"

# Federated credential: trust GitHub Actions running on main
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"$REPO"':ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Let the pipeline create/manage resources in the subscription
az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope "/subscriptions/$SUBSCRIPTION_ID"

echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
```

> Tip: validate the template before the first run —
> `az bicep build -f infra/main.bicep` and `az deployment group validate -g <rg> -f infra/main.bicep -p ...`.

## 2. GitHub configuration

**Settings → Secrets and variables → Actions → Secrets:**

| Secret                  | Value                                              |
| ----------------------- | -------------------------------------------------- |
| `AZURE_CLIENT_ID`       | `APP_ID` from step 1                               |
| `AZURE_TENANT_ID`       | tenant id from step 1                              |
| `AZURE_SUBSCRIPTION_ID` | subscription id from step 1                        |
| `DJANGO_SECRET_KEY`     | a long random string                               |
| `DATABASE_URL`          | Neon connection string `postgresql://user:pass@host/db?sslmode=require` |
| `GHCR_PAT`              | classic PAT with `read:packages` (Container Apps pull the private images) |

**Settings → Secrets and variables → Actions → Variables:**

| Variable               | Example     |
| ---------------------- | ----------- |
| `AZURE_RESOURCE_GROUP` | `bmp-rg`    |
| `AZURE_LOCATION`       | `eastus2`   |

### Create the Neon database (free, no card)

1. Sign up at <https://neon.tech> (GitHub login).
2. New Project → pick **Azure** as the cloud + a region → Create.
3. Copy the **connection string** (`postgresql://…?sslmode=require`) into the
   `DATABASE_URL` secret above.

## 3. Run the pipeline

- Push to `main` (CI runs, then CD), **or**
- **Actions → CD (Azure) → Run workflow** (manual `workflow_dispatch`).

The Container Apps pull the **private** GHCR images using `GHCR_PAT`, so the
packages can stay private — no "make public" step needed.

## 5. Get the live URLs

```bash
RG=bmp-rg
az staticwebapp show  -n bmp-web     -g $RG --query defaultHostname -o tsv               # frontend
az containerapp show  -n bmp-django  -g $RG --query properties.configuration.ingress.fqdn -o tsv
az containerapp show  -n bmp-fastapi -g $RG --query properties.configuration.ingress.fqdn -o tsv
```

---

## Teardown (avoid charges)

```bash
az group delete -n bmp-rg --yes --no-wait
```

## Cost notes (honest)

- **Static Web Apps Free** — $0, always.
- **Container Apps** — scale-to-zero + monthly free grant ⇒ ≈ $0 for a light demo.
- **Neon Postgres** — free tier, $0 (no card).
- **GHCR / GitHub Actions** — free for public repos.

So the whole demo is effectively **$0**. Still, run `az group delete -n bmp-rg --yes`
when you're done to be safe.
