# 平台2：🧪 测试管理平台 Test Management Platform

一个轻量级、结构清晰、支持 AI 辅助的测试用例管理平台，旨在帮助团队高效地组织用户故事、模块、测试用例，并集成 AI 助手快速分析与问答。

---

## ✨ 平台特色功能

| 功能模块      | 描述                                      |
| --------- | --------------------------------------- |
| 📁 项目管理   | 支持多个项目的创建与管理                            |
| 📦 模块管理   | 每个项目下可配置多个模块，模块下可维护用户故事                 |
| 🧾 用户故事管理 | 每个模块下可创建多个用户故事（User Story），便于聚焦具体功能点    |
| 🧪 测试用例管理 | 每个用户故事可关联多个测试用例，支持详细字段填写与状态追踪           |
| 🤖 AI 助手  | 基于大语言模型的对话式助手，可针对当前用户故事上下文快速回答测试相关问题    |
| 🔍 用例查询   | 支持 accordion 折叠方式查看全部测试用例详情，清晰可视        |
| 🧼 会话隔离   | 使用 `session_id` 管理用户会话，刷新后重新生成，保障上下文私有性 |
| 🧾 流式响应   | AI 助手支持流式输出，增强交互体验与响应速度                 |

---

## 🧱 技术栈

| 分类   | 技术                                |
| ---- | --------------------------------- |
| 后端   | Flask + SQLAlchemy                |
| 数据库  | SQLite（默认，可替换为 MySQL/PostgreSQL）  |
| 前端   | Bootstrap 5 + Jinja2              |
| AI能力 | OpenAI API / Moonshot API（支持流式输出） |
| 浏览器端 | Vanilla JS + Fetch API            |

---

## 📦 项目结构简述

```
your_project/
├── app.py                  # 主应用入口
├── models.py               # 数据模型（Project / Module / UserStory / TestCase）
├── templates/
│   ├── base.html           # 公共模板
│   └── userstory_detail.html  # 用户故事 + 用例 + AI 聊天界面
├── static/
│   └── ...                 # 样式、图标等
├── db.sqlite3              # 默认数据库文件
└── README.md               # 当前文档
```

---

## 🚀 快速开始

1. **安装依赖**

   ```bash
   pip install flask sqlalchemy
   ```

2. **运行应用**

   ```bash
   python app.py
   ```

3. **访问地址**

   ```
   http://localhost:5000/
   ```

---

## 🤖 AI 助手说明

* 通过右侧聊天框提问，例如：

  * 「这个用户故事有哪些关键测试点？」
  * 「帮我总结一下这几个测试用例的目的」
* 每次请求携带当前 `userstory_id` 和 `session_id`，确保上下文一致
* 支持 OpenAI / Moonshot 等模型，推荐使用带 **stream** 的接口以支持流式对话
<img width="1489" height="861" alt="image" src="https://github.com/user-attachments/assets/9030fd16-6b3a-40aa-829d-25ffe9ea162a" />
---


## 📚 数据模型关系

```text
Project 1---* Module 1---* UserStory 1---* TestCase
```

* 一个项目有多个模块
* 一个模块下有多个用户故事（User Story）
* 每个用户故事关联多个测试用例（Test Case）
<img width="1511" height="509" alt="image" src="https://github.com/user-attachments/assets/7e537f01-2137-46e9-9ba0-d32203362eb8" />
<img width="1542" height="417" alt="image" src="https://github.com/user-attachments/assets/0606e2a0-9e34-4f50-a7ab-5351c0c04987" />

---

## 🔐 会话管理说明

平台使用两种会话机制：

* **Flask Session**：后端使用 Cookie 加密保存 `session_id`，刷新默认保持。
* **JS localStorage**（可选）：前端生成 UUID 存储并发送，用于更精细控制。

> 可根据实际使用选择方案，也可扩展 Redis 等持久化 session。

---
