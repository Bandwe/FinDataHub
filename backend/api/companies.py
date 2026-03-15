# -*- coding: utf-8 -*-
"""
公司管理API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, Company


@api_bp.route('/companies', methods=['GET'])
def get_companies():
    """获取公司列表"""
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    query = Company.query
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    pagination = query.order_by(Company.code).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@api_bp.route('/companies', methods=['POST'])
def create_company():
    """新增公司"""
    data = request.get_json()
    
    # 校验必填字段
    if not data.get('name') or not data.get('code'):
        return jsonify({'code': 400, 'message': '个股名称和代码不能为空'}), 400
    
    # 检查代码是否已存在
    if Company.query.filter_by(code=data['code']).first():
        return jsonify({'code': 400, 'message': '代码已存在'}), 400
    
    company = Company(
        name=data['name'],
        code=data['code'],
        business=data.get('business', ''),
        remark=data.get('remark', '')
    )
    
    db.session.add(company)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': company.to_dict()
    })


@api_bp.route('/companies/<int:id>', methods=['PUT'])
def update_company(id):
    """更新公司信息"""
    company = Company.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        company.name = data['name']
    if 'code' in data:
        # 检查新代码是否与其他公司冲突
        existing = Company.query.filter_by(code=data['code']).first()
        if existing and existing.id != id:
            return jsonify({'code': 400, 'message': '代码已存在'}), 400
        company.code = data['code']
    if 'business' in data:
        company.business = data['business']
    if 'remark' in data:
        company.remark = data['remark']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': company.to_dict()
    })


@api_bp.route('/companies/<int:id>', methods=['DELETE'])
def delete_company(id):
    """删除公司"""
    company = Company.query.get_or_404(id)
    
    db.session.delete(company)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/companies/all', methods=['GET'])
def get_all_companies():
    """获取所有公司（用于下拉选择）"""
    companies = Company.query.order_by(Company.code).all()
    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in companies]
    })
