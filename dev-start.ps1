Write-Host "Starting AuroMart Development Environment..." -ForegroundColor Green
Write-Host ""

Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

Write-Host ""
Write-Host "Building containers with no cache..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml build --no-cache

Write-Host ""
Write-Host "Starting development containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d

Write-Host ""
Write-Host "Development environment is starting..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Changes will now reflect automatically without clearing cache!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
