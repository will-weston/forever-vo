param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('generate', 'ingest', 'classicdb', 'wdbcache', 'build_voice_references', 'tts_smoke', 'apicheck', 'tirisfal', 'audition_undead', 'audition_elreth', 'audition_rattlecages')]
    [string]$Tool,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ToolArguments
)
$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$ffmpegPath = Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '.local-tools\ffmpeg') -Filter ffmpeg.exe -Recurse | Select-Object -First 1
if (-not $ffmpegPath) { throw 'Local FFmpeg installation is missing.' }
$priorPath = $env:PATH
$priorWow = $env:WOW_DIR
$priorData = $env:FOREVER_VO_DATA_DIR
$priorTelemetry = $env:HF_HUB_DISABLE_TELEMETRY
$priorOffline = $env:HF_HUB_OFFLINE
$priorEncoding = $env:PYTHONIOENCODING
$priorUnbuffered = $env:PYTHONUNBUFFERED
$priorProgress = $env:TQDM_DISABLE
try {
    $env:PATH = $ffmpegPath.DirectoryName + ';' + $priorPath
    $env:WOW_DIR = 'C:\Program Files (x86)\World of Warcraft'
    $env:FOREVER_VO_DATA_DIR = Join-Path $PSScriptRoot '.local-state'
    $env:HF_HUB_DISABLE_TELEMETRY = '1'
    # Initial model download has been completed; keep using that cached snapshot.
    $env:HF_HUB_OFFLINE = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUNBUFFERED = '1'
    $env:TQDM_DISABLE = '1'
    Push-Location $PSScriptRoot
    try {
        & $pythonPath (Join-Path $PSScriptRoot "tools\$Tool.py") @ToolArguments
        if ($LASTEXITCODE -ne 0) { throw "$Tool failed with exit code $LASTEXITCODE" }
    } finally { Pop-Location }
} finally {
    $env:PATH = $priorPath
    $env:WOW_DIR = $priorWow
    $env:FOREVER_VO_DATA_DIR = $priorData
    $env:HF_HUB_DISABLE_TELEMETRY = $priorTelemetry
    $env:HF_HUB_OFFLINE = $priorOffline
    $env:PYTHONIOENCODING = $priorEncoding
    $env:PYTHONUNBUFFERED = $priorUnbuffered
    $env:TQDM_DISABLE = $priorProgress
}
