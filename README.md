
# VisionAgent-Test: AI视觉驱动的UI自动化测试平台

**VisionAgent-Test** 是一款基于**大语言模型（LLM）视觉能力**的下一代UI自动化测试平台。它将复杂的UI自动化测试流程，从编写繁琐的选择器（Selector）和断言代码，转变为**使用自然语言描述测试目标**。

平台结合了**AI视觉识别**、**多智能体（Multi-Agent）协作**和**实时浏览器控制**，让任何人都能够快速创建、执行和管理UI自动化测试，极大地提升了测试效率和覆盖率。

## 🎥 核心功能演示

点击下方视频，快速了解VisionAgent-Test如何通过自然语言指令，智能地理解UI界面并完成自动化操作。
[![VisionAgent-Test 演示视频](./assets/video_cover.png)](https://www.bilibili.com/video/BV1wnJXzJEny/)

---

## 🤖 核心架构：AI如何“看见”并“操作”

VisionAgent-Test 的核心是**视觉驱动的执行循环**。它模仿人类测试员的工作方式：观察界面 -> 思考下一步 -> 执行操作。

<img width="1785" alt="AI视觉驱动流程图" src="https://github.com/user-attachments/assets/335fa852-8fb0-477d-9cbe-c4bb6432e162" />

1.  **用户输入目标 (User Input)**：用户提供一个高阶的测试步骤，如“点击登录按钮”或“输入用户名 admin”。
2.  **视觉分析 (Visual Analysis)**：系统自动截取当前浏览器屏幕，并将截图与用户目标一同发送给AI视觉模型。
3.  **动作规划 (Action Planning)**：AI模型“观察”截图，理解页面上的元素布局和内容，然后规划出具体的执行动作（如点击坐标 `(x, y)`，或在某个输入框内打字）。
4.  **指令执行 (Command Execution)**：后端接收AI生成的动作指令，并驱动浏览器自动化工具（如Selenium/Playwright）来精确执行。
5.  **循环验证 (Loop & Verify)**：执行完一个子操作后，系统会再次截图，进行下一步或验证结果，直至整个测试步骤完成。

---

## ✨ 平台特色功能

| 功能模块 (UI自动化)      | 描述                                                         |
| ------------------------ | ------------------------------------------------------------ |
| 👁️ **自然语言驱动**      | 无需编写代码，用自然语言描述测试步骤，AI自动执行。           |
| 📸 **实时视觉反馈**      | 在执行过程中，前端实时展示浏览器截图，直观了解AI的每一步操作。 |
| ⏯️ **灵活的执行控制**    | 支持“全部运行”和“单步调试”模式，方便快速验证和问题定位。       |
| ✍️ **脚本绘制与编辑**    | AI生成的执行计划可被“绘制”成可视化脚本，支持手动修改、增加和删除步骤，实现人机协作。 |
| 🧠 **多Agent测试策略** | 内置多种AI Agent，从不同维度（正向、边界、异常等）生成更全面的自动化测试计划。 |

| 功能模块 (测试管理)      | 描述                                                         |
| ------------------------ | ------------------------------------------------------------ |
| 📁 **项目与模块管理**    | 支持多项目、多模块的组织结构，清晰地管理测试资产。           |
| 🧾 **用户故事与用例**    | 以用户故事为核心，关联传统的手工测试用例和AI生成的自动化脚本。 |
| 🤖 **上下文AI助手**      | 在用户故事详情页提供AI聊天助手，快速解答测试点、生成数据等。   |
| 🧼 **会话隔离**         | 使用 `session_id` 确保每个用户的AI会话上下文独立、安全。     |

---

## 🧠 多维度测试计划生成 (Maker组)

为了提升自动化用例的覆盖广度，我们引入了并联式的 **Maker组** 设计。当用户输入一个用户故事后，可以激活不同的AI Agent，从各自的专业角度生成自动化测试计划。

<img width="1547" alt="Maker组架构图" src="https://github.com/user-attachments/assets/51019305-6483-4f46-beae-371c088d19f6" />

-   **Positive Case Agent**：生成正常业务流程的“Happy Path”自动化步骤。
-   **边界值分析师 (Boundary Value Analyst)**：生成针对输入框、数字范围等边界条件的自动化步骤，如“输入最大长度字符”。
-   **错误场景推演师 (Error Guessing Specialist)**：生成模拟用户错误操作的步骤，如“输入错误的密码格式后点击登录”。
-   **状态机攻击手 (State Machine Attacker)**：生成非典型路径或异常状态转换的复杂操作序列。

---

## 🖼️ 平台截图

1.  **实时自动化执行界面**
    > 实时日志、步骤状态和浏览器截图一目了然。

    <img width="1489" alt="实时自动化执行界面" src="https://github.com/user-attachments/assets/9030fd16-6b3a-40aa-829d-25ffe9ea162a" />

2.  **测试管理与AI助手**
    > 传统的测试用例管理与强大的AI上下文助手无缝集成。

    <img width="1511" alt="测试管理界面" src="https://github.com/user-attachments/assets/7e537f01-2137-46e9-9ba0-d32203362eb8" />

3.  **脚本绘制与手动编辑 (功能概念图)**
    > AI生成的计划可以被导入到脚本编辑器中，进行可视化调整和保存。

    <img width="1542" alt="脚本编辑器" src="https://github.com/user-attachments/assets/0606e2a0-9e34-4f50-a7ab-5351c0c04987" />

---

## 🧱 技术栈

| 分类         | 技术                                                         |
| ------------ | ------------------------------------------------------------ |
| 后端         | Flask + SQLAlchemy + Socket.IO                             |
| 数据库       | SQLite（默认，可替换为 MySQL/PostgreSQL）                    |
| 前端         | Bootstrap 5 + Jinja2 + Vanilla JS                            |
| AI能力       | OpenAI API / Moonshot API (需支持视觉识别和Function Calling) |
| 浏览器自动化 | Selenium / Playwright (或其他浏览器驱动)                     |

---

## 🚀 快速开始

1.  **克隆仓库**
    ```bash
    git clone https://github.com/your-username/VisionAgent-Test.git
    cd VisionAgent-Test
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **配置环境变量**
    > 在项目根目录创建 `.env` 文件，并填入你的AI模型API密钥。
    ```
    OPENAI_API_KEY="sk-..."
    ```

4.  **运行应用**
    ```bash
    python app.py
    ```

5.  **访问地址**
    `http://localhost:5000/`

---

## 📚 数据模型关系

项目采用经典的项目管理层级结构，确保测试资产的组织性和可追溯性。

```text
Project 1---* Module 1---* UserStory 1---* (TestCase + AutomatedScript)
```

-   一个**项目**包含多个**模块**。
-   一个**模块**下有多个**用户故事**（User Story）。
-   每个**用户故事**关联多个**测试用例**（Test Case）和一个或多个**自动化脚本**（Automated Script）。
