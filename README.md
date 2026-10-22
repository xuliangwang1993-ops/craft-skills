# craft-skills

**74 个技能 = 13 个 Craft 应用技能 + 61 个开源底层工具技能（第 0 批 21 + 第 1 批 22 + 第 2 批 18）—— 一条 AI 流水线。**

扩库计划与格子总表见 [`docs/扩库立项.md`](docs/扩库立项.md)：入库一批、落地一批、立项一批，滚动推进。

（另有 8 条跨应用工作流；Craft 家族共 14 个仓库，其中 `artcraft` 是核心引擎、无独立 CLI，故无独立技能。）

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

13 个 Craft 应用各一份 SKILL.md（核心引擎 `artcraft` 是底层库，无独立 CLI，故无独立技能），写明：该应用暴露哪些 MCP 工具、标准作业流程、硬规则、路径注意。

### `skills/base/` — 底层工具 / 开源替代（61 个）

**做法是工厂化：一格一个最强工具，全覆盖不留空格，输出稳定，工具之间输出接输入串联。** 每个工具都要过三条标准：

1. **领域标杆**：在自己那一格是公认最强的；
2. **可独立使用**：命令行或 Python 直接调用，不用再包一层；
3. **可对接其他工具**：输出是标准格式，能直接当下一个工具的输入。

同一格不放两个重复工具。FFmpeg + OpenCV 是**共享底层**，给上面所有格子共用。

| 格子 | 它让我们能做什么 | 工具 |
|------|------------------|------|
| 视频剪辑主干 | 覆盖并超过剪映约八成功能 | FFmpeg + MLT |
| 字幕 | 自动出带时间轴字幕 | Whisper / FunASR（中文） |
| 人声伴奏分离 | 提伴奏、去 BGM | Demucs |
| 抠像 | 不用绿幕抠人像 | RobustVideoMatting |
| 超分放大 | 低清素材放大修复 | Real-ESRGAN |
| 配音 TTS | 自然中文配音 | CosyVoice |
| 调色 | 照片批量调色 | darktable |
| PDF | 合并拆分、OCR、提取、遮盖审计 | qpdf / OCRmyPDF / PyMuPDF |
| 办公文档 | 表格、PPT、Word、格式互转 | openpyxl / python-pptx / python-docx / Pandoc |
| 矢量 | 矢量批量导出 | Inkscape |
| 批量图片 | 缩略、转码、水印、拼图 | libvips / ImageMagick |
| 音频 | 转换、剪裁、混音、降噪 | SoX |
| 共享底层 | 所有音视频与画面分析的公共层 | FFmpeg + OpenCV |

