---
name: paddleocr
name_zh: 图片 OCR（PaddleOCR，中文最强）
description: 用 paddleocr 开源工具完成「图片文字识别（中英文）」。当任务需要 图片文字识别（中英文） 且希望用开源、可独立运行的底层工具时使用。
triggers: [paddleocr, 图片文字识别（中英文）]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: image
layer: base
backs: 图片文字识别（中英文）
wave: 1
stage: 入库
version: 1
license: Apache-2.0
---

# paddleocr · 图片 OCR（PaddleOCR，中文最强）

**它让我们能做什么：** 截图、照片、票据里的中文文字精准识别成带坐标文本，补上 OCRmyPDF 管不到的图片场景。

## 定位

- 槽位：图片文字识别（中英文）（一格一个最强工具，本格只放 paddleocr）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install paddlepaddle paddleocr
```

## 核心用法

```
paddleocr ocr -i receipt.jpg --lang ch  # 3.x CLI；2.x 为 paddleocr --image_dir receipt.jpg --lang ch
python - <<'P'
from paddleocr import PaddleOCR
ocr=PaddleOCR(lang='ch'); print(ocr.predict('receipt.jpg'))
P
```

## 输入/输出校验

- 先侦察输入，再处理。
- 识别结果非空、置信度分布合理；抽样人工核对关键字段。CLI 参数随 2.x/3.x 变化，以 `paddleocr --help` 为准。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
