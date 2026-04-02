"""快速测试脚本"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query(question):
    """测试问答"""
    print(f"\n💬 Testing query: {question}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"question": question}
        )
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"Answer: {result.get('answer', 'No answer')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_documents():
    """测试文档列表"""
    print("\n📚 Testing documents list...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"Total documents: {result.get('total', 0)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("RAG Knowledge Assistant - Backend Test")
    print("=" * 50)
    print()
    
    # 测试健康检查
    if not test_health():
        print("\n⚠️  Please make sure the backend is running!")
        print("Run: python -m uvicorn app.main:app --reload")
        exit(1)
    
    # 测试文档列表
    test_documents()
    
    # 测试问答（没有文档时会提示）
    test_query("你好")
    
    print("\n" + "=" * 50)
    print("✅ Backend test completed!")
    print("=" * 50)
