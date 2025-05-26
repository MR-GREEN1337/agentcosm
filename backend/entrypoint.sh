#!/bin/bash

# Ensure runtime environment variable ALLOWED_ORIGINS exists
if [ -z "$ALLOWED_ORIGINS" ]; then
  echo "ALLOWED_ORIGINS is not set"
  exit 1
fi

# Remove brackets and quotes, then split by comma
cleaned=$(echo "$ALLOWED_ORIGINS" | tr -d '[]"')
IFS=',' read -ra ORIGINS <<< "$cleaned"

# Build the args
ARGS=""
for origin in "${ORIGINS[@]}"; do
  trimmed=$(echo "$origin" | xargs)  # Trim whitespace
  ARGS+=" --allow_origins $trimmed"
done

# Run the server
exec adk api_server $ARGS