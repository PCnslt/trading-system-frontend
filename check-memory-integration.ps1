# Memory Integration Check Script
# Checks if memory skills are working together properly

Write-Host "🧠 Memory Integration Check" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# 1. Check ByteRover
Write-Host "1. ByteRover Status:" -ForegroundColor Yellow
$brvPath = "C:\Users\pcnsl\.openclaw\workspace\skills\byterover"
if (Test-Path $brvPath) {
    Write-Host "   ✅ Installed at: $brvPath" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not installed" -ForegroundColor Red
}

# 2. Check Humanizer
Write-Host "2. Humanizer Status:" -ForegroundColor Yellow
$humanizerPath = "C:\Users\pcnsl\.openclaw\workspace\skills\humanizer"
if (Test-Path $humanizerPath) {
    Write-Host "   ✅ Installed at: $humanizerPath" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not installed" -ForegroundColor Red
}

# 3. Check Elite Longterm Memory
Write-Host "3. Elite Longterm Memory:" -ForegroundColor Yellow
$elitePath = "C:\Users\pcnsl\.openclaw\workspace\skills\elite-longterm-memory"
if (Test-Path $elitePath) {
    Write-Host "   ✅ Installed at: $elitePath" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not installed" -ForegroundColor Red
}

# 4. Check Actual Self-Improvement
Write-Host "4. Actual Self-Improvement:" -ForegroundColor Yellow
$improvementPath = "C:\Users\pcnsl\.openclaw\workspace\skills\actual-self-improvement"
if (Test-Path $improvementPath) {
    Write-Host "   ✅ Installed at: $improvementPath" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not installed" -ForegroundColor Red
}

# 5. Check Memory Files
Write-Host "5. Memory Files:" -ForegroundColor Yellow
$memoryDir = "C:\Users\pcnsl\.openclaw\workspace\memory"
if (Test-Path $memoryDir) {
    $files = Get-ChildItem $memoryDir -File | Measure-Object
    Write-Host "   ✅ $($files.Count) memory files" -ForegroundColor Green
} else {
    Write-Host "   ❌ No memory directory" -ForegroundColor Red
}

# 6. Check MEMORY.md
Write-Host "6. MEMORY.md:" -ForegroundColor Yellow
$memoryFile = "C:\Users\pcnsl\.openclaw\workspace\MEMORY.md"
if (Test-Path $memoryFile) {
    $size = (Get-Item $memoryFile).Length
    Write-Host "   ✅ Exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Missing" -ForegroundColor Red
}

# 7. Check Today's Memory
Write-Host "7. Today's Memory:" -ForegroundColor Yellow
$today = Get-Date -Format "yyyy-MM-dd"
$todayFile = "C:\Users\pcnsl\.openclaw\workspace\memory\$today.md"
if (Test-Path $todayFile) {
    $size = (Get-Item $todayFile).Length
    Write-Host "   ✅ Today's file exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  No file for today" -ForegroundColor Yellow
}

# 8. Integration Status
Write-Host ""
Write-Host "📊 Integration Status:" -ForegroundColor Magenta
Write-Host "-------------------" -ForegroundColor Magenta

$skills = @("ByteRover", "Humanizer", "Elite Memory", "Self-Improvement")
$installed = 0
foreach ($skill in $skills) {
    $path = "C:\Users\pcnsl\.openclaw\workspace\skills\" + $skill.ToLower().Replace(" ", "-")
    if (Test-Path $path) { $installed++ }
}

$integrationScore = [math]::Round(($installed / $skills.Count) * 100)
Write-Host "Skills installed: $installed/$($skills.Count) ($integrationScore`%)" -ForegroundColor Cyan

if ($integrationScore -ge 75) {
    Write-Host "✅ Integration: GOOD" -ForegroundColor Green
} elseif ($integrationScore -ge 50) {
    Write-Host "⚠️  Integration: FAIR" -ForegroundColor Yellow
} else {
    Write-Host "❌ Integration: POOR" -ForegroundColor Red
}

# 9. Recommendations
Write-Host ""
Write-Host "🎯 Recommendations:" -ForegroundColor Green
Write-Host "-----------------" -ForegroundColor Green

if (-not (Test-Path $todayFile)) {
    Write-Host "1. Create today's memory file: memory/$today.md" -ForegroundColor Yellow
}

if ($integrationScore -lt 100) {
    $missing = $skills.Count - $installed
    Write-Host "2. Install $missing missing memory skill(s)" -ForegroundColor Yellow
}

Write-Host "3. Run daily: ByteRover query + curate + humanizer" -ForegroundColor Yellow
Write-Host "4. Weekly: Run capability-evolver for improvements" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ Integration check complete" -ForegroundColor Green