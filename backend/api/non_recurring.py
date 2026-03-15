# -*- coding: utf-8 -*-
"""
扣非净利润增长模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, NonRecurring, Company
import pandas as pd
import io


def build_query(model, query, keyword=None, company_id=None, year_from=None, year_to=None):
    """构建通用查询"""
    query = query.join(Company)
    
    if company_id:
        query = query.filter(model.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(model.year >= year_from)
    if year_to:
        query = query.filter(model.year <= year_to)
    
    return query


@api_bp.route('/non_recurring', methods=['GET'])
def get_non_recurrings():
    """获取扣非净利润数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = build_query(NonRecurring, NonRecurring.query, keyword, company_id, year_from, year_to)
    
    pagination = query.order_by(NonRecurring.year.desc(), Company.code).paginate(
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


@api_bp.route('/non_recurring', methods=['POST'])
def create_non_recurring():
    """新增扣非净利润记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    existing = NonRecurring.query.filter_by(
        company_id=data['company_id'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份的记录已存在'}), 400
    
    record = NonRecurring(
        company_id=data['company_id'],
        year=data['year'],
        non_recurring_profit=data.get('non_recurring_profit'),
        non_recurring_growth=data.get('non_recurring_growth')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/non_recurring/<int:id>', methods=['PUT'])
def update_non_recurring(id):
    """更新扣非净利润记录"""
    record = NonRecurring.query.get_or_404(id)
    data = request.get_json()
    
    if 'non_recurring_profit' in data:
        record.non_recurring_profit = data['non_recurring_profit']
    if 'non_recurring_growth' in data:
        record.non_recurring_growth = data['non_recurring_growth']
    if 'year' in data:
        record.year = data['year']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/non_recurring/<int:id>', methods=['DELETE'])
def delete_non_recurring(id):
    """删除扣非净利润记录"""
    record = NonRecurring.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/non_recurring/export', methods=['GET'])
def export_non_recurring():
    """导出Excel数据"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    
    query = build_query(NonRecurring, NonRecurring.query, None, company_id, year_from, year_to)
    records = query.order_by(NonRecurring.year.desc(), Company.code).all()
    
    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            '扣非净利润(亿元)': r.non_recurring_profit,
            '扣非增长率': r.non_recurring_growth
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
        download_name='non_recurring_export.xlsx'
    )
