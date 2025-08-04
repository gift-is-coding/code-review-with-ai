# Azure DevOps + AI 自动代码 Review 方案

本项目实现了在 Azure DevOps 平台下，基于自定义代码标准（txt），利用 AI 大模型（如 Kimi/Moonshot）对每次代码提交/PR 的变更内容进行自动化 review，并将审核结果自动归档到 Azure DevOps Wiki 和 Build Artifacts，便于团队追溯和持续改进。

---

## 设计理念与用户体验

1. **精准审查**：仅审查 Pull Request 或 Commit 的变更代码，避免全量扫描，聚焦于本次提交内容。
2. **多语言支持**：自动识别并审核常见前后端代码（如 Python、JavaScript、TypeScript、Java、Go、C++、Vue、HTML、CSS 等）。
3. **结果可追溯**：审核结果自动保存到 Azure DevOps Wiki 和 Build Artifacts，便于团队成员随时查阅和复盘。
4. **安全合规**：API Key 通过 Azure Pipeline Secret 管理，避免明文泄露。
5. **无感集成**：开发者只需正常提交 PR，审核流程自动触发，无需额外操作。
6. **灵活自定义**：代码标准可通过 txt 文件自定义，参数可通过 config.yaml 配置，支持团队个性化规范。

---

## 目录结构

- `code_standards.txt`    —— 代码标准文档（可自定义，推荐 txt 格式）
- `auto_review.py`        —— 自动 review 脚本，AI 审核 PR/commit 变更
- `azure-pipelines.yml`   —— Azure DevOps Pipeline 示例配置
- `config.yaml`           —— 参数配置文件
- `README.md`             —— 项目说明
- `result/`               —— 审核结果输出目录

---

## Azure DevOps 集成

### 推荐方案：Azure DevOps 直接使用 GitHub 源

1. **在 Azure DevOps 中配置 GitHub 连接**
   - 进入 Azure DevOps 项目 → `Project Settings` → `Service connections`
   - 点击 `New service connection` → 选择 `GitHub`
   - 授权 Azure DevOps 访问你的 GitHub 账户

2. **创建 Pipeline**
   - 进入 `Pipelines` → `New pipeline`
   - 选择 `GitHub` 作为代码源
   - 选择仓库 `gift-is-coding/code-review-with-ai`
   - 选择 `Existing Azure Pipelines YAML file`
   - 选择 `azure-pipelines.yml`

---

## 快速开始

### 1. 配置代码标准
编辑 `code_standards.txt`，定义你的团队代码规范。

### 2. 配置参数（推荐 config.yaml）
你可以将常用参数写入 `config.yaml`，如：
```yaml
moonshot_api_key: ${MOONSHOT_API_KEY}
standards: code_standards.txt
output: ai_review_result.md
pr_only: true
code_types: ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.cpp', '.vue', '.html', '.css']
# Azure DevOps Wiki 配置
wiki_url_base: ${WIKI_URL_BASE}
wiki_pat: ${WIKI_PAT}
```

> ⚠️ **安全提醒**：`config.yaml` 文件包含敏感信息（API Key、PAT Token），已被添加到 `.gitignore` 中，不会被提交到版本控制系统。请确保在本地创建此文件，并妥善保管其中的敏感信息。

### 3. 配置 API Keys 和 Wiki 设置
- 在 Azure DevOps 项目设置中，进入 `Pipelines > Library > Variable groups`，新建变量组如 `AI_CODE_REVIEW`。
- 添加以下变量：
  - `MOONSHOT_API_KEY`：Moonshot/Kimi API Key，勾选"Keep this value secret"
  - `WIKI_URL_BASE`：Azure DevOps Wiki API 基础地址
  - `WIKI_PAT`：用于 Wiki 上传的 PAT Token，勾选"Keep this value secret"

### 4. 配置 Azure DevOps Wiki
1. **获取 Wiki URL Base**：
   - 进入你的 Azure DevOps 项目
   - 点击 `Wiki` → 选择你的 Wiki
   - 在浏览器地址栏中，复制基础 URL，格式类似：
     ```
     https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wikiIdentifier}/pages
     ```

2. **创建 PAT Token**：
   - 进入 Azure DevOps → `User Settings` → `Personal access tokens`
   - 点击 `New Token`
   - 选择 `Custom defined`，设置权限：
     - `Wiki (Read & Write)`
   - 复制生成的 token

### 5. 集成到 Pipeline
- 在 `azure-pipelines.yml` 中，添加如下步骤：
```yaml
variables:
  - group: AI_CODE_REVIEW

steps:
  - script: |
      python auto_review.py \
        --moonshot_api_key $(MOONSHOT_API_KEY) \
        --wiki_url_base $(WIKI_URL_BASE) \
        --wiki_pat $(WIKI_PAT) \
        --pr_only
    displayName: 'Kimi AI 代码自动审核 + Wiki 上传'
```

### 6. 审核结果查看
- **Wiki 页面**：审核结果会自动上传到 Azure DevOps Wiki，每次生成唯一页面
- **Build Artifacts**：同时保存到 Build Artifacts，便于下载查看

---

## 用户流程

1. 开发者提交 PR。
2. Pipeline 自动触发，提取本次 PR/commit 的变更代码（支持多语言）。
3. `auto_review.py` 读取代码标准和变更代码，调用 Kimi/Moonshot API 进行审核。
4. 审核结果保存为 markdown 文件，并自动上传到 Azure DevOps Wiki。
5. 团队成员可在 Wiki 页面查看每次审核详情，便于复盘和持续改进。

---

## 最佳实践
- **只审查变更**：通过 pipeline 环境变量获取 diff，仅传递本次变更代码给 AI，提升效率和相关性。
- **API Key 安全**：严禁将 key 写入代码或明文配置，统一用 pipeline secret 管理。
- **结果归档**：使用 Wiki 和 Build Artifacts 双重存储审核结果，便于团队知识沉淀和检索。
- **标准可扩展**：支持多种规范文档格式，便于团队演进。
- **参数集中管理**：推荐用 config.yaml 管理参数，便于团队协作和复用。

---

## 参考
- [Azure DevOps Pipeline Secrets](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/variables)
- [Azure DevOps Build Artifacts](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/build-artifacts)
- [Azure DevOps Wiki API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/pages/create-or-update?view=azure-devops-rest-7.1)
- [Moonshot/Kimi API 文档](https://platform.moonshot.cn/docs/api-reference)

---

如需进一步定制或有其他需求，欢迎提出！ 