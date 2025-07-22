# Azure DevOps + AI 自动代码 Review 方案

本项目实现了在 Azure DevOps 平台下，基于自定义代码标准（docx），利用 AI 大模型（如 OpenAI GPT）对**每次代码提交/PR**的变更内容进行自动化 review，并将审核结果自动归档，便于团队追溯和持续改进。

---

## 设计理念与用户体验

1. **精准审查**：仅审查 Pull Request 或 Commit 的变更代码，避免全量扫描，聚焦于本次提交内容。
2. **多语言支持**：自动识别并审核常见前后端代码（如 Python、JavaScript、TypeScript、Java、Go、C++、Vue、HTML、CSS 等）。
3. **结果可追溯**：审核结果自动保存到 Azure DevOps Wiki（推荐）或 Artifacts，便于团队成员随时查阅和复盘。
4. **安全合规**：API Key 通过 Azure Pipeline Secret 管理，避免明文泄露。
5. **无感集成**：开发者只需正常提交 PR，审核流程自动触发，无需额外操作。
6. **灵活自定义**：代码标准可通过 docx 文件自定义，参数可通过 config.yaml 配置，支持团队个性化规范。

---

## 目录结构

- `code_standards.txt`  —— 代码标准文档（可自定义）
- `auto_review.py`      —— 自动 review 脚本，AI 审核 PR/commit 变更
- `azure-pipelines.yml` —— Azure DevOps Pipeline 示例配置
- `config.yaml`         —— （可选）参数配置文件
- `README.md`           —— 项目说明

---

## 快速开始

### 1. 配置代码标准
编辑 `code_standards.txt`，定义你的团队代码规范。

### 2. 配置参数（推荐 config.yaml）
你可以将常用参数写入 `config.yaml`，如：
```yaml
moonshot_api_key: ${MOONSHOT_API_KEY}   # 推荐用 pipeline secret 注入
standards: code_standards.docx
output: ai_review_result.md
pr_only: true
code_types: ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.cpp', '.vue', '.html', '.css']
wiki_url: https://dev.azure.com/yourorg/yourproject/_apis/wiki/wikis/yourwiki/pages?path=/AIReview
wiki_pat: $(WIKI_PAT)
```
命令行参数优先级高于配置文件。

### 3. 配置 OpenAI API Key
- 在 Azure DevOps 项目设置中，进入 `Pipelines > Library > Variable groups`，新建变量组如 `ai-secrets`。
- 添加变量 `OPENAI_API_KEY`，勾选“Keep this value secret”。
- 在 pipeline yaml 中引用该变量组。

### 4. 集成到 Pipeline
- 在 `azure-pipelines.yml` 中，添加如下步骤：
```yaml
variables:
  - group: ai-secrets

steps:
  # ... 其他步骤 ...
  - script: python auto_review.py --openai_api_key $(OPENAI_API_KEY)
    displayName: 'AI 代码自动审核'
```
- 推荐在 PR 触发的 pipeline（如 `trigger: none`, `pr: [main]`）中集成。

### 5. 审核结果归档
- `auto_review.py` 会将审核结果保存为 markdown 文件（如 `ai_review_result.md`）。
- 可通过 pipeline 步骤自动上传到 Azure DevOps Wiki（推荐，见下方脚本）或 Artifacts。

#### 示例：自动上传审核结果到 Wiki
可使用 [Azure DevOps Wiki API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/pages/create-or-update?view=azure-devops-rest-7.1) 或社区扩展任务，将 `ai_review_result.md` 自动推送到指定 Wiki 页面。

---

## 用户流程

1. 开发者提交 PR。
2. Pipeline 自动触发，提取本次 PR/commit 的变更代码（支持多语言）。
3. `auto_review.py` 读取代码标准和变更代码，调用 OpenAI API 进行审核。
4. 审核结果保存为 markdown 文件，并自动归档到 Wiki/Artifacts。
5. 团队成员可在 Wiki 查看每次审核详情，便于复盘和持续改进。

---

## 最佳实践
- **只审查变更**：通过 pipeline 环境变量（如 `System.PullRequest.SourceBranch`、`System.PullRequest.TargetBranch`）获取 diff，仅传递本次变更代码给 AI，提升效率和相关性。
- **API Key 安全**：严禁将 key 写入代码或明文配置，统一用 pipeline secret 管理。
- **结果归档**：优先推荐 Wiki，便于团队知识沉淀和检索。
- **标准可扩展**：支持多种规范文档格式，便于团队演进。
- **参数集中管理**：推荐用 config.yaml 管理参数，便于团队协作和复用。

---

## 参考
- [Azure DevOps Pipeline Secrets](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables)
- [Azure DevOps Wiki API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/pages/create-or-update?view=azure-devops-rest-7.1)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)

---

如需进一步定制或有其他需求，欢迎提出！ 