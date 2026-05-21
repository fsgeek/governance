# Pre-reg #14 expanded-vintage replication: Windows-side recovery runner for 2020Q2 + 2012Q1.
#
# Why this script exists: WSL recovery attempts for 2020Q2 (exit 1) and 2012Q1
# (exit 137, OOM) hit memory pressure inside WSL2's ~125 GB cap. Windows native
# sees 256 GB physical, so per-vintage load fits comfortably -- but the FM-load
# discipline from pre-reg #11 (per scripts/fm_rich_policy_vocab_adequacy_test.py
# L16-18, "STRICTLY SERIAL ... never two in parallel") still applies: we run
# them sequentially, not in parallel, to avoid overlapping the ~30+ GB
# pandas.read_csv peaks on a host shared with other workloads.
#
# Flags: --no-placebo --no-eps-arm skip the per-vintage script-internal
# sensitivity arms inherited from pre-reg #11. They do NOT correspond to
# pre-reg #14 §4a (corpus-level label permutation) or §4b (per-vintage
# hyperparameter sensitivity, satisfied by completed vintages). Verified
# 2026-05-18 that silence_manufacture_test.py and frame_evocation_test.py do
# not consume the placebo/eps_arm output fields. Deviation declared in
# docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md §8.
#
# PYTHONPATH: per scripts/fm_rich_policy_vocab_adequacy_test.py L30 canonical
# usage, the per-vintage script expects PYTHONPATH=. (or equivalent) so it can
# resolve `from policy.encoder import load_policy`. Without it, Python prepends
# only the script's own directory to sys.path and the import fails immediately.
#
# Expected runtime: ~20-30h sequential. Run in a dedicated PS window; script
# blocks until both finish and prints a DONE line.

$ErrorActionPreference = "Stop"
Set-Location "C:\Users\TonyMason\source\repos\governance"
$env:PYTHONPATH = (Get-Location).Path

$python = ".\.venv\Scripts\python.exe"
$logsDir = "runs\expanded-vintage-logs"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

$startedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"# Windows batch started: $startedAt" | Out-File "$logsDir\windows.status"
"# Python: $python" | Add-Content "$logsDir\windows.status"
"# PYTHONPATH: $env:PYTHONPATH" | Add-Content "$logsDir\windows.status"
"# Mode: SEQUENTIAL (FM-load discipline; result-note §8b)" | Add-Content "$logsDir\windows.status"

# --- Vintage 1: 2020Q2 ----------------------------------------------------------
$start2020 = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"2020Q2 launching at $start2020" | Add-Content "$logsDir\windows.status"
Write-Host "[$start2020] Launching 2020Q2..."

$p2020Q2 = Start-Process -FilePath $python `
    -ArgumentList "scripts\fm_rich_policy_vocab_adequacy_test.py", "--vintage", "2020Q2", "--no-placebo", "--no-eps-arm" `
    -RedirectStandardOutput "$logsDir\2020Q2.log" `
    -RedirectStandardError "$logsDir\2020Q2.err" `
    -PassThru -NoNewWindow
"# 2020Q2 PID=$($p2020Q2.Id) at $start2020" | Add-Content "$logsDir\windows.status"

$p2020Q2.WaitForExit()
$end2020 = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"2020Q2 exited code $($p2020Q2.ExitCode) at $end2020" | Add-Content "$logsDir\windows.status"
Write-Host "[$end2020] 2020Q2 exited with code $($p2020Q2.ExitCode)"

# --- Vintage 2: 2012Q1 ----------------------------------------------------------
$start2012 = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"2012Q1 launching at $start2012" | Add-Content "$logsDir\windows.status"
Write-Host "[$start2012] Launching 2012Q1..."

$p2012Q1 = Start-Process -FilePath $python `
    -ArgumentList "scripts\fm_rich_policy_vocab_adequacy_test.py", "--vintage", "2012Q1", "--no-placebo", "--no-eps-arm" `
    -RedirectStandardOutput "$logsDir\2012Q1.log" `
    -RedirectStandardError "$logsDir\2012Q1.err" `
    -PassThru -NoNewWindow
"# 2012Q1 PID=$($p2012Q1.Id) at $start2012" | Add-Content "$logsDir\windows.status"

$p2012Q1.WaitForExit()
$end2012 = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
"2012Q1 exited code $($p2012Q1.ExitCode) at $end2012" | Add-Content "$logsDir\windows.status"
Write-Host "[$end2012] 2012Q1 exited with code $($p2012Q1.ExitCode)"

"# Windows batch done: $end2012" | Add-Content "$logsDir\windows.status"

Write-Host ""
Write-Host "DONE."
Write-Host "  2020Q2 exit=$($p2020Q2.ExitCode); expected JSON: runs\fm_rich_policy_vocab_adequacy_2020Q2.json"
Write-Host "  2012Q1 exit=$($p2012Q1.ExitCode); expected JSON: runs\fm_rich_policy_vocab_adequacy_2012Q1.json"
Write-Host ""
Write-Host "Tell Claude: 'Windows batch done -- 2020Q2 exit=<code>, 2012Q1 exit=<code>'"
