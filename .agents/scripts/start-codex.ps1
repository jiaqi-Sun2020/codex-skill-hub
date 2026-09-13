[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArgs
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$required = @(
    '.agents\AGENTS.md',
    '.agents\memory\MEMORY.md',
    '.codex\config.toml',
    '.codex\hooks.json',
    '.codex\hooks\load_project_agents.py'
)

foreach ($relativePath in $required) {
    $candidate = Join-Path $projectRoot $relativePath
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "Required Codex bootstrap file is missing: $candidate"
    }
}

$codex = Get-Command codex -ErrorAction Stop
& $codex.Source --cd $projectRoot @CodexArgs
exit $LASTEXITCODE
