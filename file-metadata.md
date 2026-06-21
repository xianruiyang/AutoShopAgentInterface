# File Metadata

- `README.md`: Public repository overview, supported AutoShop version, workflow boundaries, and usage notes.
- `README.md` Development Source section: records that this package is synced from a separate development source and must not be edited as the source of truth.
- `LICENSE`: MIT license for the distributable package.
- `.editorconfig`: Text-file encoding policy for this distributable package when opened directly; declares UTF-8 for Markdown, JSON, PowerShell, ST, and related text files.
- `.vscode/settings.json`: VSCode workspace setting forcing `files.encoding=utf8` and disabling encoding auto-guessing when this package folder is opened directly.
- `SKILL.md`: Codex skill instructions and operational rules for the bundled CLI.
- `scripts/autoshop-agent.exe`: Packaged CLI binary, currently `v0.8.137`.
- `references/`: Detailed command, format, UI refresh, testing, EtherCAT slave template references, motion-axis `outputDevice` JSON binding, CANLink `programConfig` editing including existing slave station-number migration and sampled send/receive add-edit-delete, explicit CANLink `slaves` omission/add-delete boundary, dynamic CANopen workspace path, raw `canopen.data` / `canopen.up` preservation, CANopen EDS catalog export, and writable existing CANopen `dataConfig.objectTable` values.
- `references/AutoShopEthercatSlaveTemplates.md`: Reusable JSON template reference for EtherCAT `templateKey` clone, `toolboxName` device-library add, current verified `IS620N_ECAT_v2.6.8`, and `Axis_0` binding parameters.
- `references/AutoShopSkillPathPolicy.md`: Path/privacy policy for packaged skill resources and placeholders.
- `references/AutoShopH5uQuickReference.md`: H5U AutoShop quick reference for communication, modules, EtherCAT, EtherNet/IP, and CAN(CANLink).
- `references/AutoShopAgentWorkflow.md`: Split operational workflow reference for workspace export/apply, AutoShop UI actions, real hardware boundaries, and validation.
- `references/AutoShopWorkspaceJsonReference.md`: Split workspace JSON reference for POU, variables, interrupts, H5U modules, EtherCAT, motion axes, EtherNet/IP, CAN(CANLink), CANopen catalog, and writable existing CANopen objectTable values.
- `references/AutoShopH5uEasyProgrammingApplicationManual.md`: Bundled Markdown conversion of the AutoShop H5U/Easy programming and application guide.
- `references/AutoShopH5uPlcInstructionManualCn.md`: Bundled Markdown conversion of the H5U PLC instruction manual.
- `references/AutoShopH5uSeriesUserManualCn.md`: Bundled H5U series user manual Markdown.
- `references/AutoShopH5uSeriesBrochureEn.md`: Bundled H5U brochure/spec overview Markdown.

