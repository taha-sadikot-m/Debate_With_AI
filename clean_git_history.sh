#!/bin/bash

# This script helps clean sensitive data from git history

echo "🔒 Git Security Cleanup Script 🔒"
echo "This script will help remove API keys and sensitive data from git history"
echo "Warning: This will rewrite git history. All team members will need to re-clone the repository."
echo

read -p "Do you want to continue? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Operation cancelled."
    exit 0
fi

echo "Creating backup branch of current state..."
git checkout -b backup-before-cleaning

echo "Checking out main branch..."
git checkout master || git checkout main

echo "Removing sensitive .env file from git history..."
git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch .env" \
    --prune-empty --tag-name-filter cat -- --all

echo "Removing any other potential sensitive files..."
git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch **/credentials.* **/*key* **/*secret*" \
    --prune-empty --tag-name-filter cat -- --all

echo "Running garbage collection to remove old objects..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo
echo "✅ Repository cleaned of sensitive data"
echo
echo "Next steps:"
echo "1. Force push to GitHub: git push origin --force --all"
echo "2. Make sure .env and other sensitive files are in .gitignore"
echo "3. Tell all team members to re-clone the repository"
echo
echo "Remember to update your API keys as they may have been compromised."
