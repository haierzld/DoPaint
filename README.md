# DoPaint - 幼儿画作 AI 动画生成平台

将幼儿园小朋友的画作拍摄上传，AI 自动分析画作内容、推荐风格，一键生成专属动画视频。让孩子的想象力"动"起来！

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-orange" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/DashScope-1.20+-purple" alt="DashScope"/>
</p>

---

## 目录

- [核心流程](#核心流程)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 概览](#api-概览)
- [配置说明](#配置说明)

---

## 核心流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 拍摄/上传 │───▶│ AI 分析  │───▶│ 风格推荐  │───▶│ 动画生成  │
│  画作照片 │    │ 内容识别  │    │ 智能匹配  │    │ 图生视频  │
└──────────┘    │ 动物检测  │    │ 定制提示词 │    │ 自动下载  │
                └──────────┘    └──────────┘    └──────────┘
```

1. **上传画作** — 拍照或从相册选择孩子的画作
2. **AI 智能分析** — qwen-vl-plus 模型识别画作内容（人物、动物、场景、色彩）
3. **风格推荐** — 根据分析结果推荐 3 个最适合的风格，点击即可自动融合定制提示词
4. **一键生成动画** — 调用阿里万象图生视频 API，将静态画作转化为动态短片

---

## 功能特性

### 🎨 智能画作分析
- 上传即分析，识别画中人物、动物、植物、场景、色彩风格
- 自动检测 40+ 种常见动物（猫、狗、鸟、鱼、兔子、恐龙等）
- 分析结果无缝融入动画提示词

### 🔁 同租户图片去重
- 上传时自动计算图片 SHA256 哈希
- 同一机构/租户下的相同图片直接返回已有结果，不重复存储

### 🎭 8 种动画风格
| 风格 | 说明 |
|------|------|
| 🧚 魔法童话 | 温暖梦幻的魔法光效与精灵光点 |
| 🌿 自然奇境 | 微风、花开、蝴蝶翩跹的自然世界 |
| 🎉 节日庆典 | 彩带、气泡、闪烁灯光的欢乐氛围 |
| 🌊 海底世界 | 水波流动、鱼群穿梭的海洋奇观 |
| 🚀 太空冒险 | 星河流转、飞船穿梭的太空之旅 |
| 🦁 动物王国 | 动物跳跃互动的生动动画 |
| 🍂 四季变换 | 春夏秋冬流转的自然之美 |
| ✨ 专业定制 | 保留原画笔触的流畅动画 |

### 🐱 动物音效增强
- AI 分析检测到动物后，自动在提示词中加入对应动物的拟声描述和动作表现
- 猫的喵喵声、狗的汪汪声、鸟的啾啾声……生成动画更生动

### 📊 配额管理
- 每个用户 10 次免费使用额度
- 实时显示剩余次数，每生成一次扣减一次

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.115 |
| 数据库 | SQLAlchemy 2.0 + MySQL |
| 认证 | JWT (python-jose) |
| AI 引擎 | 阿里万象 DashScope (qwen-vl-plus / wanx-v1-image-to-video) |
| 图像处理 | Pillow + OpenCV (透视校正、边缘检测) |
| 存储 | 阿里云 OSS + 本地文件系统降级 |
| 日志 | Loguru |
| 前端 | 单页 HTML (原生 JS + CSS) |

---

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+ (或使用 SQLite 直接启动)

### 1. 克隆项目

```bash
git clone git@github.com:haierzld/DoPaint.git
cd DoPaint
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 DashScope API Key 和数据库信息
```

**必须配置**:
- `DASHSCOPE_API_KEY` — 阿里万象 API 密钥（[获取地址](https://dashscope.console.aliyun.com/)）
- `DATABASE_URL` — 数据库连接串（不填则默认使用 SQLite）
- `APP_SECRET_KEY` — 应用密钥（改为随机字符串）

### 4. 启动服务

```bash
python main.py
# 或
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务默认运行在 `http://localhost:8000/app/`

### 5. 开发登录

打开 `http://localhost:8000/app/`，使用任意昵称即可登录（开发模式自动创建用户）。

---

## 项目结构

```
DoPaint/
├── main.py                    # FastAPI 入口 + 开发登录 + 静态挂载
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
│
├── app/
│   ├── core/                  # 核心配置
│   │   ├── config.py          # 应用配置（pydantic-settings）
│   │   ├── security.py        # JWT + 微信登录
│   │   └── deps.py            # 依赖注入（DB会话、当前用户）
│   │
│   ├── models/                # SQLAlchemy 数据模型
│   │   ├── base.py            # 基础模型（id, created_at, updated_at）
│   │   ├── user.py            # 用户
│   │   ├── organization.py    # 机构（幼儿园）
│   │   ├── artwork.py         # 画作（含 image_hash 去重）
│   │   ├── animation.py       # 动画生成记录
│   │   ├── prompt_template.py # 提示词模板
│   │   └── order.py           # 订单
│   │
│   ├── api/
│   │   ├── router.py          # 路由汇总
│   │   └── endpoints/
│   │       ├── auth.py        # 认证（微信登录、token刷新）
│   │       ├── artworks.py    # 画作（上传、分析、删除）
│   │       ├── animations.py  # 动画（生成、轮询、下载）
│   │       ├── prompts.py     # 提示词模板（CRUD）
│   │       ├── organizations.py # 机构管理
│   │       ├── orders.py      # 订单/支付
│   │       └── admin.py       # 管理后台
│   │
│   ├── services/              # 业务逻辑
│   │   ├── artwork_service.py # 画作上传、预处理、去重、存储
│   │   ├── animation_service.py # 动画任务调度
│   │   ├── ai_service.py      # DashScope API（分析 + 图生视频）
│   │   ├── quota_service.py   # 配额校验与消费
│   │   ├── payment_service.py # 微信支付
│   │   └── storage_service.py # OSS / 本地存储
│   │
│   └── utils/
│       ├── image_processor.py # 透视校正、边缘检测、色彩增强
│       ├── prompt_builder.py  # 提示词组装（风格+分析+音效）
│       ├── video_utils.py     # 视频处理
│       └── response.py        # 统一响应格式
│
├── frontend/
│   └── index.html             # 单页前端（上传/分析/风格/生成）
│
├── scripts/
│   ├── init_db.py             # 初始化数据库
│   └── seed_prompts.py        # 初始化提示词种子数据
│
└── docs/
    ├── 技术架构方案.md
    └── 商业计划书_DoPaint.md
```

---

## API 概览

### 画作

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/artworks/upload` | 上传画作（自动去重、预处理） |
| GET | `/api/v1/artworks` | 获取画作列表（最近 20 条） |
| GET | `/api/v1/artworks/{id}` | 画作详情 |
| POST | `/api/v1/artworks/{id}/analyze` | AI 分析画作内容 |
| DELETE | `/api/v1/artworks/{id}` | 删除画作 |

### 动画

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/animations/generate` | 生成动画 |
| POST | `/api/v1/animations/batch` | 批量生成（机构版） |
| GET | `/api/v1/animations/{id}/status` | 查询生成状态 |
| GET | `/api/v1/animations` | 动画列表 |

### 提示词

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/prompts/styles` | 获取所有可用风格 |

### 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

---

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里万象 API 密钥 | (必填) |
| `DASHSCOPE_VIDEO_MODEL` | 视频生成模型 | `wanx-v1-image-to-video` |
| `DATABASE_URL` | 数据库连接串 | SQLite 本地 |
| `SELF_HOST` | 服务自身地址 | `localhost:8000` |
| `DEFAULT_FREE_QUOTA` | 新用户免费配额 | 5 |
| `MAX_UPLOAD_SIZE_MB` | 上传大小限制 | 20 |
| `WECHAT_APP_ID` | 微信小程序 AppID | (生产必填) |

---

## License

MIT
