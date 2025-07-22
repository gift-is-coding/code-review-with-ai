# Azure DevOps 自动代码 Review 工程

本项目实现了在 Azure DevOps 平台下，基于自定义代码标准（docx），对代码提交进行自动化 review，并生成反馈，供人工确认。

## 目录结构

- `code_standards.docx`  —— 代码标准文档（可自定义）
- `auto_review.py`      —— 自动 review 脚本，读取 docx 并检查代码
- `azure-pipelines.yml` —— Azure DevOps Pipeline 示例配置
- `README.md`           —— 项目说明

## 快速开始

1. 修改 `code_standards.docx`，定义你的代码规范。
2. 使用 `auto_review.py` 检查代码是否符合规范。
3. 在 Azure DevOps Pipeline 中集成本脚本，实现自动化 review。

## 用法

### 本地运行
```bash
python auto_review.py --code_path <待检查代码目录或文件>
```

### Azure DevOps 集成
在 `azure-pipelines.yml` 中添加如下步骤：
```yaml
- script: python auto_review.py --code_path $(Build.SourcesDirectory)
```

## 反馈与人工确认
自动 review 结果会输出到控制台或 pipeline 日志，供开发者人工确认和处理。

---

如需自定义规则或集成方式，请参考各文件注释。 