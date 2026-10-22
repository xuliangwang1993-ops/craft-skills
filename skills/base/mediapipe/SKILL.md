---
name: mediapipe
name_zh: 人脸/人体关键点（MediaPipe）
description: 用 mediapipe 开源工具完成「人脸/人体关键点」。当任务需要 人脸/人体关键点 且希望用开源、可独立运行的底层工具时使用。
triggers: [mediapipe, 人脸/人体关键点]
inputs:
  - name: input
    description: 输入文件路径、URL 或查询
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: vision
layer: base
backs: 人脸/人体关键点
wave: 2
stage: 入库
version: 1
license: "Apache-2.0"
---

# mediapipe · 人脸/人体关键点（MediaPipe）

**它让我们能做什么：** 人脸网格、手势、人体姿态关键点，给美颜、动作跟踪、卡点特效提供坐标。

## 定位

- 槽位：人脸/人体关键点（一格一个最强工具，本格只放 mediapipe）
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0
- 阶段：入库（文档已写，尚未落地验证）

## 安装

```sh
pip install mediapipe
```

## 核心用法

```
python - <<'PY'
import mediapipe as mp, cv2
img=cv2.imread('face.jpg')
with mp.solutions.face_mesh.FaceMesh(static_image_mode=True) as fm:
    r=fm.process(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    print(len(r.multi_face_landmarks or []))
PY
```

## 输入/输出（串联）

- 输入图片/视频帧（opencv 读入）→ 输出关键点坐标（导出 json），接 opencv 绘制 / effectcraft 跟踪。

## 输入/输出校验

- 先侦察输入，再处理。
- 输出非空、格式可被下一个工具读取；生成类任务固定 seed，同输入跑两遍结果一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 密钥只从环境变量读取，不写进命令历史或仓库。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
