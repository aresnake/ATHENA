# Nettoyage automatique des worktrees
Write-Host "Suppression de tous les worktrees sauf le main repo..." -ForegroundColor Yellow

git worktree list --porcelain | Select-String "^worktree " | ForEach-Object { 
    $path = $_.Line -replace "^worktree ", ""
    if ($path -notmatch "D:\ATHENA$") {
        Write-Host "Suppression: $path" -ForegroundColor Cyan
        git worktree remove $path --force
    }
}

Write-Host "`nNettoyage du dossier .claude-worktrees..." -ForegroundColor Yellow
if (Test-Path "C:\Users\adrie\.claude-worktrees\ATHENA") {
    Remove-Item -Recurse -Force "C:\Users\adrie\.claude-worktrees\ATHENA"
    Write-Host "Dossier supprimé" -ForegroundColor Green
}

Write-Host "`nWorktrees restants:" -ForegroundColor Yellow
git worktree list

Write-Host "`nTerminé! Utilisez maintenant uniquement D:\ATHENA" -ForegroundColor Green
