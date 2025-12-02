#!/bin/bash
# Install Redis in WSL Ubuntu-24.04

echo "=========================================="
echo "Installing Redis"
echo "=========================================="
echo ""

sudo apt-get update
sudo apt-get install -y redis-server redis-tools

echo ""
echo "Testing installation..."
redis-server --version

echo ""
echo "Redis installed successfully!"
