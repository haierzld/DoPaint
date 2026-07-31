# DoPaint API 接口文档

> Base URL: `https://api.dopaint.com/api/v1`  
> 认证方式: `Authorization: Bearer {jwt_token}`  
> Content-Type: `application/json` (文件上传用 `multipart/form-data`)

---

## 通用说明

### 统一响应格式

```json
{
  "code": 0,           // 0=成功, 其他=错误码
  "message": "操作成功",
  "data": { ... }      // 具体数据 | null
}
```

### 分页响应格式

```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| -1 | 业务错误 |
| 401 | 未登录/Token 过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 配额耗尽 |

---

## 一、认证模块 `/auth`

### 1.1 微信小程序登录

```
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "code": "081xAb0w3abcd1234efgh5678"
}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user_id": 1,
    "nickname": "王老师",
    "avatar": "https://...",
    "role": "teacher",
    "org_id": 1,
    "org_name": "阳光幼儿园",
    "plan_type": "standard"
  }
}
```

### 1.2 获取个人信息

```
GET /api/v1/auth/profile
Header: Authorization: Bearer {token}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "nickname": "王老师",
    "avatar": "https://...",
    "phone": "13800138000",
    "role": "teacher",
    "org_id": 1,
    "org_name": "阳光幼儿园",
    "plan_type": "standard",
    "monthly_quota": 1500,
    "used_quota": 390,
    "remaining_quota": 1110,
    "plan_expire_at": "2027-02-01T00:00:00",
    "created_at": "2026-06-15T10:30:00"
  }
}
```

---

## 二、画作模块 `/artworks`

### 2.1 上传画作

```
POST /api/v1/artworks/upload
Header: Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**表单参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | 画作图片 (jpg/jpeg/png/webp/bmp, ≤20MB) |
| title | String | | 画作名称 |
| author_name | String | | 作者（幼儿名字） |
| source | String | | camera / album，默认 camera |

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": 12345,
    "title": "小明的太阳",
    "author_name": "小明",
    "original_url": "https://cdn.dopaint.com/artworks/original/abc123.jpg",
    "processed_url": "https://cdn.dopaint.com/artworks/processed/abc123.jpg",
    "thumbnail_url": "https://cdn.dopaint.com/artworks/thumb/abc123.jpg",
    "source": "camera",
    "status": "completed",
    "created_at": "2026-07-30T14:30:00"
  }
}
```

### 2.2 画作列表

```
GET /api/v1/artworks?page=1&page_size=20&status=&keyword=
Header: Authorization: Bearer {token}
```

**查询参数:**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 (1-100) |
| status | string | | 筛选状态，pending/processing/completed/failed |
| keyword | string | | 搜索关键词（匹配标题/作者名） |

**响应:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 12345,
        "title": "小明的太阳",
        "author_name": "小明",
        "thumbnail_url": "https://cdn.dopaint.com/artworks/thumb/abc123.jpg",
        "original_url": "https://cdn.dopaint.com/artworks/original/abc123.jpg",
        "source": "camera",
        "status": "completed",
        "created_at": "2026-07-30T14:30:00",
        "animation_count": 2,
        "latest_video_url": null
      }
    ],
    "total": 156,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  }
}
```

### 2.3 画作详情

```
GET /api/v1/artworks/{artwork_id}
Header: Authorization: Bearer {token}
```

### 2.4 删除画作

```
DELETE /api/v1/artworks/{artwork_id}
Header: Authorization: Bearer {token}
```

### 2.5 批量删除

```
POST /api/v1/artworks/batch-delete
Header: Authorization: Bearer {token}

Body: [12345, 12346, 12347]
```

---

## 三、动画模块 `/animations`

### 3.1 生成动画

```
POST /api/v1/animations/generate
Header: Authorization: Bearer {token}
```

