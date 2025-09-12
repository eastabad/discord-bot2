#!/usr/bin/env python3
"""
检查AI模型配置，特别是Google模型版本和role方式
"""
import json
import logging
from multi_ai_service import MultiAIService

def check_ai_models():
    """检查AI模型配置详情"""
    print("🔍 检查AI模型配置详情")
    print("=" * 60)
    
    try:
        # 初始化多AI服务
        ai_service = MultiAIService()
        
        print("📋 配置的AI模型列表:")
        print("-" * 40)
        
        for i, model in enumerate(ai_service.models, 1):
            status = "✅ 启用" if model.enabled else "❌ 禁用"
            print(f"{i}. {model.name}")
            print(f"   提供商: {model.provider}")
            print(f"   模型ID: {model.model_id}")
            print(f"   最大Token: {model.max_tokens}")
            print(f"   温度: {model.temperature}")
            print(f"   状态: {status}")
            print()
        
        # 重点检查Google模型
        google_models = [m for m in ai_service.models if m.provider == "google"]
        if google_models:
            print("🤖 Google模型详情:")
            print("-" * 40)
            for model in google_models:
                print(f"模型名称: {model.name}")
                print(f"实际使用的模型ID: {model.model_id}")
                print(f"是否为2.5版本: {'否' if '1.5' in model.model_id else '是'}")
                print(f"完整版本: {model.model_id}")
                
                # 检查实际版本
                if "gemini-1.5-pro" in model.model_id:
                    print("⚠️ 注意: 配置显示为'Gemini 2.5 Pro'但实际使用'gemini-1.5-pro'")
                elif "gemini-2.5" in model.model_id:
                    print("✅ 确认: 使用Gemini 2.5版本")
                else:
                    print(f"❓ 未知版本: {model.model_id}")
        
        # 检查API密钥状态
        print("\n🔑 API密钥状态:")
        print("-" * 40)
        api_keys = {
            "Gemini": ai_service.gemini_api_key,
            "OpenRouter": ai_service.openrouter_api_key,
            "Anthropic": ai_service.anthropic_api_key
        }
        
        for name, key in api_keys.items():
            status = "✅ 已配置" if key else "❌ 未配置"
            length = f"(长度: {len(key)})" if key else ""
            print(f"{name}: {status} {length}")
        
        return ai_service
        
    except Exception as e:
        print(f"❌ 检查AI模型配置失败: {e}")
        return None

def check_role_structure():
    """检查role方式和消息结构"""
    print("\n🎭 检查Role方式和消息结构")
    print("=" * 60)
    
    print("📝 Gemini消息结构:")
    print("-" * 30)
    print("Gemini使用简单的内容传递方式:")
    print("- 直接传递prompt字符串")
    print("- 不使用角色(role)系统")
    print("- 通过generation_config控制输出参数")
    print()
    print("示例代码结构:")
    print("```python")
    print("model = genai.GenerativeModel(model_id)")
    print("response = model.generate_content(")
    print("    prompt,  # 直接传递提示词字符串")
    print("    generation_config=genai.GenerationConfig(")
    print("        temperature=0.7,")
    print("        max_output_tokens=4096")
    print("    )")
    print(")")
    print("```")
    
    print("\n📝 对比其他模型的Role结构:")
    print("-" * 30)
    print("Claude/GPT-4使用消息列表:")
    print("```python")
    print("messages = [")
    print("    {'role': 'system', 'content': '系统提示'},")
    print("    {'role': 'user', 'content': '用户输入'}")
    print("]")
    print("```")
    
    print("\n🔄 在多AI服务中的处理:")
    print("-" * 30)
    print("- Gemini: 直接使用prompt字符串")
    print("- Claude/GPT: 自动转换为消息格式")
    print("- 统一接口处理不同的API结构")

def main():
    """主函数"""
    print("🧪 AI模型配置检查工具")
    print("=" * 70)
    
    # 检查模型配置
    ai_service = check_ai_models()
    
    # 检查role结构
    check_role_structure()
    
    if ai_service:
        print("\n📊 总结:")
        print("=" * 70)
        enabled_models = [m for m in ai_service.models if m.enabled]
        print(f"✅ 可用AI模型数量: {len(enabled_models)}")
        
        google_model = next((m for m in enabled_models if m.provider == "google"), None)
        if google_model:
            print(f"🤖 Google模型: {google_model.name} ({google_model.model_id})")
            
            # 明确版本信息
            if "1.5" in google_model.model_id:
                print("⚠️ 重要提示: 虽然名称显示'2.5 Pro'，但实际使用的是Gemini 1.5 Pro")
                print("   这是因为代码中配置的model_id是'gemini-1.5-pro'")
            
            print(f"🎭 Role方式: 不使用role系统，直接传递prompt字符串")
            print(f"⚙️ 配置参数: temperature={google_model.temperature}, max_tokens={google_model.max_tokens}")
        else:
            print("❌ Google模型未启用或不可用")
    
    print("\n💡 如需升级到真正的Gemini 2.5，需要:")
    print("1. 将model_id改为'gemini-2.5-pro'或'gemini-2.5-flash'")
    print("2. 确认API密钥支持2.5版本")
    print("3. 测试API兼容性")

if __name__ == "__main__":
    main()