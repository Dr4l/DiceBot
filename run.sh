#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

if [ ! -s ".env" ] || ! grep -q '^DISCORD_TOKEN=.' .env; then
    printf "Enter your Discord Bot Token (not Application ID or Server ID): "
    read -r DISCORD_TOKEN
    if [ -z "$DISCORD_TOKEN" ]; then
        echo "A token is required."
        exit 1
    fi
    printf 'DISCORD_TOKEN=%s\n' "$DISCORD_TOKEN" > .env
    echo "Token saved to .env. It will not be requested again."
fi

echo "Installing or checking dependencies..."
.venv/bin/python -m pip install -q -r requirements.txt

echo "Starting bot..."
exec .venv/bin/python bot.py