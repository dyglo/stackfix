# StackFix Relay

This relay provides OpenAI-compatible endpoints and backs StackFix's zero-config mode.

## Run locally

```bash
pip install -e ".[relay]"
export STACKFIX_UPSTREAM_BASE_URL="https://api.tokenfactory.nebius.com/v1"
export STACKFIX_UPSTREAM_API_KEY="..."
export STACKFIX_UPSTREAM_MODEL="openai/gpt-oss-120b"
export STACKFIX_REDIS_URL="redis://localhost:6379/0"
export STACKFIX_RELAY_SECRET="dev-insecure"
python -m relay.app
```

## Docker Compose

```bash
cp relay/.env.relay.example relay/.env.relay
# edit relay/.env.relay
./scripts/deploy_vps.sh
```