# craft-skills

**15 open-source creative apps — one AI pipeline.**

[ArtCraft / Storytold](https://github.com/storytold) 出品的 Craft 家族是一整套**纯 Rust、开源、净室实现**的专业创作软件：

| 应用 | 领域 | 星 |
|------|------|---|
| [photocraft](https://github.com/storytold/photocraft) | 照片编辑 | 62.9k |
| [artcraft](https://github.com/storytold/artcraft) | 核心引擎 | 29.0k |
| [pdfcraft](https://github.com/storytold/pdfcraft) | PDF 阅读/编辑 | 14.3k |
| [filmcraft](https://github.com/storytold/filmcraft) | 视频剪辑 | 13.7k |
| [wordcraft](https://github.com/storytold/wordcraft) | 文字处理 | 13.0k |
| [lightcraft](https://github.com/storytold/lightcraft) | 照片调色 | 12.9k |
| [vectorcraft](https://github.com/storytold/vectorcraft) | 矢量绘图 | 9.1k |
| [effectcraft](https://github.com/storytold/effectcraft) | 动效合成 | 6.8k |
| [gridcraft](https://github.com/storytold/gridcraft) | 电子表格 | 5.1k |
| [cadcraft](https://github.com/storytold/cadcraft) | 工程设计 | 5.1k |
| [designcraft](https://github.com/storytold/designcraft) | 版面设计 | 4.1k |
| [deckcraft](https://github.com/storytold/deckcraft) | 演示文稿 | 3.4k |
| [soundcraft](https://github.com/storytold/soundcraft) | 音频制作 | 2.9k |
| [figcraft](https://github.com/storytold/figcraft) | 界面设计 | 1.3k |

每个应用都**自带 CLI + MCP 服务器**，全部动作都是命令——你可以点，AI 也可以。

**但这些工具是散的。** 这个仓库做的事是：**把它们串成流水线。**

---

## 为什么不只是「MCP 技能包」

官方已经做好了 MCP，一行命令就能接：

```sh
claude mcp add wordcraft -- wordcraft-cli mcp
```

所以「把 MCP 接起来」没有价值。**有价值的是跨应用编排** —— 一件真实的活儿从来不止一个应用：

- 一份诉状要经过 **文字处理 → 导出 → 合并 → 安全检查**
- 一组婚礼照要经过 **图库筛选 → 批量调色 → 分层导出**
- 一份数据报告要经过 **表格计算 → 文档撰写 → 封面设计**

这个仓库里的 `workflows/` 就是这些跨应用的流水线，**每一步都写明用哪个工具、为什么、以及会踩什么坑**。

---

## 内容

### `workflows/` — 跨应用流水线（本仓库的重点）

| 流水线 | 串了哪些应用 | 干什么 |
|--------|-------------|--------|
| [`legal-bundle`](workflows/legal-bundle/) | WordCraft → PdfCraft | 诉状改稿 → 带批注 PDF → 合并卷宗 → **虚假遮盖审计** |
| [`photo-pipeline`](workflows/photo-pipeline/) | LightCraft → PhotoCraft | 图库智能筛选 → 批量调色 → 分层导出 |
| [`data-report`](workflows/data-report/) | GridCraft → WordCraft → DesignCraft | 数据校验 → 报告正文 → 封面成图 |
| [`deck-builder`](workflows/deck-builder/) | GridCraft → DeckCraft | 数据 → 图表 → 路演稿 |
| [`video-package`](workflows/video-package/) | FilmCraft → SoundCraft → EffectCraft | 剪辑 → 混音归一 → 动效片头 |
| [`print-ready`](workflows/print-ready/) | VectorCraft → PdfCraft | 矢量稿 → 印刷级 PDF 校验 |
| [`drawing-export`](workflows/drawing-export/) | CADCraft → PdfCraft | 图纸检索 → 批量转 PDF → 归档 |
| [`podcast-produce`](workflows/podcast-produce/) | SoundCraft → WordCraft | 混音归一 → 节目文稿与章节轴 |

### `skills/` — 单应用技能

13 个应用各一份 SKILL.md（核心引擎 `artcraft` 是底层库，无独立 CLI，故无独立技能），写明：该应用暴露哪些 MCP 工具、标准作业流程、硬规则、路径注意。

---

## 快速开始

**1. 装应用**（去各自 GitHub Releases 下载，或从 [ArtCraft 官网](https://getartcraft.com) 的 Launcher 装）

**2. 接进你的 agent**

Claude Code 示例：

```sh
claude mcp add wordcraft    -- wordcraft-cli mcp
claude mcp add pdfcraft     -- pdfcraft-cli mcp
claude mcp add gridcraft    -- gridcraft-cli mcp
claude mcp add figcraft     -- figcraft-cli mcp
# …其余同理，见各 skills/<app>/SKILL.md
```

**3. 用技能**

把 `skills/` 或 `workflows/` 下的目录复制到你的技能目录（如 `~/.claude/skills/`），然后直接提需求：

> 「把 `/path/to/诉状.docx` 做成带批注的 PDF，和证据清单合并成卷宗，顺便查一下有没有假遮盖。」

agent 会按 `legal-bundle` 的流水线自己串起来。

---

## Windows / WSL 路径坑

**这些可执行文件是 Windows 程序，不认 WSL 的 `/mnt/c/...` 路径**，必须传 `C:\...` 格式：

```sh
# ❌ 会报「系统找不到指定的路径」
wordcraft-cli info /mnt/c/Users/you/doc.docx

# ✅
wordcraft-cli info 'C:\Users\you\doc.docx'
# 或从 WSL 转换
wordcraft-cli info "$(wslpath -w /mnt/c/Users/you/doc.docx)"
```

---

## 许可与归属

- **本仓库的技能文档**：MIT
- **各 Craft 应用**：MIT OR Apache-2.0（见各自仓库）
- **本仓库是社区项目，非官方。** ArtCraft / Storytold 与本仓库无隶属关系。
- 所有应用名称与商标归其各自所有者。

---

## 参与

欢迎补充流水线。一个好的流水线技能应该包含：

1. **为什么串**（这些应用为什么必须一起用）
2. **有序步骤**（每步用哪个工具，别只说「用 WordCraft」）
3. **坑点**（你实际踩过的，不是想象出来的）

提 PR 前请确认流水线**真的跑通过**。
