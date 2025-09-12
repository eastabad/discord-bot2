#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from signal_config import SignalConfigManager, SignalMapping, AITemplate
from dataclasses import asdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')

# 初始化配置管理器
config_manager = SignalConfigManager()

@app.route('/')
def index():
    """主页 - 重定向到配置页面"""
    return redirect(url_for('settings'))

@app.route('/setting')
@app.route('/settings')
def settings():
    """统一配置主页面"""
    return render_template('unified_config.html')

@app.route('/detailed')
def detailed_config_page():
    """详细配置管理页面"""
    return render_template('detailed_config.html')

@app.route('/simple-config')
def simple_config_page():
    """简化配置管理页面"""
    return render_template('simple_config.html')

@app.route('/parsing-config')
def parsing_config_page():
    """解析配置管理页面"""
    return render_template('parsing_config.html')

@app.route('/api/signal-mappings', methods=['GET'])
def get_signal_mappings():
    """获取所有信号映射"""
    try:
        with open(config_manager.signal_mappings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-mappings', methods=['POST'])
def add_signal_mapping():
    """添加新的信号映射"""
    try:
        data = request.get_json() or {}
        signal_type = data.get('signal_type')
        signal_value = data.get('signal_value')
        chinese_description = data.get('chinese_description')
        
        if not all([signal_type, signal_value, chinese_description]):
            return jsonify({'success': False, 'error': '所有字段都是必需的'}), 400
        
        config_manager.add_signal_mapping(signal_type, signal_value, chinese_description)
        return jsonify({'success': True, 'message': '信号映射添加成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-mappings/<int:index>', methods=['PUT'])
def update_signal_mapping(index):
    """更新信号映射"""
    try:
        # 加载现有映射
        with open(config_manager.signal_mappings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 更新数据
        update_data = request.json
        data[index].update(update_data)
        data[index]['updated_at'] = datetime.now().isoformat()
        
        # 保存
        with open(config_manager.signal_mappings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '信号映射更新成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-mappings/<int:index>', methods=['DELETE'])
def delete_signal_mapping(index):
    """删除信号映射"""
    try:
        # 加载现有映射
        with open(config_manager.signal_mappings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 删除数据
        deleted_item = data.pop(index)
        
        # 保存
        with open(config_manager.signal_mappings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': f'已删除信号映射: {deleted_item["signal_type"]}.{deleted_item["signal_value"]}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates', methods=['GET'])
def get_ai_templates():
    """获取所有AI模板"""
    try:
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates', methods=['POST'])
def add_ai_template():
    """添加新的AI模板"""
    try:
        data = request.json
        template_name = data.get('template_name')
        command_type = data.get('command_type')
        template_content = data.get('template_content')
        description = data.get('description', '')
        
        if not all([template_name, command_type, template_content]):
            return jsonify({'success': False, 'error': '模板名称、命令类型和模板内容都是必需的'}), 400
        
        # 加载现有模板
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        # 添加新模板
        new_template = {
            'template_name': template_name,
            'command_type': command_type,
            'template_content': template_content,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        templates.append(new_template)
        
        # 保存
        with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'AI模板添加成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates/<int:index>', methods=['PUT'])
def update_ai_template(index):
    """更新AI模板"""
    try:
        # 加载现有模板
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 更新数据
        update_data = request.json
        data[index].update(update_data)
        data[index]['updated_at'] = datetime.now().isoformat()
        
        # 保存
        with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'AI模板更新成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates/<int:index>', methods=['DELETE'])
def delete_ai_template(index):
    """删除AI模板"""
    try:
        # 加载现有模板
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 删除数据
        deleted_item = data.pop(index)
        
        # 保存
        with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': f'已删除AI模板: {deleted_item["template_name"]}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-translation', methods=['POST'])
def test_translation():
    """测试信号翻译"""
    try:
        test_data = request.json
        
        # 加载信号映射
        mappings = config_manager.load_signal_mappings()
        
        # 翻译结果
        results = {}
        for key, value in test_data.items():
            if key in mappings and value in mappings[key]:
                results[f"{key}_zh"] = mappings[key][value]
            else:
                results[f"{key}_zh"] = value  # 没找到映射就返回原值
        
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export-config', methods=['GET'])
def export_config():
    """导出配置"""
    try:
        # 读取信号映射
        with open(config_manager.signal_mappings_file, 'r', encoding='utf-8') as f:
            signal_mappings = json.load(f)
        
        # 读取AI模板
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            ai_templates = json.load(f)
        
        config_export = {
            'signal_mappings': signal_mappings,
            'ai_templates': ai_templates,
            'export_time': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        return jsonify(config_export)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/import-config', methods=['POST'])
def import_config():
    """导入配置"""
    try:
        config_data = request.json
        
        # 导入信号映射
        if 'signal_mappings' in config_data:
            with open(config_manager.signal_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(config_data['signal_mappings'], f, ensure_ascii=False, indent=2)
        
        # 导入AI模板
        if 'ai_templates' in config_data:
            with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
                json.dump(config_data['ai_templates'], f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '配置导入成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== 统一配置界面API端点 ===============

@app.route('/api/parsing-config', methods=['GET'])
def get_parsing_config():
    """获取解析引擎配置"""
    try:
        # 直接读取simple_field_texts.json文件
        with open('config/simple_field_texts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取字段配置
        config = data.get('fields', {})
        
        return jsonify({
            'success': True, 
            'config': config,
            'message': f'成功加载 {len(config)} 个字段配置'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/parsing-config', methods=['POST'])
def save_parsing_config():
    """保存解析引擎配置"""
    try:
        # 读取现有配置
        with open('config/simple_field_texts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取请求数据
        new_config = request.get_json() or {}
        
        # 更新配置
        fields_updated = 0
        for field_name, field_config in new_config.items():
            if 'outputs' in field_config and field_name in data.get('fields', {}):
                # 更新字段输出格式
                data['fields'][field_name]['outputs'] = field_config['outputs']
                fields_updated += 1
        
        # 更新时间戳
        data['updated_at'] = datetime.now().isoformat()
        
        # 保存到文件
        with open('config/simple_field_texts.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'成功保存 {fields_updated} 个字段配置'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-parsing', methods=['POST'])
def test_parsing_config():
    """测试解析配置"""
    try:
        from simple_config_engine import SimpleFieldConfig
        
        data = request.get_json() or {}
        test_data = data.get('test_data', {})
        
        # 创建配置引擎进行测试
        config_engine = SimpleFieldConfig()
        
        # 模拟解析测试 - 简单返回测试数据的格式化版本
        result = f"测试数据解析: {test_data}"
        
        return jsonify({
            'success': True,
            'result': str(result)[:200] + ('...' if len(str(result)) > 200 else ''),
            'message': '解析测试完成'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates-unified', methods=['GET'])
def get_ai_templates_unified():
    """获取AI模板配置（统一界面）"""
    try:
        from simple_ai_template import SimpleAITemplate
        ai_template = SimpleAITemplate()
        
        # 获取所有模板 - 使用正确的数据结构
        templates = {}
        template_mapping = {
            'chart_analysis': 'CT',
            'report_analysis': 'RP', 
            'image_analysis': 'IMG',
            'prediction_analysis': 'PRED'
        }
        
        for ui_key, template_key in template_mapping.items():
            template_info = ai_template.templates.get(template_key, {})
            templates[ui_key] = {
                'template': template_info.get('template', f'{template_key}模板暂未配置'),
                'name': template_info.get('name', f'{template_key}模板'),
                'description': template_info.get('description', '')
            }
        
        return jsonify({
            'success': True,
            'templates': templates,
            'message': f'成功加载 {len(templates)} 个模板'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates-unified', methods=['POST'])
def save_ai_template_unified():
    """保存AI模板（统一界面）"""
    try:
        from simple_ai_template import SimpleAITemplate
        ai_template = SimpleAITemplate()
        
        data = request.get_json() or {}
        template_type = data.get('template_type')
        template_content = data.get('template_content', '')
        
        if not template_type:
            return jsonify({'success': False, 'error': '模板类型不能为空'}), 400
        
        # 映射界面类型到实际模板键名
        template_mapping = {
            'chart_analysis': 'CT',
            'report_analysis': 'RP',
            'image_analysis': 'IMG', 
            'prediction_analysis': 'PRED'
        }
        
        actual_template_key = template_mapping.get(template_type)
        if not actual_template_key:
            return jsonify({'success': False, 'error': f'不支持的模板类型: {template_type}'}), 400
        
        # 更新模板内容
        if actual_template_key not in ai_template.templates:
            ai_template.templates[actual_template_key] = {}
        
        ai_template.templates[actual_template_key]['template'] = template_content
        ai_template.templates[actual_template_key]['name'] = f'{actual_template_key}模板'
        ai_template.templates[actual_template_key]['description'] = f'{template_type}的AI分析模板'
        
        # 保存到文件
        ai_template._save_templates(ai_template.templates)
        
        return jsonify({
            'success': True,
            'message': f'成功保存模板: {template_type}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============== Order Block Ticker路由管理API端点 ===============

@app.route('/api/orderblock-routes', methods=['GET'])
def get_orderblock_routes():
    """获取Order Block路由配置"""
    try:
        from orderblock_webhook import OrderBlockWebhookHandler
        
        # 创建模拟Bot对象
        class MockBot:
            pass
        
        handler = OrderBlockWebhookHandler(MockBot())
        routes = handler.get_all_ticker_mappings()
        
        # 转换为前端需要的格式
        route_data = []
        route_dict = {}
        
        # 按ticker分组
        for mapping in routes:
            ticker = mapping['ticker']
            channel_id = mapping['channel_id']
            
            if ticker not in route_dict:
                route_dict[ticker] = {
                    'ticker': ticker,
                    'channel_ids': [],
                    'channel_count': 0
                }
            
            route_dict[ticker]['channel_ids'].append(channel_id)
            route_dict[ticker]['channel_count'] += 1
        
        route_data = list(route_dict.values())
        
        return jsonify({
            'success': True,
            'data': route_data,
            'message': f'成功加载 {len(route_data)} 个路由配置'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orderblock-routes', methods=['POST'])
def add_orderblock_route():
    """添加Order Block路由"""
    try:
        from orderblock_webhook import OrderBlockWebhookHandler
        import re
        
        data = request.get_json() or {}
        ticker = data.get('ticker', '').strip()
        channel_ids_input = data.get('channel_ids', '').strip()
        description = data.get('description', '').strip()
        
        if not ticker:
            return jsonify({'success': False, 'error': 'Ticker不能为空'}), 400
        
        if not channel_ids_input:
            return jsonify({'success': False, 'error': '频道ID不能为空'}), 400
        
        # 解析频道ID列表 - 支持逗号、空格、换行分隔
        channel_ids = []
        for part in re.split(r'[,\s\n]+', channel_ids_input):
            part = part.strip()
            if part and part.isdigit():
                channel_ids.append(int(part))
        
        if not channel_ids:
            return jsonify({'success': False, 'error': '没有找到有效的频道ID'}), 400
        
        # 创建模拟Bot对象
        class MockBot:
            pass
        
        handler = OrderBlockWebhookHandler(MockBot())
        
        # 先删除该ticker的所有现有映射
        handler.remove_ticker_mappings(ticker)
        
        # 添加新的映射
        success_count = 0
        for channel_id in channel_ids:
            if handler.add_ticker_channel_mapping(ticker, channel_id, description):
                success_count += 1
        
        if success_count > 0:
            return jsonify({
                'success': True,
                'message': f'成功添加 {ticker} 到 {success_count} 个频道的路由配置'
            })
        else:
            return jsonify({'success': False, 'error': '添加路由失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orderblock-routes/<path:ticker>', methods=['DELETE'])
def delete_orderblock_route(ticker):
    """删除Order Block路由"""
    try:
        from orderblock_webhook import OrderBlockWebhookHandler
        
        # 创建模拟Bot对象
        class MockBot:
            pass
        
        handler = OrderBlockWebhookHandler(MockBot())
        success = handler.remove_ticker_mappings(ticker)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'成功删除 {ticker} 的路由配置'
            })
        else:
            return jsonify({'success': False, 'error': '删除路由失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-orderblock-webhook', methods=['POST'])
def test_orderblock_webhook():
    """测试Order Block webhook"""
    try:
        import requests
        
        data = request.get_json() or {}
        ticker = data.get('ticker', 'NASDAQ:TSLA')
        event = data.get('event', 'New Bullish OB Formed')
        
        # 构造测试数据
        test_data = {
            'ticker': ticker,
            'timeframe': '15m',
            'event': event,
            'price': '345.22',
            'bullish_ob': '345.22 - 344.55' if 'Bullish' in event else 'N/A',
            'bearish_ob': '346.10 - 345.80' if 'Bearish' in event else 'N/A'
        }
        
        # 发送到本地Order Block webhook
        response = requests.post('http://localhost:5000/webhook/orderblock', json=test_data, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': f'测试信号发送成功: {ticker} - {event}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'测试失败: HTTP {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 确保模板目录存在
    os.makedirs('templates', exist_ok=True)
    
    # 开发模式运行
    app.run(host='0.0.0.0', port=8080, debug=True)

