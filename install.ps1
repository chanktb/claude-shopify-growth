#Requires -Version 5.1
<#
.SYNOPSIS
  Install the claude-collection-optimizer skills + scripts into ~/.claude.
.DESCRIPTION
  Copies the four collection-* skills to ~/.claude/skills/ and the helper
  scripts to ~/.claude/scripts/ so Claude Code loads them by slash command.
  Re-run after pulling updates. Your knowledge-base/ and .env stay in the repo.
#>
param(
  [string]$ClaudeHome = (Join-Path $env:USERPROFILE ".claude")
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path

$skillsDst  = Join-Path $ClaudeHome "skills"
$scriptsDst = Join-Path $ClaudeHome "scripts"
New-Item -ItemType Directory -Force -Path $skillsDst, $scriptsDst | Out-Null

Write-Host "Installing claude-collection-optimizer -> $ClaudeHome" -ForegroundColor Cyan

# Skills
Get-ChildItem -Directory (Join-Path $repo "skills") | ForEach-Object {
  $dst = Join-Path $skillsDst $_.Name
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  Copy-Item -Recurse -Force $_.FullName $dst
  Write-Host "  skill  $($_.Name)" -ForegroundColor Green
}

# Scripts
Get-ChildItem (Join-Path $repo "scripts") -Filter *.py | ForEach-Object {
  Copy-Item -Force $_.FullName (Join-Path $scriptsDst $_.Name)
  Write-Host "  script $($_.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done. In Claude Code, run /reload-plugins or restart the session." -ForegroundColor Cyan
Write-Host "Optional: create knowledge-base/INDEX.md + pk-*.md, and copy" -ForegroundColor DarkGray
Write-Host "config.example.env to .env if you want publish notifications." -ForegroundColor DarkGray
