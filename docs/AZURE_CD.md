# Azure CD — runbook

This project ships a full **Continuous Deployment** pipeline to Azure:

| Part            | Azure service                          | Defined in            |
| --------------- | -------------------------------------- | --------------------- |
| Frontend        | **Static Web Apps** (Free)             | `infra/main.bicep`    |
| Django backend  | **Container Apps** (image from GHCR)   | `infra/main.bicep`    |
| FastAPI backend | **Container Apps** (image from GHCR)   | `infra/main.bicep`    |
| Database        | **PostgreSQL Flexible Server**         | `infra/main.bicep`    |
| Pipeline        | GitHub Actions + **OIDC** (no secrets) | `.github/workflows/cd.yml` |

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

| Secret                    | Value                                            |
| ------------------------- | ------------------------------------------------ |
| `AZURE_CLIENT_ID`         | `APP_ID` from step 1                             |
| `AZURE_TENANT_ID`         | tenant id from step 1                            |
| `AZURE_SUBSCRIPTION_ID`   | subscription id from step 1                      |
| `POSTGRES_ADMIN_PASSWORD` | a strong password (≥ 8 chars, mixed)             |
| `DJANGO_SECRET_KEY`       | a long random string                             |

**Settings → Secrets and variables → Actions → Variables:**

| Variable               | Example       |
| ---------------------- | ------------- |
| `AZURE_RESOURCE_GROUP` | `bmp-rg`      |
| `AZURE_LOCATION`       | `westeurope`  |

## 3. Run the pipeline

- Push to `main` (CI runs, then CD), **or**
- **Actions → CD (Azure) → Run workflow** (manual `workflow_dispatch`).

## 4. Make the GHCR images public (one-time, after the first build)

Azure Container Apps pulls the backend images anonymously, so the packages must be public:

**Repo → Packages → `apm-interview-django` / `apm-interview-fastapi` → Package settings → Change visibility → Public.**

Re-run the CD workflow afterwards so the Container Apps can pull successfully.

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
- **PostgreSQL Flexible (B1ms)** — covered by the 12-month free offer on a new account;
  otherwise ~$12–15/mo. **Delete the resource group when you're done demoing.**
- **GHCR / GitHub Actions** — free for public repos.
