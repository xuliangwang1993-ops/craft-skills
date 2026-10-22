---
name: opencv
name_zh: 计算机视觉（共享底层）
description: 用 opencv 开源工具图像/视频读取、几何变换、特征检测、目标跟踪、色彩空间、绿幕抠像等视觉分析。当任务需要 计算机视觉（共享底层） 且希望用开源、可独立运行的底层工具（共享底层 · 支撑 photocraft / filmcraft / effectcraft）时使用。
triggers: [opencv, 计算机视觉]
inputs:
  - name: file
    description: 输入文件路径
    required: true
tools: [shell]
mcp: []
permissions: [read_file, write_file, shell]
category: vision
layer: base
backs: 共享底层 · 支撑 photocraft / filmcraft / effectcraft
version: 1
license: Apache-2.0（4.5 起）
---

# opencv · 计算机视觉（共享底层）

**它让我们能做什么：** 共享底层：和 FFmpeg 一起承担所有画面分析——跟踪、主体识别、智能裁竖屏、抠像后处理都在这一层。

图像/视频读取、几何变换、特征检测、目标跟踪、色彩空间、绿幕抠像等视觉分析。

## 定位

- 槽位：共享底层 · 支撑 photocraft / filmcraft / effectcraft
- 三条标准：领域标杆 · 可独立使用 · 输出可接下一个工具的输入
- 许可：Apache-2.0（4.5 起）

## 安装

```sh
pip install opencv-python-headless
```

## 核心用法

```
import cv2
img = cv2.imread("in.jpg")                         # BGR；读取失败返回 None
assert img is not None
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 100, 200)
cv2.imwrite("edges.png", edges)
cap = cv2.VideoCapture("in.mp4")
fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
ok, frame = cap.read()
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (35, 60, 60), (85, 255, 255))   # 绿幕掩码
```

## 输入/输出校验

- 先侦察输入（格式、时长/页数/尺寸），再处理。
- `cv2.imwrite` 返回 True；重新 `imread` 检查 shape；视频统计帧数与 fps 与源一致。

## 硬规则

- **不覆盖原文件**，一律输出新文件。
- 批量操作先拿一个样本跑通、校验，再全量。
- 输出格式要能直接作为下一个工具的输入（见 README「底层工具」串联说明）。
