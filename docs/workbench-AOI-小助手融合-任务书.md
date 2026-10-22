# 任务书：Workbench 骨架 × AOI 展示 × 小助手前台 融合改版

> 给 DeepSeek（AI 编码助手）的自包含任务书。直接照此执行，完成后按文末「回报内容」汇报。

## 0. 背景与原则

我们在做一座"工厂"：每一个能力格子放一个最强的开源工具，写成 Skill，串成流水线。工厂四原则：

1. **一格一个最强工具**：每格只选一个，按"能直接用、协议友好、维护活跃"挑最强的。
2. **全覆盖不留空格**：搜索、浏览器自动化、数据库、OCR、三维、地图、科研等空格陆续补齐。
3. **输出稳定**：同样输入得到同样质量的输出，可复现。
4. **输出接输入串联**：上一个工具的输出就是下一个工具的输入，能组成完整链路。

当前技能库：**56 个 Skill**（13 个原有 + 43 个底层开源工具），来源仓库 `xuliangwang1993-ops/craft-skills`。

**优先级（必须体现在实现顺序里）：**
- **P1**：生产 → 后测 → 客服，一趟跑通、跑顺。
- **P2**：小助手（前台接待）做好。
- 其余（立项/入库/落地/主页样板/每周推进）在后。

## 1. Workbench 骨架（结构层，已有真实代码）

**真实位置**：仓库 `xuliangwang1993-ops/xconnect-landing`，分支 `factory/integrate-workbench`，目录 `workbench/`。README 中称其为 **X-connect Workbench (PWA)**，是在 Render 上的网页 bot 基础上升级而来。

目录结构：
- `server.mjs`、`server-voice.mjs`（入口）、`voice-auth.mjs`
- `public/`：`index.html`、`app.js`、`styles.css`、`sw.js`、`manifest.webmanifest`、`xc-handshake.js`
- `integrations/`：`slack.mjs`、`event-to-card.mjs`
- `test/`、`slack-app-manifest.yaml`、`README.md`
- `desktop/`：Electron 27 桌面壳（README 写明**尚未构建、未验证**）

技术栈：
- **后端**：纯 Node.js（ESM，无框架），Node ≥ 18，唯一依赖 `ws`；启动命令 `node server-voice.mjs`。
- **前端**：手写 PWA，原生 JS/HTML/CSS + service worker，卡片优先（card-first）的工作台。
- **数据**：卡片存储在 Supabase。
- **聊天**：走网关 `/v1/chat/completions`（api.x-connect.ai）或 Subrouter key。
- **语音**：豆包实时语音（WebSocket）。

**要求**：
- **在这套现有代码上做**，不要换框架重写，保持现有技术栈（不引入 React/Vue 等框架和构建链）。
- AOI 展示（第 2 节）和小助手讲解（第 3 节）作为新增模块/卡片加进这个 workbench。
- 从 `factory/integrate-workbench` **新建分支**开发，完成后开 PR（目标分支 `factory/integrate-workbench`），**不要合并**。
- 工作区按"工厂流水线"组织：输入 → 批处理 → 生产 → 后测 → 交付/客服；技能目录从 craft-skills 的 Skill 元数据生成，不手写。
- 骨架只负责"台子"，不写死展示内容。

## 2. AOI 展示（展示层）

- 展示 aoi-cloud 网关（api.x-connect.ai）的能力与**已验收样品**，作为主页样板出口。
- 参考现有站点：
  - https://xconnect-portal.onrender.com （门户）
  - https://sanxian-shouzuo.onrender.com （已上线样品）
- 每个样品卡片：用到的技能链、输入、输出、验收状态（只展示"落地验收通过"的）。
- 能力墙按格子分组，空格显示"建设中"，体现全覆盖进度。

## 3. 小助手 = 前台接待

- 客户进站第一个接触的就是小助手，由它**把整个流程讲清楚**。
- **批处理在前**：客户先提交素材/需求，后台批处理启动；小助手在等待期间讲解。
- **讲解像动画一样流畅，从头带到尾**：
  - 分步（step）讲解 + 滚动联动：讲到哪一步，页面对应区域高亮/滚动到位。
  - 自动推进（auto-advance），每步有进度条；客户可暂停、上一步、**跳过**。
  - 讲解与批处理真实进度联动（批处理完成某步时讲解同步推进）。
  - 动画用原生 CSS（transition/animation）与少量原生 JS 实现，不引入框架，尊重 `prefers-reduced-motion`。
- 小助手的回答依据 **knowledge 包**（见第 5 节），不得编造。

## 4. "搭台你唱戏"融合思路

- **台**：Workbench 骨架 + AOI 展示层，负责结构与内容。
- **戏**：小助手负责"演"——带客户走流程、解说样品、回答问题、引导下单/使用。
- 技术上：骨架和展示层暴露"可被讲解的锚点"（如 `data-tour-step="produce"`），小助手的讲解脚本只引用锚点，不耦合具体 DOM。
- 讲解脚本数据化（JSON/YAML），新增技能或样品时只改数据不改代码。

## 5. 新技能上线，小助手主动提醒老客户

- **knowledge 同步**：craft-skills 每个 README（含技能数已更新为 56 的那份）同步进小助手 knowledge；新 README 入库时自动同步（CI/webhook 触发，生成 knowledge 包并版本化）。不要只放在 GitHub 上。
- **主动提醒**：检测 knowledge 包新增技能 → 给现有客户生成"新技能速览"：
  - 新技能是什么、补了哪个格子、能接在哪条链路上；
  - **怎么用**：每个技能一段 how-to（输入示例 → 操作 → 输出示例）。
- **渠道**：站内小助手首屏提示 + 通知中心；邮件/其他渠道先做接口与模板，**不要真实发送**，留开关。
- 客户可关闭提醒；已读状态记录。

## 6. 交付物

1. 在现有 workbench（`xconnect-landing` / `factory/integrate-workbench` / `workbench/`）上接入新模块。
2. AOI 展示层：能力墙 + 验收样品卡片。
3. 小助手前台：分步动画讲解（自动推进/暂停/跳过）+ 与批处理进度联动。
4. 讲解脚本与锚点数据化。
5. knowledge 同步脚本/CI + 新技能提醒（站内实现，外发渠道仅接口）。
6. README 更新说明以上用法。

## 7. 验收标准

- [ ] P1 链路：一个真实需求能从提交 → 批处理/生产 → 后测 → 客服答疑一趟跑通。
- [ ] 小助手讲解能从头自动播到尾，可暂停、跳过，滚动与高亮同步，无卡顿。
- [ ] 展示层只出现验收通过的样品；空格显示"建设中"。
- [ ] 改一个 craft-skills README 后，knowledge 包自动更新，小助手能回答新内容。
- [ ] 新增一个技能后，老客户登录看到"新技能速览"及 how-to。
- [ ] 移动端可用；构建与现有测试通过。

## 8. 约束

- **开 PR，不要合并**。
- **代码里不得出现任何密钥**，一律走环境变量。
- **不要动 x-connect.ai 主站、Wix、Cloudflare 的任何配置。**
- 不改与本任务无关的文件；不做真实对外消息发送。

## 9. 回报内容

完成后请回报：
1. PR 链接与分支名（基于 `factory/integrate-workbench` 新建）；
2. 改动文件清单与每项一句话说明；
3. 在现有 workbench 代码上改了哪些模块、新增了哪些文件（确认未换框架、未改技术栈）；
4. 验收清单逐项结果（通过/未通过/原因）；
5. 预览地址或截图/录屏（小助手讲解全流程）；
6. 遗留问题与下一步建议。
