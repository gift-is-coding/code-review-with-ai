#!/usr/bin/env python3
"""
测试 Azure DevOps Wiki 连接
"""

import requests
import base64
import json

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
        
        test_page_url = f"{test_url}&path=/TestPage"
        print(f"测试页面 URL: {test_page_url}")
        
        resp = requests.put(test_page_url, headers=headers, json=test_data, timeout=30)
        print(f"状态码: {resp.status_code}")
        print(f"响应: {resp.text[:500]}...")
        
        if resp.status_code in [200, 201]:
            print("✅ PUT 请求成功")
        else:
            print("❌ PUT 请求失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 使用你提供的凭据
    wiki_url = "https://dev.azure.com/giiift/test-for-HLS/_wiki/wikis/test-for-HLS.wiki/"
    pat_token = ""
    
    test_wiki_connection(wiki_url, pat_token) 