| 技能 | 名称 | 补位的 Craft 槽位 | 许可 | 安装 |
|------|------|------------------|------|------|
| [`ffmpeg`](skills/base/ffmpeg/) | 音视频转码与处理（共享底层） | 共享底层 · 支撑 filmcraft / soundcraft / effectcraft | LGPL-2.1+（启用 --enable-gpl 编译时为 GPL） | `sudo apt install ffmpeg` |
| [`opencv`](skills/base/opencv/) | 计算机视觉（共享底层） | 共享底层 · 支撑 photocraft / filmcraft / effectcraft | Apache-2.0（4.5 起） | `pip install opencv-python-headless` |
| [`mlt`](skills/base/mlt/) | 多轨时间线剪辑（melt） | filmcraft 开源替代 | LGPL-2.1（部分模块 GPL） | `sudo apt install melt` |
| [`whisper`](skills/base/whisper/) | 语音识别与字幕（Whisper） | filmcraft / soundcraft 字幕补位 | MIT | `pip install -U openai-whisper` |
| [`funasr`](skills/base/funasr/) | 中文语音识别（FunASR / Paraformer） | filmcraft / soundcraft 中文字幕补位 | MIT（模型权重另见各自模型许可） | `pip install -U funasr modelscope torch torchaudio` |
| [`demucs`](skills/base/demucs/) | 人声/伴奏分离（Demucs） | soundcraft 开源补位 | MIT | `pip install -U demucs` |
| [`sox`](skills/base/sox/) | 音频处理（SoX） | soundcraft 开源替代 | GPL-2.0（libsox 为 LGPL） | `sudo apt install sox libsox-fmt-all` |
| [`robust-video-matting`](skills/base/robust-video-matting/) | 无绿幕人像抠像（RVM） | effectcraft / filmcraft 抠像补位 | GPL-3.0 | `git clone https://github.com/PeterL1n/RobustVideoMatting && pip install -r RobustVideoMatting/requirements_inference.txt` |
| [`real-esrgan`](skills/base/real-esrgan/) | 超分辨率放大（Real-ESRGAN） | photocraft / filmcraft 画质增强补位 | BSD-3-Clause | `pip install realesrgan basicsr` |
| [`cosyvoice`](skills/base/cosyvoice/) | 中文配音 TTS（CosyVoice） | soundcraft / filmcraft 配音补位 | Apache-2.0 | `git clone --recursive https://github.com/FunAudioLLM/CosyVoice && cd CosyVoice && pip install -r requirements.txt` |
| [`darktable-cli`](skills/base/darktable-cli/) | 照片批量调色（darktable） | lightcraft 开源替代 | GPL-3.0 | `sudo apt install darktable` |
| [`qpdf`](skills/base/qpdf/) | PDF 结构操作（qpdf） | pdfcraft 开源替代 | Apache-2.0 | `sudo apt install qpdf` |
| [`ocrmypdf`](skills/base/ocrmypdf/) | 扫描件 OCR（OCRmyPDF） | pdfcraft OCR 开源替代 | MPL-2.0（依赖 Tesseract Apache-2.0、Ghostscript AGPL） | `sudo apt install ocrmypdf tesseract-ocr-chi-sim` |
| [`pymupdf`](skills/base/pymupdf/) | PDF 读取/渲染/编辑（PyMuPDF） | pdfcraft 开源替代 | ⚠️ AGPL-3.0（或付费商业许可） | `pip install pymupdf` |
| [`openpyxl`](skills/base/openpyxl/) | Excel 读写（openpyxl） | gridcraft 开源替代 | MIT | `pip install openpyxl` |
| [`python-pptx`](skills/base/python-pptx/) | PPT 生成（python-pptx） | deckcraft 开源替代 | MIT | `pip install python-pptx` |
| [`python-docx`](skills/base/python-docx/) | Word 读写（python-docx） | wordcraft 开源替代 | MIT | `pip install python-docx` |
| [`pandoc`](skills/base/pandoc/) | 文档格式互转（Pandoc） | wordcraft / deckcraft 格式转换补位 | GPL-2.0+ | `sudo apt install pandoc` |
| [`inkscape`](skills/base/inkscape/) | 矢量图命令行（Inkscape） | vectorcraft 开源替代 | GPL-2.0+ | `sudo apt install inkscape` |
| [`libvips`](skills/base/libvips/) | 高速批量图片处理（libvips） | photocraft 批处理开源替代 | LGPL-2.1+ | `sudo apt install libvips-tools` |
| [`imagemagick`](skills/base/imagemagick/) | 通用图片处理（ImageMagick） | photocraft 批处理开源替代 | ImageMagick License（Apache-2.0 风格） | `sudo apt install imagemagick` |

**第 1 批（扩库，阶段：入库，未实测）— 22 个新格子：**

