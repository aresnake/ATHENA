# Nettoyage des Worktrees - Plan

## Problème

10 worktrees Git actifs créent de la confusion :
- Code dupliqué partout
- Modifications perdues entre worktrees
- Claude Code charge des versions différentes selon le dossier

## Décision

**Tout centraliser sur `D:\ATHENA` (main repo)**

## Actions

### 1. Supprimer tous les worktrees

```powershell
# Lister
git worktree list

# Supprimer chaque worktree
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/distracted-jones
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/fervent-thompson
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/gracious-dubinsky
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/mystifying-lumiere
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/pedantic-boyd
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/romantic-shamir
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/suspicious-swirles
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/vigilant-sanderson
git worktree remove C:/Users/adrie/.claude-worktrees/ATHENA/vigorous-murdock

# Ou en une fois (PowerShell)
git worktree list --porcelain | Select-String "^worktree " | ForEach-Object {
    $path = $_.Line -replace "^worktree ", ""
    if ($path -notmatch "D:\\ATHENA$") {
        git worktree remove $path --force
    }
}
```

### 2. Nettoyer le dossier

```powershell
# Supprimer le dossier .claude-worktrees
Remove-Item -Recurse -Force C:\Users\adrie\.claude-worktrees\ATHENA
```

### 3. Configurer Claude Code

Dans `.claude/settings.local.json` :
```json
{
  "workingDirectory": "D:\\ATHENA"
}
```

### 4. Relancer Claude Code

```powershell
cd D:\ATHENA
claude-code
```

## Résultat attendu

- ✅ Un seul dossier : `D:\ATHENA`
- ✅ Un seul état Git
- ✅ Modifications toujours au bon endroit
- ✅ Pas de confusion

## Pour Claude Desktop

Config MCP reste la même :
```json
{
  "mcpServers": {
    "blender": {
      "command": "D:\\ATHENA\\.venv\\Scripts\\python.exe",
      "args": ["-m", "athena_mcp.mcp_core.server", "--stdio", ...]
    }
  }
}
```

Desktop charge depuis `D:\ATHENA` (le bon endroit maintenant).
