# WonderWiki - 记忆维基 v0.1

一个基于 Obsidian 笔记的静态知识库前端，提供搜索、分类浏览、知识图谱等功能。

## 快速开始

### 1. 配置路径

编辑以下文件，把路径改成你的 Obsidian vault 位置：

- `scanner.py` 第 20 行：`VAULT = r'你的vault路径'`
- `api_server.py` 第 13-14 行：`VAULT` 和 `DATA_DIR`

### 2. 扫描 vault（一次性）

```bash
python scanner.py
```

这会扫描你的 Obsidian vault，生成 `data/index.json`。

### 3. 启动服务（两个终端）

**终端 1 — API 服务器（端口 19998）：**
```bash
python api_server.py
```

**终端 2 — 前端静态服务器（端口 19999）：**
```bash
python serve.py
```

### 4. 打开浏览器

访问 `http://127.0.0.1:19999/`

## 功能

- 文件列表浏览
- 全文搜索
- 分类统计
- 知识图谱可视化（D3.js）
- 双向链接展示
- 在 Obsidian 中打开（需安装 Obsidian 并注册 obsidian:// 协议）

## 文件说明

| 文件 | 用途 |
|------|------|
| `scanner.py` | 扫描 Obsidian vault，生成 index.json |
| `api_server.py` | API 服务器（搜索、打开文件等） |
| `serve.py` | 前端静态文件服务器 |
| `index.html` | 前端页面 |
| `.gitignore` | Git 忽略规则（排除 data/） |

## 注意事项

- 需要 Python 3.8+
- 需要 PyYAML 库：`pip install pyyaml`
- 仅支持 Windows 的 `obsidian://` 协议（Mac/Linux 需自行适配）
- 不修改你的 Obsidian vault 文件，只读扫描

## 分享给朋友的完整步骤

### 包含的内容

```
wonderwiki-clean/
├── scanner.py          # 扫描 Obsidian vault，生成 index.json
├── api_server.py       # API 后端（搜索、打开文件等）
├── serve.py            # 前端静态服务器
├── index.html          # 前端页面
├── .gitignore          # Git 忽略规则（data/ 被忽略）
└── README.md           # 本文件
```

### 接收方操作步骤

1. **克隆或下载** 仓库到任意目录

2. **配置路径** — 编辑以下两个文件，把路径改成自己的 Obsidian vault 位置：
   - `scanner.py` 第 20 行：`VAULT = r'你的vault路径'`
   - `api_server.py` 第 13-14 行：`VAULT` 和 `DATA_DIR`

3. **扫描 vault**（生成 index.json）：
   ```bash
   python scanner.py
   ```

4. **启动两个服务**（各开一个终端窗口）：
   
   终端 1 — API 服务器（端口 19998）：
   ```bash
   python api_server.py
   ```
   
   终端 2 — 前端静态服务器（端口 19999）：
   ```bash
   python serve.py
   ```

5. **打开浏览器**，访问 `http://127.0.0.1:19999/`

6. （可选）在 Obsidian 中打开文件：确保 Obsidian 已安装且注册了 `obsidian://` 协议

### 常见问题

- **Q: 提示 "ModuleNotFoundError: No module named 'yaml'"**
  - A: 运行 `pip install pyyaml`

- **Q: 点击"在 Obsidian 中打开"没反应**
  - A: 确认 Obsidian 已安装且设置了 URI Handler（Obsidian 设置 → 高级 → 确保 "Deep links" 开启）

- **Q: Mac / Linux 能用吗**
  - A: 代码本身跨平台，但 `api_server.py` 的 `/api/open` 用了 Windows explorer 命令。Mac/Linux 需改成 `open` 或 `xdg-open`。

---

## 知识体系说明



# 个人知识库搭建体系

## 三件套

| 角色 | 工具 | 职责 |
|------|------|------|
| **怎么写** | LLM Wiki 方法论 | 知识结构化规范、实体/概念提取、双向链接 |
| **怎么读** | Obsidian | 编辑器、双向链接渲染、图谱视图 |
| **怎么管** | WonderWiki | 剪藏分类、全文搜索、批量仪表盘、可视化知识图谱 |

## 核心原则

- **LLM Wiki** 负责写入侧：读一篇文章，提取实体和概念，建立双向链接，形成可增长的知识库
- **Obsidian** 负责阅读侧：用编辑器浏览、用图谱视图发现关联
- **WonderWiki** 负责管理侧：每天剪藏几十篇文章，cron 自动整理分类，Web 界面提供搜索、仪表盘、知识图谱

## 三者关系

```
剪藏文章 → LLM Wiki（结构化写入） → Obsidian（阅读浏览）
                                    ↓
                              WonderWiki（搜索/分类/可视化）
                                    ↑
                              Hermes Cron（自动化流转）
```

- WonderWiki **不碰 vault 文件**，只读索引，不影响 Obsidian 知识库
- Hermes Cron 负责自动化：每天凌晨自动整理剪藏、自动刷新索引
- 三者各司其职，互不干扰

## 搭建步骤

### 1. 安装基础工具
- Obsidian（编辑器）
- Obsidian Web Clipper（浏览器剪藏插件）
- Hermes Agent（自动化调度）

### 2. 建立 LLM Wiki 结构
```
vault/
├── wiki/
│   ├── entities/        # 人、产品、公司
│   ├── concepts/        # 概念、方法论
│   ├── sources/         # 原始剪藏
│   ├── index.md         # 索引
│   └── log.md           # 操作日志
├── raw/
│   └── Clippings/       # 待分类剪藏
└── daily/               # 日记
```

### 3. 配置自动化
- **Obsidian Clippings Cron**：每天凌晨自动整理 `raw/Clippings/` 到对应分类
- **WonderWiki Cron**：每天凌晨自动扫描 vault 更新索引

### 4. 使用 WonderWiki
- 访问 `http://localhost:19999`
- 仪表盘查看 vault 健康度
- 搜索全文（不只是标题）
- 批量分类未处理的剪藏
- 知识图谱查看关联密度

## 为什么需要三件套？

一个人管理知识库的典型流程：

1. **收集**：Web Clipper 剪藏文章 → `raw/Clippings/`
2. **整理**：Hermes Cron 自动分类 → 移动到 `raw/ai-agents/` 等
3. **提炼**：LLM Wiki 提取实体/概念 → 创建 `wiki/entities/` 和 `wiki/concepts/`
4. **阅读**：Obsidian 浏览、图谱视图
5. **管理**：WonderWiki 搜索、分类助手、仪表盘

每一步都自动化了，人只需要做两件事：**读文章**和**做决策**。

## 技术细节

- **LLM Wiki**：基于 Karpathy 的方法论，用 AI 辅助结构化知识
- **Obsidian**：本地 Markdown 文件，Git 版本控制
- **WonderWiki**：Python 扫描 + HTML 前端，D3.js 知识图谱
- **Hermes Cron**：定时任务调度自动化流程

## 分享

这套体系适合：
- 每天剪藏大量文章的读者
- 需要管理多个知识领域的研究者
- 想用 AI 辅助知识管理的人

核心思路：**自动化收集 + 结构化写入 + 可视化浏览**，人只做决策。
```
