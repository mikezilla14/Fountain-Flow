$attribContent = @"
# Attribution

Fountain-Flow is a superset of the **Fountain** markup language.

- **Fountain** was created by John August and Nima Yousefi.
- Original Syntax & Specification: [fountain.io](https://fountain.io)
- Fountain-Flow extends this syntax to include state management, branching, and asset logic for interactive media.

This project is not affiliated with or endorsed by the creators of Fountain.
"@
Set-Content -Path docs/ATTRIBUTION.md -Value $attribContent -Encoding UTF8
