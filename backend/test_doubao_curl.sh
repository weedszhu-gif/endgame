#!/bin/bash

# 豆包API测试脚本

API_KEY="83e2399c-d79e-4c97-8307-2b1e9018ddc8"
MODEL="doubao-seed-1-6-251015"

# 测试1：简单文本请求
echo "=== 测试1：简单文本请求 ==="
curl "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{ 
    "model": "'$MODEL'", 
    "messages": [ 
        { 
            "content": [ 
                { 
                    "text": "如何解方程 2x + 3 = 7？", 
                    "type": "text" 
                } 
            ], 
            "role": "user" 
        } 
    ] 
}'

echo -e "\n\n=== 测试2：苏格拉底式提问 ==="
curl "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{ 
    "model": "'$MODEL'", 
    "messages": [ 
        { 
            "content": [ 
                { 
                    "text": "我用配方法解方程 x² + 4x + 3 = 0", 
                    "type": "text" 
                } 
            ], 
            "role": "user" 
        } 
    ] 
}'

echo -e "\n\n=== 测试结果 ==="
echo "如果API调用成功，你将看到JSON格式的响应"
echo "如果出现 'Invalid API-key provided' 错误，说明API密钥不正确或已过期"
echo "如果出现其他错误，请检查网络连接和模型名称"
