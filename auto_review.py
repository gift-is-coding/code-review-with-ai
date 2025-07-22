import sys
import os
import argparse
from docx import Document
import subprocess
import yaml
import requests

SUPPORTED_EXTS = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.cpp', '.c', '.cs', '.vue', '.html', '.css', '.json', '.sh']


def load_config(config_path='config.yaml'):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_standards(docx_path):
    doc = Document(docx_path)
    rules = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            rules.append(text)
    return '\n'.join(rules)


def get_changed_files(pr_only, code_types=None):
    if code_types is None:
        code_types = SUPPORTED_EXTS
    changed_files = []
    if pr_only:
        base = os.environ.get('SYSTEM_PULLREQUEST_TARGETBRANCH')
        head = os.environ.get('SYSTEM_PULLREQUEST_SOURCEBRANCH')
        if base and head:
            base = base.replace('refs/heads/', '')
            head = head.replace('refs/heads/', '')
            diff_cmd = f'git diff --name-only origin/{base}...origin/{head}'
        else:
            diff_cmd = 'git diff --name-only HEAD~1'
        result = subprocess.run(diff_cmd, shell=True, capture_output=True, text=True)
        files = [f for f in result.stdout.splitlines() if os.path.splitext(f)[1] in code_types]
        for f in files:
            diff_content = subprocess.run(f'git diff {f}', shell=True, capture_output=True, text=True).stdout
            if not diff_content:
                with open(f, 'r', encoding='utf-8') as file:
                    diff_content = file.read()
            changed_files.append((f, diff_content))
    else:
        for root, _, files in os.walk('.'):
            for f in files:
                if os.path.splitext(f)[1] in code_types:
                    fpath = os.path.join(root, f)
                    with open(fpath, 'r', encoding='utf-8') as file:
                        changed_files.append((fpath, file.read()))
    return changed_files


def kimi_review_code(standard, code_files, api_key, api_base=None):
    # Moonshot/kimi API endpoint
    if api_base is None:
        api_base = 'https://api.moonshot.cn/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    model = 'kimi-k2-0711-preview'
    feedbacks = []
    for fname, code in code_files:
        ext = os.path.splitext(fname)[1]
        prompt = f"""
你是一名资深代码审查专家，请根据如下代码标准对给定 {ext} 代码进行审核，指出不符合标准的地方并给出建议：

代码标准：
{standard}

待审核代码（文件名：{fname}）：
{code}

请用中文输出审核结果。
"""
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800
        }
        try:
            resp = requests.post(api_base, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            feedback = result['choices'][0]['message']['content']
        except Exception as e:
            feedback = f"{fname}: Kimi 审核失败 - {e}"
        feedbacks.append((fname, feedback))
    return feedbacks


def save_review_result(feedbacks, output_path='ai_review_result.md'):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# AI 代码审核结果\n\n')
        for fname, feedback in feedbacks:
            f.write(f'## 文件: {fname}\n')
            f.write(feedback.strip() + '\n\n')
    print(f'审核结果已保存到 {output_path}')


def upload_to_wiki(md_path, wiki_url, pat_token):
    pass


def main():
    config = load_config()
    parser = argparse.ArgumentParser(description='Kimi AI 自动代码 review 脚本')
    parser.add_argument('--code_path', required=False, help='待检查代码目录或文件（全量模式下使用）')
    parser.add_argument('--standards', default=config.get('standards', 'code_standards.docx'), help='代码标准文档')
    parser.add_argument('--moonshot_api_key', default=config.get('moonshot_api_key'), help='Moonshot/Kimi API Key')
    parser.add_argument('--moonshot_api_base', default=config.get('moonshot_api_base'), help='Moonshot API Base URL')
    parser.add_argument('--pr_only', action='store_true', default=config.get('pr_only', False), help='仅审查 PR/commit 变更代码')
    parser.add_argument('--output', default=config.get('output', 'ai_review_result.md'), help='审核结果输出路径')
    parser.add_argument('--wiki_url', default=config.get('wiki_url'), help='Azure DevOps Wiki 页面 API 地址')
    parser.add_argument('--wiki_pat', default=config.get('wiki_pat'), help='用于 Wiki 上传的 PAT Token')
    parser.add_argument('--code_types', nargs='*', default=config.get('code_types', SUPPORTED_EXTS), help='需要审核的代码文件扩展名列表')
    args = parser.parse_args()

    standard = load_standards(args.standards)
    code_types = args.code_types
    if args.pr_only:
        code_files = get_changed_files(pr_only=True, code_types=code_types)
    else:
        code_files = get_changed_files(pr_only=False, code_types=code_types)
    print(f'共需审核 {len(code_files)} 个文件...')
    feedbacks = kimi_review_code(standard, code_files, args.moonshot_api_key, args.moonshot_api_base)
    save_review_result(feedbacks, args.output)
    if args.wiki_url and args.wiki_pat:
        upload_to_wiki(args.output, args.wiki_url, args.wiki_pat)

if __name__ == "__main__":
    main() 