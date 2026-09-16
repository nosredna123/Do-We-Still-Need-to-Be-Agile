#!/bin/bash

set -e

echo "Initializing Database..."
python scripts/create_db.py

echo "Starting Server..."
exec "$@"