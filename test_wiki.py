#!/usr/bin/env python3
"""
测试 Azure DevOps Wiki 连接
"""

import requests
import base64
import json
import yaml
import os

def load_config(config_path='config.yaml'):
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        print(f"⚠️ 配置文件 {config_path} 不存在")
        return {}

def test_wiki_connection(wiki_url_base, pat_token):
    """测试 Wiki 连接"""
    print("=== 测试 Azure DevOps Wiki 连接 ===")
    
    # 处理 URL 格式
    if '_wiki/wikis/' in wiki_url_base:
        wiki_url_base = wiki_url_base.replace('_wiki/wikis/', '_apis/wiki/wikis/')
    
    if not wiki_url_base.endswith('/pages'):
        wiki_url_base = wiki_url_base.rstrip('/') + '/pages'
    
    # 构建测试 URL
    test_url = f"{wiki_url_base}?api-version=6.0"
    
    print(f"测试 URL: {test_url}")
    print(f"PAT Token 长度: {len(pat_token)}")
    
    # 构建认证头
    headers = {
        'Content-Type': 'application/json',
    }
    
    if not pat_token.startswith('Basic '):
        pat_b64 = base64.b64encode(f':{pat_token}'.encode('utf-8')).decode('utf-8')
        headers['Authorization'] = f'Basic {pat_b64}'
    else:
        headers['Authorization'] = pat_token
    
    print(f"认证头: {headers['Authorization'][:20]}...")
    
    try:
        # 测试 GET 请求（列出页面）
        print("\n1. 测试 GET 请求（列出页面）...")
        resp = requests.get(test_url, headers=headers, timeout=30)
        print(f"状态码: {resp.status_code}")
        print(f"响应: {resp.text[:500]}...")
        
        if resp.status_code == 200:
            print("✅ GET 请求成功")
            
            # 尝试解析响应
            try:
                data = resp.json()
                print(f"页面数量: {len(data.get('value', []))}")
            except:
                print("无法解析 JSON 响应")
        else:
            print("❌ GET 请求失败")
        
        # 测试 PUT 请求（创建测试页面）
        print("\n2. 测试 PUT 请求（创建测试页面）...")
        test_content = "# 测试页面\n\n这是一个测试页面，用于验证 Wiki API 连接。"
        
        test_data = {
            "content": test_content,
            "contentType": "markdown"
        }
        
        # 使用时间戳创建唯一的测试页面名
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        test_page_name = f"/TestPage_{timestamp}"
        test_page_url = f"{test_url}&path={test_page_name}"
        print(f"测试页面 URL: {test_page_url}")
        
        resp = requests.put(test_page_url, headers=headers, json=test_data, timeout=30)
        print(f"状态码: {resp.status_code}")
        print(f"响应: {resp.text[:500]}...")
        
        if resp.status_code in [200, 201]:
            print("✅ PUT 请求成功")
            print(f"✅ 测试页面创建成功: {test_page_name}")
        else:
            print("❌ PUT 请求失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 从配置文件读取凭据
    config = load_config()
    wiki_url = config.get('wiki_url_base')
    pat_token = config.get('wiki_pat')
    
    if not wiki_url or not pat_token:
        print("❌ 请在 config.yaml 中配置 wiki_url_base 和 wiki_pat")
        print("示例配置:")
        print("wiki_url_base: https://dev.azure.com/your-org/your-project/_wiki/wikis/your-wiki.wiki/")
        print("wiki_pat: your-pat-token")
        exit(1)
    
    # 检查是否是 Pipeline 变量格式
    if wiki_url.startswith('${') or pat_token.startswith('${'):
        print("❌ 检测到 Pipeline 变量格式，请使用实际的 URL 和 Token 进行本地测试")
        print("当前配置:")
        print(f"  wiki_url_base: {wiki_url}")
        print(f"  wiki_pat: {pat_token[:10]}..." if len(pat_token) > 10 else f"  wiki_pat: {pat_token}")
        print("\n请修改 config.yaml 为实际值:")
        print("wiki_url_base: https://dev.azure.com/giiift/test-for-HLS/_wiki/wikis/test-for-HLS.wiki/")
        print("wiki_pat: your-actual-pat-token")
        exit(1)
    
    test_wiki_connection(wiki_url, pat_token) 