**请求体:**
```json
{
  "artwork_id": 12345,
  "style_code": "magic_fairytale",
  "custom_prompt": "",
  "duration": 5,
  "resolution": "720p"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artwork_id | int | ✅ | 画作ID |
| style_code | string | ✅ | 风格编号，见提示词模板列表 |
| custom_prompt | string | | 自定义提示词（旗舰版可用），≤500字 |
| duration | int | | 视频时长(秒)，3/5/8，默认5 |
| resolution | string | | 480p/720p/1080p，默认720p |

**响应:**
```json
{
  "code": 0,
  "data": {
    "animation_id": 67890,
    "artwork_id": 12345,
    "status": "generating",
    "estimated_seconds": 30
  }
}
```

### 3.2 批量生成

```
POST /api/v1/animations/batch-generate
Header: Authorization: Bearer {token}
```

**请求体:**
```json
{
  "artwork_ids": [12345, 12346, 12347],
  "style_code": "magic_fairytale",
  "custom_prompt": "",
  "duration": 5,
  "resolution": "720p"
}
```

> artwork_ids 数量限制：1-30

**响应:**
```json
{
  "code": 0,
  "data": {
    "total": 3,
    "results": [
      {"artwork_id": 12345, "animation_id": 67890},
      {"artwork_id": 12346, "animation_id": 67891},
      {"artwork_id": 12347, "animation_id": 67892}
    ]
  }
}
```

### 3.3 查询动画状态（轮询接口）

```
GET /api/v1/animations/{animation_id}/status
Header: Authorization: Bearer {token}
```

**生成中状态:**
```json
{
  "code": 0,
  "data": {
    "animation_id": 67890,
    "artwork_id": 12345,
    "status": "generating",
    "video_url": null,
    "thumbnail_url": null,
    "duration": 5,
    "resolution": "720p",
    "prompt_style": "magic_fairytale",
    "error_msg": null,
    "created_at": "2026-07-30T14:30:00",
    "completed_at": null,
    "estimated_seconds": 15
  }
}
```

**完成状态:**
```json
{
  "code": 0,
  "data": {
    "animation_id": 67890,
    "artwork_id": 12345,
    "status": "completed",
    "video_url": "https://cdn.dopaint.com/videos/abc123.mp4",
    "thumbnail_url": "https://cdn.dopaint.com/thumbs/abc123.jpg",
    "duration": 5,
    "resolution": "720p",
    "prompt_style": "magic_fairytale",
    "error_msg": null,
    "created_at": "2026-07-30T14:30:00",
    "completed_at": "2026-07-30T14:30:35",
    "estimated_seconds": null
  }
}
```

**失败状态:**
```json
{
  "code": 0,
  "data": {
    "status": "failed",
    "error_msg": "AI服务暂时不可用，请稍后重试"
  }
}
```

### 3.4 动画列表

```
GET /api/v1/animations?page=1&page_size=20&status=&style=&artwork_id=
Header: Authorization: Bearer {token}
```

### 3.5 重试失败任务

```
POST /api/v1/animations/{animation_id}/retry
Header: Authorization: Bearer {token}
```

---

## 四、提示词模板 `/prompts`

### 4.1 获取可用模板列表

```
GET /api/v1/prompts
Header: Authorization: Bearer {token}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "total": 8,
    "items": [
      {
        "id": 1,
        "style_code": "magic_fairytale",
        "style_name": "魔法童话",
        "style_icon": "🧚",
        "description": "画面变成温馨童话世界，角色轻轻摆动微笑...",
        "category": "story",
        "default_duration": 5,
        "default_resolution": "720p",
        "thumbnail": "https://...",
        "demo_video_url": "https://...",
        "is_preset": true,
        "is_paid": false,
        "price": 0,
        "required_plan": null,
        "sort_order": 1
      }
    ]
  }
}
```

### 4.2 模板详情

```
GET /api/v1/prompts/{style_code}
Header: Authorization: Bearer {token}
```

---

## 五、机构管理 `/organizations`

> 需要园长/管理员角色（role=admin）

### 5.1 机构信息

```
GET  /api/v1/organizations/info       # 获取
PUT  /api/v1/organizations/info       # 更新
```

**更新请求体:**
```json
{
  "name": "阳光幼儿园",
  "contact_phone": "13800138000",
  "address": "XX市XX区XX路100号"
}
```

### 5.2 教师管理

```
GET    /api/v1/organizations/teachers            # 教师列表
POST   /api/v1/organizations/teachers            # 添加教师 { "user_id": 5 }
DELETE /api/v1/organizations/teachers/{user_id}  # 移除教师
```

### 5.3 用量统计

```
GET /api/v1/organizations/usage
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "monthly_quota": 1500,
    "used_quota": 390,
    "remaining": 1110,
    "total_animations": 120,
    "completed_animations": 115,
    "total_artworks": 156,
    "month": "2026-07"
  }
}
```

---

## 六、订单支付 `/orders`

### 6.1 获取套餐列表

```
GET /api/v1/orders/plans
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "org_plans": [
      {
        "plan_code": "standard",
        "plan_name": "标准版",
        "price": 4999,
        "original_price": 5999,
        "features": ["1,500次/月 生成量", "8种动画风格", ...],
        "monthly_quota": 1500,
        "teacher_limit": 15,
        "resolution": "1080p",
        "recommended": true
      }
    ],
    "personal_plans": [
      {
        "plan_code": "monthly",
        "plan_name": "个人月卡",
        "price": 29.9,
        "original_price": 39.9,
        "features": ["100次/月", "6种风格", "去水印"],
        "monthly_quota": 100
      }
    ]
  }
}
```

### 6.2 创建订单

```
POST /api/v1/orders/create
```

**请求体:**
```json
{
  "product_type": "org_plan",
  "product_id": "standard",
  "org_id": 1
}
```

### 6.3 发起支付

```
POST /api/v1/orders/{order_no}/pay
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "order_no": "20260730143000A1B2C3D4",
    "amount": 4999,
    "product_name": "标准版",
    "wx_pay_params": {
      "appId": "wx...",
      "timeStamp": "1751388600",
      "nonceStr": "...",
      "package": "prepay_id=...",
      "signType": "RSA",
      "paySign": "..."
    }
  }
}
```

### 6.4 订单列表

```
GET /api/v1/orders?page=1&page_size=20
```

---

## 七、完整业务流程示例

### 场景：老师给全班画作生成动画

```
第1步: 微信登录
  POST /api/v1/auth/login  {"code": "wx_code"}
  → 获取 access_token

