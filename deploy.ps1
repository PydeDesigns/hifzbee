Write-Host "🚀 Deploying HifzBee changes..." -ForegroundColor Cyan

# Add all changes to git
Write-Host "📦 Adding changes to git..." -ForegroundColor Yellow
& 'C:\Program Files\Git\cmd\git.exe' add .

# Get commit message from user
$commitMessage = Read-Host "Enter commit message"

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
& 'C:\Program Files\Git\cmd\git.exe' commit -m $commitMessage

# Push to GitHub
Write-Host "⬆️ Pushing to GitHub..." -ForegroundColor Yellow
& 'C:\Program Files\Git\cmd\git.exe' push origin main

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
Write-Host "Your changes are now on GitHub. Render will automatically deploy the updates." -ForegroundColor Cyan
Write-Host "You can check the deployment status at: https://dashboard.render.com" -ForegroundColor Cyan

Read-Host "`nPress Enter to exit"
