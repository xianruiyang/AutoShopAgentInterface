# AutoShop Lite ST Container Notes

Use these notes when maintaining or diagnosing `scripts/autoshop-agent.exe`.

## Verified Container Shape

The tested AutoShop Lite project stores `MAIN.ST`, `INT_001.ST`, and `SBR_001.ST` as binary containers, not plain text. Each file starts with ASCII `AutoShop`.

The editable ST source body is the final MFC-style `CString` block before four trailing zero bytes.

Length header rules:

- `length < 0xFF`: one byte length.
- `length < 0xFFFF`: `FF` plus a two-byte little-endian length.
- longer text: `FF FF FF` plus a four-byte little-endian length.

The CLI preserves all bytes outside that final text block.

## Encoding

Project embedded ST text defaults to GB2312/CP936.

Exported txt defaults to UTF-8.

Change these only through JSON config or CLI flags unless a project proves a different encoding.

## Safety Boundary

Supported:

- List existing `*.ST` program containers.
- Export embedded ST source text.
- Import txt into an existing `*.ST` container.

Not supported:

- Creating or deleting POU nodes.
- Editing `.hcp` project tables.
- Editing variable tables, hardware configuration, or cross-reference data.

Writes create backups unless `--no-backup` is supplied.
