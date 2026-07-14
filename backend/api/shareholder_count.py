# -*- coding: utf-8 -*-
"""
股东户数模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from datetime import datetime, date
from . import api_bp
from models import db, ShareholderCount, Company
import io


def parse_stat_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


@api_bp.route('/shareholder_count', methods=['GET'])
def get_shareholder_counts():
    """获取股东户数数据列表"""
    company_id = request.args.get('company_id', type=int)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ShareholderCount.query.join(Company)
    
    if company_id:
        query = query.filter(ShareholderCount.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    pagination = query.order_by(ShareholderCount.stat_date.desc(), Company.code).paginate(
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


@api_bp.route('/shareholder_count', methods=['POST'])
def create_shareholder_count():
    """新增股东户数记录"""
    data = request.get_json()
    stat_date = parse_stat_date(data.get('stat_date'))
    
    if not data.get('company_id') or not stat_date:
        return jsonify({'code': 400, 'message': '公司ID和统计日期不能为空'}), 400
    
    existing = ShareholderCount.query.filter_by(
        company_id=data['company_id'],
        stat_date=stat_date
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该日期的记录已存在'}), 400
    
    record = ShareholderCount(
        company_id=data['company_id'],
        stat_date=stat_date,
        total_holders=data.get('total_holders'),
        change=data.get('change')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/shareholder_count/<int:id>', methods=['PUT'])
def update_shareholder_count(id):
    """更新股东户数记录"""
    record = ShareholderCount.query.get_or_404(id)
    data = request.get_json()
    
    if 'total_holders' in data:
        record.total_holders = data['total_holders']
    if 'change' in data:
        record.change = data['change']
    if 'stat_date' in data:
        stat_date = parse_stat_date(data.get('stat_date'))
        if not stat_date:
            return jsonify({'code': 400, 'message': '统计日期格式不正确'}), 400
        record.stat_date = stat_date
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/shareholder_count/<int:id>', methods=['DELETE'])
def delete_shareholder_count(id):
    """删除股东户数记录"""
    record = ShareholderCount.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/shareholder_count/export', methods=['GET'])
def export_shareholder_count():
    """导出 Excel 数据"""
    import pandas as pd

    company_id = request.args.get('company_id', type=int)
    keyword = request.args.get('keyword', '')

    query = ShareholderCount.query.join(Company)

    if company_id:
        query = query.filter(ShareholderCount.company_id == company_id)
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )

    records = query.order_by(ShareholderCount.stat_date.desc(), Company.code).all()

    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '统计日期': r.stat_date.strftime('%Y-%m-%d') if r.stat_date else '',
            '股东总人数': r.total_holders,
            '较上期变化': r.change
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
        download_name='shareholder_count_export.xlsx'
    )
