#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
if [ ! -d "node_modules" ]; then
  echo "Installing record-screen-tool dependencies..."
  npm install --silent
fi
