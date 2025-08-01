import sys
import os
import argparse
import subprocess
import yaml
import requests
import datetime

# this is for pipeline testing
def get_latest_result_file(result_dir='result'):
    files = [f for f in os.listdir(result_dir) if f.startswith('ai_review_result_') and f.endswith('.md')]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(result_dir, files[0])

SUPPORTED_EXTS = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.cpp', '.c', '.cs', '.vue', '.html', '.css', '.json', '.sh']


def load_config(config_path='config.yaml'):
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def load_standards(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_changed_files(pr_only, code_types=None):
    if code_types is None:
        code_types = SUPPORTED_EXTS
    changed_files = []
    if pr_only:
        # Azure DevOps 环境变量
        base = os.environ.get('SYSTEM_PULLREQUEST_TARGETBRANCH') or os.environ.get('BUILD_SOURCEBRANCHNAME')
        head = os.environ.get('SYSTEM_PULLREQUEST_SOURCEBRANCH') or os.environ.get('BUILD_SOURCEBRANCH')
        
        print(f"Debug: base={base}, head={head}")
        
        if base and head:
            # 清理分支名称
            base = base.replace('refs/heads/', '').replace('refs/pull/', '')
            head = head.replace('refs/heads/', '').replace('refs/pull/', '')
            
            # 尝试不同的 diff 命令
            diff_cmd = f'git diff --name-only origin/{base}...origin/{head}'
            print(f"Debug: 执行命令: {diff_cmd}")
            
            result = subprocess.run(diff_cmd, shell=True, capture_output=True, text=True)
            print(f"Debug: diff 命令输出: {result.stdout}")
            print(f"Debug: diff 命令错误: {result.stderr}")
            
            if result.returncode != 0:
                # 如果上面的命令失败，尝试其他方式
                diff_cmd = f'git diff --name-only {base}...{head}'
                print(f"Debug: 尝试备用命令: {diff_cmd}")
                result = subprocess.run(diff_cmd, shell=True, capture_output=True, text=True)
                print(f"Debug: 备用命令输出: {result.stdout}")
        else:
            # 如果没有 PR 信息，使用最近的提交
            diff_cmd = 'git diff --name-only HEAD~1'
            print(f"Debug: 使用最近提交: {diff_cmd}")
            result = subprocess.run(diff_cmd, shell=True, capture_output=True, text=True)
        
        files = [f for f in result.stdout.splitlines() if f.strip() and os.path.splitext(f)[1] in code_types]
        print(f"Debug: 找到的变更文件: {files}")
        
        for f in files:
            if os.path.exists(f):
                diff_content = subprocess.run(f'git diff {f}', shell=True, capture_output=True, text=True).stdout
                if not diff_content:
                    with open(f, 'r', encoding='utf-8') as file:
                        diff_content = file.read()
                changed_files.append((f, diff_content))
                print(f"Debug: 添加文件 {f} 到审核列表")
            else:
                print(f"Debug: 文件 {f} 不存在，跳过")
    else:
        for root, _, files in os.walk('.'):
            for f in files:
                if os.path.splitext(f)[1] in code_types:
                    fpath = os.path.join(root, f)
                    with open(fpath, 'r', encoding='utf-8') as file:
                        changed_files.append((fpath, file.read()))
    
    print(f"Debug: 总共找到 {len(changed_files)} 个文件需要审核")
    return changed_files


def kimi_review_code(standard, code_files, api_key, api_base=None):
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


def save_review_result(feedbacks, output_path=None):
    result_dir = 'result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    if output_path is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(result_dir, f'ai_review_result_{timestamp}.md')
    else:
        output_path = os.path.join(result_dir, output_path) if not output_path.startswith(result_dir) else output_path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# AI 代码审核结果\n\n')
        for fname, feedback in feedbacks:
            f.write(f'## 文件: {fname}\n')
            f.write(feedback.strip() + '\n\n')
    print(f'审核结果已保存到 {output_path}')
    return output_path


def main():
    print("=== AI 代码审核脚本开始 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"环境变量: PR_ONLY={os.environ.get('SYSTEM_PULLREQUEST_TARGETBRANCH')}")
    
    config = load_config()
    parser = argparse.ArgumentParser(description='Kimi AI 自动代码 review 脚本')
    parser.add_argument('--code_path', required=False, help='待检查代码目录或文件（全量模式下使用）')
    parser.add_argument('--standards', default=config.get('standards', 'code_standards.txt'), help='代码标准文档(txt)')
    parser.add_argument('--moonshot_api_key', default=config.get('moonshot_api_key'), help='Moonshot/Kimi API Key')
    parser.add_argument('--moonshot_api_base', default=config.get('moonshot_api_base'), help='Moonshot API Base URL')
    parser.add_argument('--pr_only', action='store_true', default=config.get('pr_only', False), help='仅审查 PR/commit 变更代码')
    parser.add_argument('--output', default=None, help='审核结果输出路径（如不指定则自动加时间戳）')
    parser.add_argument('--code_types', nargs='*', default=config.get('code_types', SUPPORTED_EXTS), help='需要审核的代码文件扩展名列表')
    args = parser.parse_args()

    print(f"参数: pr_only={args.pr_only}, standards={args.standards}")
    print(f"支持的代码类型: {args.code_types}")

    standard = load_standards(args.standards)
    print(f"代码标准长度: {len(standard)} 字符")
    
    code_types = args.code_types
    if args.pr_only:
        print("使用 PR 模式，只审核变更文件...")
        code_files = get_changed_files(pr_only=True, code_types=code_types)
    else:
        print("使用全量模式，审核所有文件...")
        code_files = get_changed_files(pr_only=False, code_types=code_types)
    
    print(f'共需审核 {len(code_files)} 个文件...')
    
    if len(code_files) == 0:
        print("没有找到需要审核的文件，创建空的审核结果...")
        feedbacks = [("无变更文件", "本次 PR 没有包含需要审核的代码文件。")]
    else:
        print("开始调用 Kimi API 进行审核...")
        feedbacks = kimi_review_code(standard, code_files, args.moonshot_api_key, args.moonshot_api_base)
    
    print(f"审核完成，共生成 {len(feedbacks)} 个反馈...")
    result_path = save_review_result(feedbacks, args.output)
    print(f"=== 审核脚本完成，结果保存到: {result_path} ===")

if __name__ == "__main__":
    main() 