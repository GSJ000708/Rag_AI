"""验证智谱 API Key"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

api_key = os.getenv("ZHIPU_API_KEY")

print("=" * 60)
print("智谱 API Key 验证")
print("=" * 60)

if not api_key:
    print("❌ 错误: 未找到 ZHIPU_API_KEY 环境变量")
    print("\n请检查:")
    print("1. .env 文件是否存在")
    print("2. .env 文件中是否有 ZHIPU_API_KEY=xxx")
    exit(1)

if api_key == "your_zhipu_api_key_here":
    print("❌ 错误: API Key 未配置")
    print("\n请在 .env 文件中将 ZHIPU_API_KEY 设置为你的实际 API Key")
    print("\n获取方式:")
    print("1. 访问 https://open.bigmodel.cn/")
    print("2. 登录/注册")
    print("3. 进入控制台 → API Keys")
    print("4. 创建新的 API Key")
    exit(1)

print(f"✅ API Key 已配置")
print(f"   前10个字符: {api_key[:10]}...")
print(f"   长度: {len(api_key)} 字符")

# 测试 API 调用
print("\n正在测试 API 连接...")
try:
    from zhipuai import ZhipuAI
    
    client = ZhipuAI(api_key=api_key)
    
    # 测试 Embedding
    print("\n测试 Embedding API...")
    response = client.embeddings.create(
        model="embedding-3",
        input="测试文本"
    )
    print(f"✅ Embedding API 正常")
    print(f"   向量维度: {len(response.data[0].embedding)}")
    
    # 测试 LLM
    print("\n测试 LLM API...")
    response = client.chat.completions.create(
        model="glm-4-air",
        messages=[{"role": "user", "content": "你好"}],
    )
    print(f"✅ LLM API 正常")
    print(f"   响应: {response.choices[0].message.content[:50]}...")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！API Key 配置正确！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ API 调用失败: {e}")
    print("\n可能的原因:")
    print("1. API Key 格式错误")
    print("2. API Key 已过期或无效")
    print("3. 账户余额不足")
    print("4. 网络连接问题")
    print("\n请检查你的 API Key 是否正确")
    exit(1)
