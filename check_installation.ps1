# RFID Database System - Installation Check
# This script helps verify your setup is complete

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RFID Database System - Installation Checker" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: PostgreSQL Installation
Write-Host "1. Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>$null
    if ($pgVersion) {
        Write-Host "   ✅ PostgreSQL is installed: $pgVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ PostgreSQL not found in PATH" -ForegroundColor Red
        Write-Host "      Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host "   ❌ PostgreSQL not installed" -ForegroundColor Red
    Write-Host "      Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    $allGood = $false
}

# Check 2: PostgreSQL Service
Write-Host ""
Write-Host "2. Checking PostgreSQL service..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService) {
    if ($pgService.Status -eq "Running") {
        Write-Host "   ✅ PostgreSQL service is running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  PostgreSQL service is installed but not running" -ForegroundColor Yellow
        Write-Host "      Starting service..." -ForegroundColor Yellow
        try {
            Start-Service $pgService.Name
            Write-Host "   ✅ Service started successfully" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ Failed to start service. Please start it manually." -ForegroundColor Red
            $allGood = $false
        }
    }
} else {
    Write-Host "   ⚠️  PostgreSQL service not found" -ForegroundColor Yellow
    Write-Host "      This might be normal if PostgreSQL was installed manually" -ForegroundColor Gray
}

# Check 3: Python Installation
Write-Host ""
Write-Host "3. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "   ✅ Python is installed: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Python not found" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   ❌ Python not installed" -ForegroundColor Red
    $allGood = $false
}

# Check 4: pip Installation
Write-Host ""
Write-Host "4. Checking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>$null
    if ($pipVersion) {
        Write-Host "   ✅ pip is installed: $pipVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ pip not found" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   ❌ pip not installed" -ForegroundColor Red
    $allGood = $false
}

# Check 5: Required Python packages
Write-Host ""
Write-Host "5. Checking Python packages..." -ForegroundColor Yellow

$requiredPackages = @(
    "pyserial",
    "flask",
    "flask-socketio",
    "psycopg2-binary"
)

$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>$null
    if ($installed) {
        Write-Host "   ✅ $package is installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $package is NOT installed" -ForegroundColor Red
        $missingPackages += $package
        $allGood = $false
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "   Missing packages detected. Install them with:" -ForegroundColor Yellow
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan
}

# Check 6: Database configuration
Write-Host ""
Write-Host "6. Checking database configuration..." -ForegroundColor Yellow
if (Test-Path "database.py") {
    Write-Host "   ✅ database.py found" -ForegroundColor Green
    
    $dbContent = Get-Content "database.py" -Raw
    if ($dbContent -match "host='localhost'") {
        Write-Host "   ✅ Database host configured: localhost" -ForegroundColor Green
    }
    if ($dbContent -match "port=5432") {
        Write-Host "   ✅ Database port configured: 5432" -ForegroundColor Green
    }
    if ($dbContent -match "username='postgres'") {
        Write-Host "   ✅ Database username configured: postgres" -ForegroundColor Green
    }
    if ($dbContent -match "password='123'") {
        Write-Host "   ⚠️  Database password: 123 (default)" -ForegroundColor Yellow
        Write-Host "      Consider changing this in production!" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ database.py not found" -ForegroundColor Red
    $allGood = $false
}

# Check 7: Other required files
Write-Host ""
Write-Host "7. Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "main.py",
    "reader.py",
    "tag_writer.py",
    "web_interface.py",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $allGood = $false
    }
}

# Final Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "  ✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your system is ready to use! Next steps:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  1. Test database connection:" -ForegroundColor White
    Write-Host "     python test_database.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  2. Start the tag writer:" -ForegroundColor White
    Write-Host "     python tag_writer.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  3. Or start the full system:" -ForegroundColor White
    Write-Host "     python main.py" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  ⚠️  SOME CHECKS FAILED" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please fix the issues above before continuing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor White
    Write-Host "  • Install PostgreSQL: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host "  • Install Python packages: pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "  • Make sure PostgreSQL service is running" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "For detailed setup instructions, see:" -ForegroundColor White
Write-Host "  • QUICK_START_DATABASE.md" -ForegroundColor Cyan
Write-Host "  • README_DATABASE.md" -ForegroundColor Cyan
Write-Host ""

# Pause at the end
Read-Host "Press Enter to exit"
