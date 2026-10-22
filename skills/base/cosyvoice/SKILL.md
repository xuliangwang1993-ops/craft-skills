---
name: cosyvoice
name_zh: 中文配音 TTS（CosyVoice）
description: 用 cosyvoice 开源工具阿里通义开源多语种语音合成，支持预置音色、3 秒零样本声音复刻、跨语种与情感指令。当任务需要 中文配音 TTS（CosyVoice） 且希望用开源、可独立运行的底层工具（soundcraft / filmcraft 配音补位）时使用。
triggers: [cosyvoice, 中文配音 TTS]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: audio
layer: base
backs: soundcraft / filmcraft 配音补位
version: 1
license: Apache-2.0
---

# cosyvoice · 中文配音 TTS（CosyVoice）

**它让我们能做什么：** 配音 TTS：给视频、播客、数字人生成自然中文配音。

阿里通义开源多语种语音合成，支持预置音色、3 秒零样本声音复刻、跨语种与情感指令。

## 定位

- 槽位：soundcraft / filmcraft 配音补位
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0

## 安装

```sh
# requirements.txt 锁定 torch==2.3.1、onnxruntime-gpu、TensorRT、deepspeed，只支持 Python 3.10，需独立 conda 环境
conda create -n cosyvoice -y python=3.10 && conda activate cosyvoice
git clone --recursive https://github.com/FunAudioLLM/CosyVoice && cd CosyVoice && pip install -r requirements.txt
# 模型需单独下载（数 GB），否则下面的 pretrained_models 路径不存在
python -c "from modelscope import snapshot_download; snapshot_download('iic/CosyVoice2-0.5B', local_dir='pretrained_models/CosyVoice2-0.5B')"
```

## 核心用法

```
import sys; sys.path.append("third_party/Matcha-TTS")
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav
cv = CosyVoice2("pretrained_models/CosyVoice2-0.5B")
prompt = load_wav("ref.wav", 16000)
for i, out in enumerate(cv.inference_zero_shot("要合成的文字。", "参考音频对应文字。", prompt, stream=False)):
    torchaudio.save(f"tts_{i}.wav", out["tts_speech"], cv.sample_rate)
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- 试听语速、多音字；用 `soxi` 核对采样率。**声音复刻须取得声音本人授权。**

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
