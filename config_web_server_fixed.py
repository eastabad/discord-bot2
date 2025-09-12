#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from signal_config import SignalConfigManager, SignalMapping, AITemplate
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    """配置主页面"""
    return render_template('settings.html')

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
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
            
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
def update_signal_mapping(index: int):
    """更新信号映射"""
    try:
        # 加载现有映射
        with open(config_manager.signal_mappings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 更新数据
        update_data = request.get_json()
        if not update_data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
            
        data[index].update(update_data)
        data[index]['updated_at'] = datetime.now().isoformat()
        
        # 保存
        with open(config_manager.signal_mappings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '信号映射更新成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signal-mappings/<int:index>', methods=['DELETE'])
def delete_signal_mapping(index: int):
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
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
            
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
def update_ai_template(index: int):
    """更新AI模板"""
    try:
        # 加载现有模板
        with open(config_manager.ai_templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if index >= len(data):
            return jsonify({'success': False, 'error': '索引超出范围'}), 400
        
        # 更新数据
        update_data = request.get_json()
        if not update_data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
            
        data[index].update(update_data)
        data[index]['updated_at'] = datetime.now().isoformat()
        
        # 保存
        with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'AI模板更新成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai-templates/<int:index>', methods=['DELETE'])
def delete_ai_template(index: int):
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
        test_data = request.get_json()
        if not test_data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
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
        config_data = request.get_json()
        if not config_data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        # 导入信号映射
        if 'signal_mappings' in config_data and config_data['signal_mappings']:
            with open(config_manager.signal_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(config_data['signal_mappings'], f, ensure_ascii=False, indent=2)
        
        # 导入AI模板
        if 'ai_templates' in config_data and config_data['ai_templates']:
            with open(config_manager.ai_templates_file, 'w', encoding='utf-8') as f:
                json.dump(config_data['ai_templates'], f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '配置导入成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 确保模板目录存在
    os.makedirs('templates', exist_ok=True)
    
    # 开发模式运行
    app.run(host='0.0.0.0', port=8080, debug=True)