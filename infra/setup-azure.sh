#!/usr/bin/env bash
# =============================================================================
# One-time Azure setup for the GitHub Actions CD pipeline.
#
# Creates the passwordless OIDC identity (App Registration + federated
# credential), grants it Contributor, registers the resource providers, and
# prints every value you need to paste into GitHub.
#
# Prereqs: `az login` already done, with the right subscription selected.
# Usage:   bash infra/setup-azure.sh [owner/repo]
# Safe to re-run (idempotent).
# =============================================================================
set -euo pipefail

REPO="${1:-CDenisUa/apm-interview}"
APP_NAME="apm-interview-cd"

echo "==> Using repo: $REPO"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "==> Subscription: $SUBSCRIPTION_ID"

echo "==> Registering resource providers..."
for ns in Microsoft.App Microsoft.OperationalInsights Microsoft.DBforPostgreSQL Microsoft.Web; do
  az provider register --namespace "$ns" -o none
done

echo "==> Ensuring App Registration '$APP_NAME'..."
APP_ID=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)
if [ -z "$APP_ID" ]; then
  APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
fi
echo "    appId: $APP_ID"

echo "==> Ensuring service principal..."
az ad sp show --id "$APP_ID" >/dev/null 2>&1 || az ad sp create --id "$APP_ID" -o none

echo "==> Ensuring federated credential (repo:$REPO @ main)..."
if ! az ad app federated-credential list --id "$APP_ID" \
       --query "[?name=='github-main'].name" -o tsv | grep -q github-main; then
  az ad app federated-credential create --id "$APP_ID" --parameters "{
    \"name\":\"github-main\",
    \"issuer\":\"https://token.actions.githubusercontent.com\",
    \"subject\":\"repo:${REPO}:ref:refs/heads/main\",
    \"audiences\":[\"api://AzureADTokenExchange\"]
  }" -o none
fi

echo "==> Granting Contributor on the subscription..."
az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope "/subscriptions/$SUBSCRIPTION_ID" -o none 2>/dev/null || true

# Suggested strong values for the two app secrets.
PG_PW="Bmp$(openssl rand -hex 10)!"
DJ_KEY=$(openssl rand -hex 32)

cat <<EOF

============================================================================
✅ Azure side is ready. Now paste these into GitHub:

GitHub → Settings → Secrets and variables → Actions → Secrets
  AZURE_CLIENT_ID          = $APP_ID
  AZURE_TENANT_ID          = $TENANT_ID
  AZURE_SUBSCRIPTION_ID    = $SUBSCRIPTION_ID
  POSTGRES_ADMIN_PASSWORD  = $PG_PW
  DJANGO_SECRET_KEY        = $DJ_KEY

GitHub → ... → Variables
  AZURE_RESOURCE_GROUP     = bmp-rg
  AZURE_LOCATION           = westeurope

Then: Actions → "CD (Azure)" → Run workflow.
After the first build, make the GHCR packages public and re-run.
============================================================================
EOF