| 技能 | 名称 | 格子 | 许可 | 安装 |
|------|------|------|------|------|
| [`playwright`](skills/base/playwright/) | 浏览器自动化（Playwright） | 浏览器自动化 | Apache-2.0 | `pip install playwright` |
| [`crawl4ai`](skills/base/crawl4ai/) | 网页抓取与正文提取（Crawl4AI） | 网页抓取/正文提取 | Apache-2.0 | `pip install -U crawl4ai` |
| [`searxng`](skills/base/searxng/) | 元搜索（SearXNG，自托管） | 网页搜索 | AGPL-3.0 | `docker run -d -p 8888:8080 --name searxng searxng/searxng` |
| [`paddleocr`](skills/base/paddleocr/) | 图片 OCR（PaddleOCR，中文最强） | 图片文字识别（中英文） | Apache-2.0 | `pip install paddlepaddle paddleocr` |
| [`postgresql`](skills/base/postgresql/) | 关系数据库（PostgreSQL / psql） | 关系数据库 | PostgreSQL License（类 MIT） | `sudo apt install postgresql-client` |
| [`duckdb`](skills/base/duckdb/) | 嵌入式分析（DuckDB） | 数据分析/SQL on 文件 | MIT | `pip install duckdb` |
| [`blender`](skills/base/blender/) | 3D 建模与渲染（Blender 无界面） | 3D 建模/渲染 | GPL-2.0+ | `sudo apt install blender` |
| [`gdal`](skills/base/gdal/) | 地图与地理数据（GDAL/OGR） | GIS/地理数据 | MIT | `sudo apt install gdal-bin` |
| [`graphviz`](skills/base/graphviz/) | 图表与流程图（Graphviz） | 流程图/关系图 | EPL-1.0 | `sudo apt install graphviz` |
| [`tectonic`](skills/base/tectonic/) | LaTeX 排版（Tectonic） | 数学公式/学术排版 | MIT | `cargo install tectonic` |
| [`ripgrep`](skills/base/ripgrep/) | 代码与文本搜索（ripgrep） | 全文/代码搜索 | MIT OR Unlicense | `sudo apt install ripgrep` |
| [`jq`](skills/base/jq/) | JSON 处理（jq） | JSON 处理 | MIT | `sudo apt install jq` |
| [`yt-dlp`](skills/base/yt-dlp/) | 媒体下载（yt-dlp） | 在线音视频下载 | Unlicense | `pip install -U yt-dlp` |
| [`docker`](skills/base/docker/) | 容器运行（Docker） | 容器/环境隔离 | Apache-2.0（Docker Engine / Moby） | `curl -fsSL https://get.docker.com | sh` |
| [`qdrant`](skills/base/qdrant/) | 向量检索（Qdrant） | 向量数据库/语义检索 | Apache-2.0 | `docker run -d -p 6333:6333 -v $PWD/qdrant:/qdrant/storage qdrant/qdrant` |
| [`argos-translate`](skills/base/argos-translate/) | 离线翻译（Argos Translate） | 机器翻译（离线） | MIT | `pip install argostranslate` |
| [`zbar`](skills/base/zbar/) | 二维码/条码识别（ZBar） | 二维码/条码 | LGPL-2.1 | `sudo apt install zbar-tools` |
| [`himalaya`](skills/base/himalaya/) | 命令行邮件（Himalaya） | 邮件收发 | MIT | `cargo install himalaya` |
| [`comfyui`](skills/base/comfyui/) | 本地图像生成（ComfyUI，需 GPU） | AI 图像生成 | GPL-3.0（模型权重另见各自许可） | `git clone https://github.com/comfyanonymous/ComfyUI` |
| [`rembg`](skills/base/rembg/) | 图片去背景（rembg） | 图片抠图/去背景 | MIT | `pip install "rembg[cli]"` |
| [`pyscenedetect`](skills/base/pyscenedetect/) | 镜头切分（PySceneDetect） | 镜头/场景检测 | BSD-3-Clause | `pip install "scenedetect[opencv]"` |
| [`librosa`](skills/base/librosa/) | 音乐节拍分析（librosa） | 节拍/音乐分析（卡点） | ISC | `pip install librosa soundfile` |

**第 2 批（扩库，阶段：入库，未实测）— 18 个新格子：**

