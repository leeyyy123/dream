"""
测试智谱AI配置
运行此脚本检查API Key是否配置正确
"""

import os
import sys
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_config():
    """测试AI配置"""
    print("=" * 50)
    print("智谱AI配置测试")
    print("=" * 50)

    # 检查环境变量
    api_key = os.getenv('ZHIPU_API_KEY')
    print(f"\n1. 环境变量检查:")
    print(f"   ZHIPU_API_KEY: {'[OK] 已配置' if api_key else '[FAIL] 未配置'}")

    if api_key:
        # 只显示前8位和后4位
        masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
        print(f"   API Key内容: {masked_key}")
    else:
        print("\n[ERROR] ZHIPU_API_KEY 环境变量未设置!")
        print("\n请设置环境变量:")
        print("  Windows (CMD): set ZHIPU_API_KEY=你的API_Key")
        print("  Windows (PowerShell): $env:ZHIPU_API_KEY='你的API_Key'")
        print("  Linux/Mac: export ZHIPU_API_KEY=你的API_Key")
        return False

    # 尝试导入zhipuai
    print(f"\n2. 包导入检查:")
    try:
        from zhipuai import ZhipuAI
        print(f"   zhipuai包: [OK] 已安装")
    except ImportError as e:
        print(f"   zhipuai包: [FAIL] 导入失败 - {e}")
        print("\n请运行: pip install zhipuai")
        return False

    # 尝试初始化客户端
    print(f"\n3. 客户端初始化检查:")
    try:
        client = ZhipuAI(api_key=api_key)
        print(f"   客户端初始化: [OK] 成功")
    except Exception as e:
        print(f"   客户端初始化: [FAIL] 失败 - {e}")
        return False

    # 测试API调用
    print(f"\n4. API调用测试:")
    try:
        print("   正在发送测试请求...")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": "你好，请回复'测试成功'"}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"   API调用: [OK] 成功")
        print(f"   AI回复: {result}")

    except Exception as e:
        print(f"   API调用: [FAIL] 失败")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {e}")

        # 常见错误提示
        error_str = str(e).lower()
        if 'unauthorized' in error_str or '401' in error_str:
            print("\n[提示] API Key可能无效，请检查:")
            print("  1. API Key是否正确")
            print("  2. API Key是否已激活")
            print("  3. 账户是否有可用额度")
        elif 'timeout' in error_str or 'connection' in error_str:
            print("\n[提示] 网络连接问题，请检查:")
            print("  1. 网络连接是否正常")
            print("  2. 是否需要配置代理")
        return False

    print("\n" + "=" * 50)
    print("[OK] 所有测试通过！AI服务配置正常")
    print("=" * 50)
    return True


if __name__ == '__main__':
    success = test_ai_config()
    sys.exit(0 if success else 1)
