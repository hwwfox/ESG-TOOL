# ESG-TOOL

AI 驱动的 ESG 报告编写工具，基于多智能体协作模式自动生成符合上交所《可持续发展报告披露指引与编写指南》与 GRI 标准的报告草案、重要性分析及过程性文件。系统包含可交互的 Web 界面，方便用户输入企业信息、确认成果并下载归档文件。

## 功能亮点

- **多代理工作流**：StakeholderAnalysis、Materiality、PolicyBenchmark、PeerBenchmark、ReportCompiler 等智能体顺序运行，覆盖利益相关方分析、重要性矩阵构建、政策与同业对标以及报告草案生成。
- **指南对标**：内置上交所披露指引和 GRI 标准的关键条款映射，自动为议题与政策评估提供引用来源。
- **过程性文件归档**：每次运行会生成政策对标清单、同业对标分析及用户确认记录，并以 JSON 形式归档，支持随时下载。
- **用户交互确认**：Web 审阅界面支持勾选确认章节、填写补充意见，形成可追溯的确认记录。

## 快速开始

### 1. 创建环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动 Web 应用

```bash
export FLASK_APP=esg_tool.ui.app:app
flask run
```

浏览器访问 `http://127.0.0.1:5000`，按照流程填写企业信息即可触发多代理工作流并生成成果。

### 3. 文件归档

- 所有运行结果会保存至 `storage/archives/<package_id>` 下的 `package.json`。
- 可在“成果归档”页面查看历史记录，并下载：
  - 报告草案（TXT）
  - 政策对标 / 同业对标 / 用户确认等过程性文件（JSON）

## 目录结构

```
├── docs/
│   └── workflow.md              # 多代理工作流说明
├── esg_tool/
│   ├── agents/                  # 各智能体实现
│   ├── services/                # 指南映射等共享服务
│   ├── storage/                 # 存储相关模块
│   ├── ui/                      # Flask Web 界面与模板
│   ├── utils/                   # 工具函数
│   ├── workflows/               # 工作流编排
│   └── models.py                # 核心数据模型
├── storage/archives/.gitkeep    # 归档目录占位
└── README.md
```

## 后续拓展建议

- 集成量化指标采集及可视化模块。
- 扩展英文版报告生成，支持多语言披露。
- 接入企业内部制度、数据仓库，实现实时数据驱动的披露内容自动填充。
