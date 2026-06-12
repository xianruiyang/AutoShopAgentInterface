# AutoShop Skill Path Policy

This development knowledge file defines the path and privacy rules for the packaged `autoshop-agent-interface` skill.

## Packaged Path Rules

- Inside the skill package, reference bundled files relative to the skill root:
  - `scripts/autoshop-agent.exe`
  - `references/AutoShopAgentWorkflow.md`
  - `references/AutoShopWorkspaceJsonReference.md`
  - `references/AutoShopCliCommands.md`
  - `references/AutoShopEthercatSlaveTemplates.md`
  - `references/AutoShopH5uQuickReference.md`
  - `references/AutoShopH5uEasyProgrammingApplicationManual.md`
  - `references/AutoShopH5uPlcInstructionManualCn.md`
  - `references/AutoShopH5uSeriesUserManualCn.md`
  - `references/AutoShopH5uSeriesBrochureEn.md`
- In PowerShell examples, invoke the bundled CLI as:

```powershell
.\scripts\autoshop-agent.exe <command>
```

- Do not include machine-local absolute paths in packaged skill files. Avoid examples containing drive letters, user profiles, host names, workspace roots, or real bench IP addresses.
- Use placeholders for user/workspace paths:
  - `<project-dir>`
  - `<project-copy-dir>`
  - `<workspace-dir>`
  - `<archive-dir>`
  - `<state-json>`
  - `<tmp-dir>`
  - `<device-library-dir>`
  - `<hardware-config.json>`
  - `<plc-ip>`
  - `<profile-name>`
- Keep implementation and maintenance paths in development metadata only. Do not publish them into the installed skill.

## Reference Sync

Development source files under `knowledge/` are copied into the packaged skill under `references/` only after local edits are complete. The packaged skill and installed Codex skill must not be the source of truth.

## Validation

Before sync is complete:

1. Run `quick_validate.py` on the packaged skill and installed skill.
2. Scan packaged text files for drive-letter paths, user profile paths, workspace roots, host names, real bench IP addresses, and stale product names.

3. Confirm intended placeholder examples still show the command shape clearly.
