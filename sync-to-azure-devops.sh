#!/bin/bash

# 同步 GitHub 代码到 Azure DevOps 的脚本
# 使用方法: ./sync-to-azure-devops.sh

set -e

# 配置变量
GITHUB_REPO="https://github.com/gift-is-coding/code-review-with-ai.git"
AZURE_DEVOPS_REPO="https://dev.azure.com/YOUR_ORG/YOUR_PROJECT/_git/YOUR_REPO"
TEMP_DIR="temp_sync"

echo "开始同步 GitHub 代码到 Azure DevOps..."

# 清理临时目录
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# 克隆 Azure DevOps 仓库
echo "克隆 Azure DevOps 仓库..."
git clone "$AZURE_DEVOPS_REPO" "$TEMP_DIR"

# 进入临时目录
cd "$TEMP_DIR"

# 备份 Azure DevOps 特定的文件（如果有的话）
if [ -f "azure-pipelines.yml" ]; then
    cp azure-pipelines.yml azure-pipelines.yml.backup
fi

# 清空目录（保留 .git）
find . -mindepth 1 -not -path './.git*' -delete

# 从 GitHub 复制最新代码
echo "从 GitHub 复制最新代码..."
git clone --depth 1 "$GITHUB_REPO" temp_github
cp -r temp_github/* .
rm -rf temp_github

# 恢复 Azure DevOps 特定的文件
if [ -f "azure-pipelines.yml.backup" ]; then
    cp azure-pipelines.yml.backup azure-pipelines.yml
    rm azure-pipelines.yml.backup
fi

# 提交并推送
echo "提交更改到 Azure DevOps..."
git add .
git commit -m "Sync from GitHub: $(date)" || echo "没有更改需要提交"
git push

# 清理
cd ..
rm -rf "$TEMP_DIR"

echo "同步完成！" 