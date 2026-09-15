[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'

Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Git is required. Install Git, reopen the terminal, and rerun bootstrap.'
    }

    $BootstrapPython = $null
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $BootstrapPython = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
    }
    if (-not $BootstrapPython -and (Get-Command python -ErrorAction SilentlyContinue)) {
        $CandidateVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($LASTEXITCODE -eq 0 -and $CandidateVersion -eq '3.12') {
            $BootstrapPython = & python -c "import sys; print(sys.executable)"
        }
    }
    if (-not $BootstrapPython) {
        throw 'Python 3.12 is required. Install it from python.org, reopen the terminal, and rerun bootstrap.'
    }

    if (-not (Test-Path -LiteralPath $VenvPython)) {
        if (Test-Path -LiteralPath (Join-Path $RepoRoot '.venv')) {
            throw 'The existing .venv is incomplete. Move it aside or remove it, then rerun bootstrap.'
        }
        & $BootstrapPython -m venv .venv
    }

    $VenvVersion = & $VenvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if ($LASTEXITCODE -ne 0 -or $VenvVersion -ne '3.12') {
        throw 'The existing .venv is stale or is not Python 3.12. Remove only the root .venv directory, then rerun bootstrap.'
    }

    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r requirements.txt

    & $VenvPython scripts\verify_workshop.py
    if ($LASTEXITCODE -ne 0) { throw 'Workshop verification failed.' }

    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.git'))) {
        git init -b main
        if (-not (git config user.name)) { git config user.name 'Workshop Student' }
        if (-not (git config user.email)) { git config user.email 'student@local.invalid' }
        git add .
        git commit -m 'Workshop start'
        git tag workshop-start
    } elseif (-not (git tag --list workshop-start)) {
        if (git status --porcelain --untracked-files=normal) {
            throw 'Cannot create the workshop-start recovery tag because tracked files already differ. Start from a clean clone or preserve your work and ask the instructor.'
        }
        git tag workshop-start HEAD
    } elseif ((git rev-parse workshop-start) -ne (git rev-parse HEAD)) {
        if (git status --porcelain --untracked-files=normal) {
            throw 'Cannot update the stale workshop-start tag because tracked files already differ. Use a clean clone or ask the instructor.'
        }
        git tag --force workshop-start HEAD
    }

    Write-Host ''
    Write-Host 'Setup complete.' -ForegroundColor Green
    Write-Host 'Activate: .\.venv\Scripts\Activate.ps1'
    Write-Host 'Then open README.md and begin Lab 1 in Foundations-start.'
    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
        Write-Warning 'Codex CLI was not found. This is okay if you will use the signed-in IDE extension.'
    }
}
finally {
    Pop-Location
}
