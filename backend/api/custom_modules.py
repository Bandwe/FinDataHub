# -*- coding: utf-8 -*-
"""
自定义模块管理API
"""
from flask import request, jsonify, g
from . import api_bp
from models import db, CustomModule, ModuleKeyword
from functools import wraps


# 简单的权限控制装饰器（演示用途）
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 这里可以实现实际的权限验证逻辑
        # 例如：检查session中的用户角色、token验证等
        # 目前仅作为演示，允许所有请求通过
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/custom-modules', methods=['GET'])
def get_custom_modules():
    """获取所有自定义模块列表"""
    try:
        modules = CustomModule.query.filter_by(is_active=True).order_by(CustomModule.sort_order.asc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [m.to_dict() for m in modules]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/all', methods=['GET'])
def get_all_modules():
    """获取所有模块（包括禁用的）- 用于管理"""
    try:
        modules = CustomModule.query.order_by(CustomModule.sort_order.asc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [m.to_dict() for m in modules]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>', methods=['GET'])
def get_custom_module(module_id):
    """获取单个模块详情"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': module.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@api_bp.route('/custom-modules', methods=['POST'])
@admin_required
def create_custom_module():
    """创建自定义模块"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name') or not data.get('code'):
            return jsonify({'code': 400, 'message': '模块名称和代码不能为空'}), 400
        
        # 检查代码是否已存在
        existing = CustomModule.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({'code': 400, 'message': '模块代码已存在'}), 400
        
        # 创建模块
        module = CustomModule(
            name=data['name'],
            code=data['code'],
            icon=data.get('icon', 'Grid'),
            description=data.get('description', ''),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True),
            created_by=data.get('created_by', 'admin')
        )
        
        db.session.add(module)
        db.session.flush()  # 获取module.id
        
        # 创建默认关键词
        default_keywords = [
            {'keyword': 'code', 'label': '代码', 'data_type': 'string', 'is_required': True},
            {'keyword': 'name', 'label': '个股名称', 'data_type': 'string', 'is_required': True},
            {'keyword': 'year', 'label': '年份', 'data_type': 'number', 'is_required': True}
        ]
        
        for idx, kw in enumerate(default_keywords):
            keyword = ModuleKeyword(
                module_id=module.id,
                keyword=kw['keyword'],
                label=kw['label'],
                data_type=kw['data_type'],
                is_required=kw['is_required'],
                sort_order=idx
            )
            db.session.add(keyword)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': module.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>', methods=['PUT'])
@admin_required
def update_custom_module(module_id):
    """更新自定义模块"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        data = request.get_json()
        
        # 如果修改了code，检查是否与其他模块冲突
        if data.get('code') and data['code'] != module.code:
            existing = CustomModule.query.filter_by(code=data['code']).first()
            if existing:
                return jsonify({'code': 400, 'message': '模块代码已存在'}), 400
            module.code = data['code']
        
        if 'name' in data:
            module.name = data['name']
        if 'icon' in data:
            module.icon = data['icon']
        if 'description' in data:
            module.description = data['description']
        if 'sort_order' in data:
            module.sort_order = data['sort_order']
        if 'is_active' in data:
            module.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': module.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>', methods=['DELETE'])
@admin_required
def delete_custom_module(module_id):
    """删除自定义模块"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        db.session.delete(module)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


# ============ 关键词管理接口 ============

@api_bp.route('/custom-modules/<int:module_id>/keywords', methods=['GET'])
def get_module_keywords(module_id):
    """获取模块的所有关键词"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        keywords = ModuleKeyword.query.filter_by(module_id=module_id).order_by(ModuleKeyword.sort_order.asc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [k.to_dict() for k in keywords]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>/keywords', methods=['POST'])
@admin_required
def create_module_keyword(module_id):
    """为模块添加关键词"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        data = request.get_json()
        
        if not data.get('keyword'):
            return jsonify({'code': 400, 'message': '关键词不能为空'}), 400
        
        # 检查关键词是否已存在
        existing = ModuleKeyword.query.filter_by(module_id=module_id, keyword=data['keyword']).first()
        if existing:
            return jsonify({'code': 400, 'message': '该关键词已存在'}), 400
        
        keyword = ModuleKeyword(
            module_id=module_id,
            keyword=data['keyword'],
            label=data.get('label', data['keyword']),
            data_type=data.get('data_type', 'string'),
            is_required=data.get('is_required', False),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(keyword)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': keyword.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'添加失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>/keywords/<int:keyword_id>', methods=['PUT'])
@admin_required
def update_module_keyword(module_id, keyword_id):
    """更新关键词"""
    try:
        keyword = ModuleKeyword.query.filter_by(id=keyword_id, module_id=module_id).first()
        if not keyword:
            return jsonify({'code': 404, 'message': '关键词不存在'}), 404
        
        data = request.get_json()
        
        # 如果修改了keyword，检查是否与其他关键词冲突
        if data.get('keyword') and data['keyword'] != keyword.keyword:
            existing = ModuleKeyword.query.filter_by(module_id=module_id, keyword=data['keyword']).first()
            if existing:
                return jsonify({'code': 400, 'message': '该关键词已存在'}), 400
            keyword.keyword = data['keyword']
        
        if 'label' in data:
            keyword.label = data['label']
        if 'data_type' in data:
            keyword.data_type = data['data_type']
        if 'is_required' in data:
            keyword.is_required = data['is_required']
        if 'sort_order' in data:
            keyword.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': keyword.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>/keywords/<int:keyword_id>', methods=['DELETE'])
@admin_required
def delete_module_keyword(module_id, keyword_id):
    """删除关键词"""
    try:
        keyword = ModuleKeyword.query.filter_by(id=keyword_id, module_id=module_id).first()
        if not keyword:
            return jsonify({'code': 404, 'message': '关键词不存在'}), 404
        
        db.session.delete(keyword)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@api_bp.route('/custom-modules/<int:module_id>/keywords/batch', methods=['POST'])
@admin_required
def batch_update_keywords(module_id):
    """批量更新关键词（用于排序和批量修改）"""
    try:
        module = CustomModule.query.get(module_id)
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        data = request.get_json()
        keywords_data = data.get('keywords', [])
        
        # 删除现有的关键词
        ModuleKeyword.query.filter_by(module_id=module_id).delete()
        
        # 创建新的关键词
        for idx, kw_data in enumerate(keywords_data):
            keyword = ModuleKeyword(
                module_id=module_id,
                keyword=kw_data['keyword'],
                label=kw_data.get('label', kw_data['keyword']),
                data_type=kw_data.get('data_type', 'string'),
                is_required=kw_data.get('is_required', False),
                sort_order=kw_data.get('sort_order', idx)
            )
            db.session.add(keyword)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '批量更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'批量更新失败: {str(e)}'}), 500