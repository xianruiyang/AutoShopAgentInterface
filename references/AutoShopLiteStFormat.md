# AutoShop Lite ST 容器记录

维护或诊断 `scripts/autoshop-agent.exe` 时使用本文档。

## 已验证的容器结构

已测试的 AutoShop Lite 工程中，`MAIN.ST`、`INT_001.ST`、`SBR_001.ST` 不是纯文本文件，而是二进制容器。每个文件都以 ASCII 签名 `AutoShop` 开头。

可编辑的 ST 源码位于文件尾部，是最后一个 MFC 风格的 `CString` 文本块，后面跟随 4 个 `00` 字节。

长度头规则：

- `length < 0xFF`：1 字节长度。
- `length < 0xFFFF`：`FF` 加 2 字节小端长度。
- 更长文本：`FF FF FF` 加 4 字节小端长度。

CLI 写回 ST 时只替换这个最终文本块，并保留其余二进制内容。

## 全局变量表样本

`全局变量/变量表/变量表.gvt` 已通过用户在 AutoShop 内手工创建变量得到样本。该文件是 AutoShop 5.03 `CLVTItem` 序列化格式，顶层保持 4 个 `CLVTItem` 对象；真实变量行位于最后一个对象的内部数组，不能把第二个变量写成新的顶层对象。

`workspace export` 会在 `变量表.gvt.json` 中导出：

- `semanticType: "global-variable-table-v5.03"`
- `globalVariableRows`

`workspace apply` 会优先根据 `globalVariableRows` 重建 `.gvt` 内部变量行数组，并复用已有样本行的隐藏类型/标志字段。未确认的新字段不要直接伪造；保留 `contentBase64` 作为字节级兜底。

当前已采样的 `STRING<128>` 格式把显式 `dataType` 保存为最后一个变量记录之后的尾部字符串，而不是记录内部字段。因此编辑 `globalVariableRows` 时必须让带 `dataType` 的行保持最后；新增 BOOL 等普通变量应插入到它之前。CLI 会在 dry-run/apply 阶段拒绝把带 `dataType` 的行写在中间，以避免 AutoShop 重新打开后变量表读空。

## 编码

工程内嵌 ST 文本默认按 GB2312/CP936 处理。

导出的 txt 默认按 UTF-8 写出。

除非某个工程已经证明使用不同编码，否则只通过 JSON 配置或 CLI 参数调整编码，不要在代码里写死特殊规则。

## 安全边界

已支持：

- 列出现有 `*.ST` 程序容器。
- 导出内嵌 ST 源码。
- 将 txt 写回既有 `*.ST` 容器。

未支持：

- 新建或删除 POU 节点。
- 编辑 `.hcp` 工程表。
- 语义化编辑硬件配置、交叉引用数据，或未采样确认的其它私有变量表格式。

写回默认创建备份。只有显式传入 `--no-backup` 时才跳过备份。
