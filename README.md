$readmeContent = @"
# Fountain-Flow

A superset of the Fountain screenplay syntax designed for Interactive Fiction, Visual Novels, and RPGs.
It adds logic for:
- State Management (~)
- Branching Decisions (?)
- Asset Injection (!)
"@
Set-Content -Path README.md -Value $readmeContent -Encoding UTF8