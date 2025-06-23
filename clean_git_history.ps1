# PowerShell script to remove sensitive files from Git history
Write-Host "🔒 Git Security Cleanup Script 🔒" -ForegroundColor Cyan
Write-Host "This script will help remove API keys and sensitive data from git history"
Write-Host "Warning: This will rewrite git history. All team members will need to re-clone the repository.`n" -ForegroundColor Yellow

$confirm = Read-Host "Do you want to continue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Operation cancelled."
    exit 0
}

Write-Host "Creating backup branch of current state..." -ForegroundColor Green
git checkout -b backup-before-cleaning

$mainBranch = "master"
$checkMainBranch = git branch --list master
if (!$checkMainBranch) {
    $mainBranch = "main"
}

Write-Host "Checking out main branch..." -ForegroundColor Green
git checkout $mainBranch

Write-Host "Removing sensitive .env file from git history..." -ForegroundColor Green
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all

Write-Host "Removing any other potential sensitive files..." -ForegroundColor Green
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch **/credentials.* **/*key* **/*secret*" --prune-empty --tag-name-filter cat -- --all

Write-Host "Running garbage collection to remove old objects..." -ForegroundColor Green
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "`n✅ Repository cleaned of sensitive data" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Force push to GitHub: git push origin --force --all" -ForegroundColor White
Write-Host "2. Make sure .env and other sensitive files are in .gitignore" -ForegroundColor White
Write-Host "3. Tell all team members to re-clone the repository" -ForegroundColor White
Write-Host "`nRemember to update your API keys as they may have been compromised." -ForegroundColor Yellow
