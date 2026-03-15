# -*- coding: utf-8 -*-
"""
股东结构模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, ShareholderStructure, Company
import pandas as pd
import io


@api_bp.route('/shareholder_structure', methods=['GET'])
def get_shareholder_structures():
    """获取股东结构数据列表"""
    company_id = request.args.get('company_id', type=int)
    shareholder_type = request.args.get('shareholder_type')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ShareholderStructure.query.join(Company)
    
    if company_id:
        query = query.filter(ShareholderStructure.company_id == company_id)
    
    if shareholder_type:
        query = query.filter(ShareholderStructure.shareholder_type == shareholder_type)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    pagination = query.order_by(ShareholderStructure.stat_date.desc(), Company.code).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@api_bp.route('/shareholder_structure', methods=['POST'])
def create_shareholder_structure():
    """新增股东结构记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('stat_date'):
        return jsonify({'code': 400, 'message': '公司ID和统计日期不能为空'}), 400
    
    existing = ShareholderStructure.query.filter_by(
        company_id=data['company_id'],
        stat_date=data['stat_date'],
        shareholder_type=data.get('shareholder_type', '')
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该日期该类型的记录已存在'}), 400
    
    record = ShareholderStructure(
        company_id=data['company_id'],
        stat_date=data['stat_date'],
        shareholder_type=data.get('shareholder_type', ''),
        holding_ratio=data.get('holding_ratio'),
        change_ratio=data.get('change_ratio')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/shareholder_structure/<int:id>', methods=['PUT'])
def update_shareholder_structure(id):
    """更新股东结构记录"""
    record = ShareholderStructure.query.get_or_404(id)
    data = request.get_json()
    
    if 'holding_ratio' in data:
        record.holding_ratio = data['holding_ratio']
    if 'change_ratio' in data:
        record.change_ratio = data['change_ratio']
    if 'shareholder_type' in data:
        record.shareholder_type = data['shareholder_type']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/shareholder_structure/<int:id>', methods=['DELETE'])
def delete_shareholder_structure(id):
    """删除股东结构记录"""
    record = ShareholderStructure.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/shareholder_structure/export', methods=['GET'])
def export_shareholder_structure():
    """导出 Excel 数据"""
    company_id = request.args.get('company_id', type=int)
    keyword = request.args.get('keyword', '')

    query = ShareholderStructure.query.join(Company)

    if company_id:
        query = query.filter(ShareholderStructure.company_id == company_id)
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )

    records = query.order_by(ShareholderStructure.stat_date.desc(), Company.code).all()

    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '统计日期': r.stat_date.strftime('%Y-%m-%d') if r.stat_date else '',
            '股东类型': r.shareholder_type,
            '持股比例 (%)': r.holding_ratio,
            '变动比例 (%)': r.change_ratio
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    from flask import send_file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='shareholder_structure_export.xlsx'
    )
