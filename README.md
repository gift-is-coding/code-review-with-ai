# Azure DevOps + AI 自动代码 Review 模板

本项目提供了 Azure DevOps Pipeline 模板，用于在多个项目中实现 AI 自动代码审核。基于自定义代码标准（txt），利用 AI 大模型（如 Kimi/Moonshot）对每次代码提交/PR 的变更内容进行自动化 review，并将审核结果自动归档到 Azure DevOps Wiki 和 Build Artifacts，便于团队追溯和持续改进。

## 🎯 核心特性

- **模板化架构**：提供可复用的 Pipeline 模板，避免重复配置
- **多技术栈支持**：内置 Python、JavaScript、Java 等标准
- **统一管理**：集中管理审核标准和配置
- **易于集成**：目标项目只需几行配置即可启用 AI 审核

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

```
code-review-with-ai/
├── templates/
│   └── ai-review.yml              # 主模板文件
├── standards/
│   ├── python_standards.txt       # Python 代码标准
│   ├── javascript_standards.txt   # JavaScript 代码标准
│   └── java_standards.txt         # Java 代码标准
├── examples/
│   ├── python-project/            # Python 项目示例
│   ├── javascript-project/        # JavaScript 项目示例
│   └── java-project/              # Java 项目示例
├── auto_review.py                 # 核心审核脚本
├── test_wiki.py                   # Wiki 连接测试脚本
├── requirements.txt               # Python 依赖
├── config.yaml                    # 本地配置文件
├── azure-pipelines.yml            # 当前项目 Pipeline
└── README.md                      # 项目文档
```

---

## 🚀 快速开始

### 方案一：在目标项目中使用模板（推荐）

1. **在目标项目中创建 Pipeline 文件**

```yaml
# 目标项目的 azure-pipelines.yml
trigger:
  - main

pr:
  - main

extends:
  template: https://github.com/gift-is-coding/code-review-with-ai/templates/ai-review.yml
  parameters:
    projectName: 'your-project-name'
    standardsFile: 'standards/python_standards.txt'  # 根据技术栈选择
    codeTypes:
      - '.py'
      - '.js'
      - '.ts'
    enableWikiUpload: true
    enableArtifacts: true
```

2. **配置 Azure DevOps 变量组**
   - 在 Azure DevOps 中创建变量组 `AI_CODE_REVIEW`
   - 添加变量：
     - `MOONSHOT_API_KEY`：Moonshot/Kimi API Key
     - `WIKI_URL_BASE`：Azure DevOps Wiki API 基础地址
     - `WIKI_PAT`：用于 Wiki 上传的 PAT Token

### 方案二：本地开发和测试

1. **克隆模板仓库**
```bash
git clone https://github.com/gift-is-coding/code-review-with-ai.git
cd code-review-with-ai
```

2. **配置本地环境**
```yaml
# config.yaml
moonshot_api_key: your-api-key
wiki_url_base: https://dev.azure.com/giiift/test-for-HLS/_wiki/wikis/test-for-HLS.wiki/
wiki_pat: your-pat-token
```

3. **测试 Wiki 连接**
```bash
python test_wiki.py
```

4. **运行代码审核**
```bash
python auto_review.py --project_name "test-project" --pr_only
```

---

## 快速开始

## 📋 使用指南

### 1. 选择技术栈标准

根据你的项目技术栈，选择合适的标准文件：

| 技术栈 | 标准文件 | 支持的文件类型 |
|--------|----------|----------------|
| Python | `standards/python_standards.txt` | `.py`, `.pyx`, `.pyi` |
| JavaScript | `standards/javascript_standards.txt` | `.js`, `.ts`, `.jsx`, `.tsx`, `.vue` |
| Java | `standards/java_standards.txt` | `.java`, `.xml`, `.properties` |

### 2. 配置项目参数

在目标项目的 Pipeline 中配置参数：

```yaml
extends:
  template: https://github.com/gift-is-coding/code-review-with-ai/templates/ai-review.yml
  parameters:
    projectName: 'your-project-name'           # 项目名称
    standardsFile: 'standards/python_standards.txt'  # 标准文件
    codeTypes:                                 # 审核的文件类型
      - '.py'
      - '.js'
      - '.ts'
    enableWikiUpload: true                     # 是否上传到 Wiki
    enableArtifacts: true                      # 是否发布到 Artifacts
```

### 3. 自定义代码标准

你可以创建自定义的标准文件：

```txt
# custom_standards.txt
你的团队代码标准：

1. 代码风格
   - 遵循团队约定
   - 使用统一的格式化工具

2. 命名规范
   - 变量和函数命名规则
   - 类名命名规则

3. 其他规范
   - 错误处理要求
   - 文档要求
   - 测试要求
```

## 🔧 配置说明

### 1. Azure DevOps 变量组配置

在 Azure DevOps 中创建变量组 `AI_CODE_REVIEW`：

1. **进入项目设置**：`Project Settings` → `Library`
2. **创建变量组**：点击 `+ Variable group`
3. **添加变量**：
   - `MOONSHOT_API_KEY`：Moonshot/Kimi API Key（勾选"Keep this value secret"）
   - `WIKI_URL_BASE`：Azure DevOps Wiki API 基础地址
   - `WIKI_PAT`：用于 Wiki 上传的 PAT Token（勾选"Keep this value secret"）

### 2. Wiki 配置

1. **获取 Wiki URL Base**：
   - 进入 Azure DevOps 项目
   - 点击 `Wiki` → 选择你的 Wiki
   - 复制基础 URL，格式类似：
     ```
     https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wikiIdentifier}/
     ```

2. **创建 PAT Token**：
   - 进入 `User Settings` → `Personal access tokens`
   - 点击 `New Token`
   - 设置权限：`Wiki (Read & Write)`
   - 复制生成的 token

## 📝 完整示例

### Python 项目示例

```yaml
# python-project/azure-pipelines.yml
trigger:
  - main

pr:
  - main

extends:
  template: https://github.com/gift-is-coding/code-review-with-ai/templates/ai-review.yml
  parameters:
    projectName: 'python-project'
    standardsFile: 'standards/python_standards.txt'
    codeTypes:
      - '.py'
      - '.pyx'
      - '.pyi'
    enableWikiUpload: true
    enableArtifacts: true
```

### JavaScript 项目示例

```yaml
# js-project/azure-pipelines.yml
trigger:
  - main

pr:
  - main

extends:
  template: https://github.com/gift-is-coding/code-review-with-ai/templates/ai-review.yml
  parameters:
    projectName: 'js-project'
    standardsFile: 'standards/javascript_standards.txt'
    codeTypes:
      - '.js'
      - '.ts'
      - '.jsx'
      - '.tsx'
      - '.vue'
    enableWikiUpload: true
    enableArtifacts: true
```

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