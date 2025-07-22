import sys
import os
import argparse
from docx import Document
import re


def load_standards(docx_path):
    doc = Document(docx_path)
    rules = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            rules.append(text)
    return rules


def check_code_file(filepath, rules):
    feedback = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 1. 每行代码不超过 120 个字符。
    for idx, line in enumerate(lines):
        if len(line.rstrip('\n')) > 120:
            feedback.append(f"{filepath}: 第{idx+1}行超过120字符")
    # 2. 变量名应使用小写字母和下划线（snake_case）。
    snake_case_pattern = re.compile(r'\b([a-z]+(_[a-z0-9]+)*)\b')
    for idx, line in enumerate(lines):
        assign_match = re.findall(r'(\w+)\s*=.*', line)
        for var in assign_match:
            if not snake_case_pattern.fullmatch(var) and not var.isupper():
                feedback.append(f"{filepath}: 第{idx+1}行变量名 '{var}' 不符合snake_case")
    # 3. 函数应有 docstring 注释。
    for idx, line in enumerate(lines):
        if line.strip().startswith('def '):
            next_idx = idx + 1
            while next_idx < len(lines) and lines[next_idx].strip() == '':
                next_idx += 1
            if next_idx >= len(lines) or not (lines[next_idx].strip().startswith('"""') or lines[next_idx].strip().startswith("''")):
                feedback.append(f"{filepath}: 第{idx+1}行函数缺少 docstring 注释")
    # 4. 禁止使用 print 进行日志输出，推荐 logging。
    for idx, line in enumerate(lines):
        if 'print(' in line:
            feedback.append(f"{filepath}: 第{idx+1}行使用了 print，推荐使用 logging")
    # 5. 文件必须以空行结尾。
    if lines and lines[-1].strip() != '':
        feedback.append(f"{filepath}: 文件未以空行结尾")
    return feedback


def iter_code_files(code_path):
    code_files = []
    if os.path.isfile(code_path) and code_path.endswith('.py'):
        code_files.append(code_path)
    else:
        for root, _, files in os.walk(code_path):
            for f in files:
                if f.endswith('.py'):
                    code_files.append(os.path.join(root, f))
    return code_files


def main():
    parser = argparse.ArgumentParser(description='自动代码 review 脚本')
    parser.add_argument('--code_path', required=True, help='待检查代码目录或文件')
    parser.add_argument('--standards', default='code_standards.docx', help='代码标准文档')
    args = parser.parse_args()

    rules = load_standards(args.standards)
    print('加载的代码标准:')
    for rule in rules:
        print(' -', rule)
    print('\n开始检查代码...')
    code_files = iter_code_files(args.code_path)
    all_feedback = []
    for f in code_files:
        feedback = check_code_file(f, rules)
        all_feedback.extend(feedback)
    if all_feedback:
        print('\n发现以下不符合代码标准的问题:')
        for fb in all_feedback:
            print(fb)
        sys.exit(1)
    else:
        print('所有代码均符合标准！')

if __name__ == "__main__":
    main() 