@echo off
echo Starting AuroMart Development Environment...
echo.

echo Stopping any existing containers...
docker-compose -f docker-compose.dev.yml down

echo.
echo Building containers with no cache...
docker-compose -f docker-compose.dev.yml build --no-cache

echo.
echo Starting development containers...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo Development environment is starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo Changes will now reflect automatically without clearing cache!
echo.
pause
