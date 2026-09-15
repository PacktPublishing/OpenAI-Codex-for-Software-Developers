[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Foundations-start','Repository-Orientation-start','Planning-Tests-start','Implementation-start','Debugging-Extension-start','Review-Refactor-start','Handoff-start')]
    [string]$Stage,
    [switch]$ConfirmReset
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Target = (Resolve-Path (Join-Path $RepoRoot $Stage)).Path
if (-not $Target.StartsWith($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Resolved stage is outside the repository root.'
}

function Remove-StageArtifact {
    param([Parameter(Mandatory = $true)][string]$ArtifactPath)
    if (-not (Test-Path -LiteralPath $ArtifactPath)) { return }
    $FullPath = [System.IO.Path]::GetFullPath($ArtifactPath)
    $StagePrefix = $Target.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $FullPath.StartsWith($StagePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove path outside the selected stage: $FullPath"
    }
    if ([System.IO.Directory]::Exists($FullPath)) {
        [System.IO.Directory]::Delete($FullPath, $true)
    } else {
        [System.IO.File]::Delete($FullPath)
    }
}

Push-Location $RepoRoot
try {
    if (-not (git tag --list workshop-start)) {
        throw 'Recovery tag workshop-start is missing. Run bootstrap from a clean checkout before using reset.'
    }
    Write-Host "Changes that would be discarded from ${Stage}:"
    git status --short -- $Stage
    git clean -nd -- $Stage
    if (-not $ConfirmReset) {
        Write-Host 'Preview only; nothing changed. Rerun with -ConfirmReset to restore this stage to workshop-start.' -ForegroundColor Yellow
        return
    }
    git restore --source=workshop-start --staged --worktree -- $Stage
    git clean -fd -- $Stage
    @('instance', '.pytest_cache', '.ruff_cache', '.env') | ForEach-Object {
        Remove-StageArtifact (Join-Path $Target $_)
    }
    Get-ChildItem -LiteralPath $Target -Recurse -Directory -Force -Filter '__pycache__' |
        Sort-Object FullName -Descending |
        ForEach-Object { Remove-StageArtifact $_.FullName }
    Get-ChildItem -LiteralPath $Target -Recurse -File -Force |
        Where-Object { $_.Extension -in @('.pyc', '.pyo') } |
        ForEach-Object { Remove-StageArtifact $_.FullName }
    Write-Host "$Stage restored to workshop-start." -ForegroundColor Green
}
finally {
    Pop-Location
}
