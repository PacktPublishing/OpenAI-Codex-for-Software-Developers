[CmdletBinding()]
param([switch]$Full)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$VenvRoot = Join-Path $RepoRoot '.venv'
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'

Push-Location $RepoRoot
try {
    if ((Test-Path -LiteralPath $VenvRoot) -and -not (Test-Path -LiteralPath $VenvPython)) {
        throw 'The root .venv is incomplete. Remove only .venv and rerun scripts\bootstrap.ps1.'
    }
    if (Test-Path -LiteralPath $VenvPython) {
        $VenvVersion = & $VenvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -ne 0 -or $VenvVersion -ne '3.12') {
            throw 'The root .venv is stale or is not Python 3.12. Remove only .venv and rerun scripts\bootstrap.ps1.'
        }
        if ($Full) {
            & $VenvPython scripts\verify_workshop.py
        } else {
            & $VenvPython scripts\verify_workshop.py --structure-only
        }
    } else {
        if ($Full) {
            py -3.12 scripts\verify_workshop.py
        } else {
            py -3.12 scripts\verify_workshop.py --structure-only
        }
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    git --version
    if (Test-Path -LiteralPath (Join-Path $RepoRoot '.git')) {
        if (-not (git tag --list workshop-start)) {
            Write-Warning 'Recovery tag workshop-start is missing. Run bootstrap from a clean checkout.'
        }
    }
    if (Get-Command codex -ErrorAction SilentlyContinue) {
        codex --version
        codex login status
    } else {
        Write-Warning 'Codex CLI not found; confirm the IDE extension is installed and signed in.'
    }
}
finally {
    Pop-Location
}