| 技能 | 名称 | 格子 | 许可 | 安装 |
|------|------|------|------|------|
| [`deepfilternet`](skills/base/deepfilternet/) | 语音降噪（DeepFilterNet） | 语音降噪 | MIT OR Apache-2.0 | `pip install deepfilternet` |
| [`practical-rife`](skills/base/practical-rife/) | 慢动作补帧（Practical-RIFE） | 慢动作补帧 | MIT | `git clone https://github.com/hzwer/Practical-RIFE && cd Practical-RIFE && pip install -r requirements.txt` |
| [`iopaint`](skills/base/iopaint/) | 图片修复/消除路人（LaMa · IOPaint） | 图片修复/消除路人 | Apache-2.0（LaMa 模型 Apache-2.0） | `pip install iopaint` |
| [`mediapipe`](skills/base/mediapipe/) | 人脸/人体关键点（MediaPipe） | 人脸/人体关键点 | Apache-2.0 | `pip install mediapipe` |
| [`ultralytics-yolo`](skills/base/ultralytics-yolo/) | 目标检测/跟踪（Ultralytics YOLO） | 目标检测/跟踪 | ⚠️ AGPL-3.0（闭源商用需 Ultralytics 企业许可） | `pip install ultralytics` |
| [`gpt-sovits`](skills/base/gpt-sovits/) | 声音克隆/变声（GPT-SoVITS） | 声音克隆/变声 | MIT（底模另见各自许可） | `git clone https://github.com/RVC-Boss/GPT-SoVITS && cd GPT-SoVITS && bash install.sh` |
| [`whisperx`](skills/base/whisperx/) | 逐字时间对齐（WhisperX） | 逐字时间对齐 | BSD-2-Clause（说话人分离用 pyannote，需 HF token 并同意模型条款） | `pip install whisperx` |
| [`liveportrait`](skills/base/liveportrait/) | 数字人口型/表情驱动（LivePortrait） | 数字人口型/表情驱动 | ⚠️ 代码 MIT，但依赖的 InsightFace 人脸模型仅限非商用（商用须替换检测模型或取得授权） | `git clone https://github.com/KwaiVGI/LivePortrait && cd LivePortrait && pip install -r requirements.txt` |
| [`wan`](skills/base/wan/) | 文生视频（Wan 2.x） | 文生视频 | Apache-2.0（⚠️ 需大显存 GPU） | `git clone https://github.com/Wan-Video/Wan2.2 && cd Wan2.2 && pip install -r requirements.txt` |
| [`llama-cpp`](skills/base/llama-cpp/) | 本地大模型推理（llama.cpp） | 本地大模型推理 | MIT（模型权重另见各自许可） | `git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp && cmake -B build && cmake --build build -j` |
| [`meilisearch`](skills/base/meilisearch/) | 全文检索引擎（Meilisearch） | 全文检索引擎 | MIT（社区版；部分企业功能为商业许可） | `docker run -d -p 7700:7700 -e MEILI_MASTER_KEY=$MEILI_KEY -v $PWD/meili:/meili_data getmeili/meilisearch` |
| [`n8n`](skills/base/n8n/) | 工作流编排（n8n） | 工作流编排 | ⚠️ Sustainable Use License（源码可见，非 OSI 开源；不得作为托管服务转售） | `docker run -d -p 5678:5678 -v $PWD/n8n:/home/node/.n8n docker.n8n.io/n8nio/n8n` |
| [`vl-convert`](skills/base/vl-convert/) | 图表绘制（Vega-Lite · vl-convert） | 图表绘制 | BSD-3-Clause（Vega-Lite）/ BSD-3-Clause（vl-convert） | `pip install vl-convert-python` |
| [`calibre`](skills/base/calibre/) | 电子书转换（Calibre） | 电子书 | GPL-3.0 | `sudo apt install calibre` |
| [`fonttools`](skills/base/fonttools/) | 字体子集/处理（fontTools） | 字体子集/处理 | MIT | `pip install fonttools brotli` |
| [`rclone`](skills/base/rclone/) | 文件同步/云存储（rclone） | 文件同步/云存储 | MIT | `sudo apt install rclone` |
| [`7zip`](skills/base/7zip/) | 压缩归档（7-Zip） | 压缩归档 | LGPL-2.1（部分 BSD-3；unRAR 代码受 unRAR 许可限制，不得用于制作 RAR 压缩器） | `sudo apt install 7zip   # 提供 7zz；旧发行版 p7zip-full 提供 7z` |
| [`exiftool`](skills/base/exiftool/) | 文件元数据（ExifTool） | 文件元数据 | Artistic License / GPL-1.0+（Perl 同款双许可） | `sudo apt install libimage-exiftool-perl` |

> 第 2 批许可提醒：⚠️ Ultralytics YOLO 为 **AGPL-3.0**（闭源商用需企业许可）；⚠️ n8n 为 **Sustainable Use License，非 OSI 开源**；⚠️ LivePortrait 代码 MIT，但依赖的 **InsightFace 模型仅限非商用**；Calibre 为 GPL-3.0；7-Zip 的 unRAR 部分有额外限制；WhisperX 说话人分离需同意 pyannote 模型条款；Meilisearch 企业功能为商业许可；Wan、LivePortrait、RIFE、GPT-SoVITS 建议/需要 GPU。

> 许可提醒：PyMuPDF、SearXNG 为 **AGPL-3.0**；Blender、ComfyUI 为 GPL；ComfyUI 需要 GPU。PyMuPDF 为 **AGPL-3.0**（网络服务对外提供须开源，商用闭源需买商业许可或换 pypdf）；SoX、darktable、Inkscape、Pandoc、RobustVideoMatting 为 GPL，改代码后分发须开源；只作为独立命令行调用一般不受影响。

**刻意没收的**：Ardour、Natron、Penpot、Scribus、LibreCAD、FreeCAD、GIMP —— 都需要再包一层接口才能给 AI 稳定调用，不满足「可独立使用」；Natron 另外基本停更。

#### 正在重写的三个缺口

开源里没有够格的工具，这三格不留空，锁定闭源标杆自己重写：

1. **模板与素材生态** —— 剪映的模板、贴纸、音乐、特效库是护城河，只能自建或接免版权素材库。
2. **一键成片** —— PySceneDetect 切镜头 + 大模型挑片段 + MLT 成片，需要自己串成完整流程。
3. **美颜 / 数字人精修** —— MediaPipe、LivePortrait、MuseTalk 能做但质量不够，需重写到剪映水准。

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

把 `skills/`、`skills/base/` 或 `workflows/` 下的目录复制到你的技能目录（如 `~/.claude/skills/`），然后直接提需求：

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
- **底层工具**：各自许可见上表（MIT / Apache / BSD / MPL / LGPL / GPL / AGPL）
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