第2步: 批量上传画作（循环调用）
  POST /api/v1/artworks/upload  (multipart, 30次)
  → 获得 30 个 artwork_id

第3步: 获取可用风格
  GET /api/v1/prompts
  → 选择 style_code

第4步: 批量生成动画
  POST /api/v1/animations/batch-generate
  {
    "artwork_ids": [12345, ...],
    "style_code": "magic_fairytale"
  }
  → 获得 30 个 animation_id

第5步: 轮询结果（前端每3秒轮询一次）
  GET /api/v1/animations/{animation_id}/status
  → status=completed 时获取 video_url

第6步: 下载/分享
  直接使用 video_url 下载或分享
```

---

## 八、前端调用建议

### 轮询策略

```javascript
// 生成动画后轮询状态
async function pollUntilComplete(animationId) {
  const maxAttempts = 40;  // 最多轮询40次（120秒）
  let attempts = 0;

  while (attempts < maxAttempts) {
    const res = await fetch(`/api/v1/animations/${animationId}/status`);
    const { data } = await res.json();

    if (data.status === 'completed') return data;
    if (data.status === 'failed') throw new Error(data.error_msg);

    await sleep(3000);  // 每3秒轮询
    attempts++;
  }
  throw new Error('生成超时');
}
```

### 批量上传优化

```javascript
// 并发上传，每次最多5个
async function batchUpload(files) {
  const concurrency = 5;
  const results = [];

  for (let i = 0; i < files.length; i += concurrency) {
    const batch = files.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map(f => uploadSingle(f))
    );
    results.push(...batchResults);
  }
  return results;
}
```
