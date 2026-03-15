# -*- coding: utf-8 -*-
"""
研发投入模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, RdExpense, Company
import pandas as pd
import io


@api_bp.route('/rd_expense', methods=['GET'])
def get_rd_expenses():
    """获取研发投入数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = RdExpense.query.join(Company)
    
    if company_id:
        query = query.filter(RdExpense.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(RdExpense.year >= year_from)
    if year_to:
        query = query.filter(RdExpense.year <= year_to)
    
    pagination = query.order_by(RdExpense.year.desc(), Company.code).paginate(
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


@api_bp.route('/rd_expense', methods=['POST'])
def create_rd_expense():
    """新增研发投入记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    existing = RdExpense.query.filter_by(
        company_id=data['company_id'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份的记录已存在'}), 400
    
    record = RdExpense(
        company_id=data['company_id'],
        year=data['year'],
        revenue=data.get('revenue'),
        rd_expense=data.get('rd_expense'),
        rd_ratio=data.get('rd_ratio'),
        rd_growth=data.get('rd_growth'),
        rd_return=data.get('rd_return')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/rd_expense/<int:id>', methods=['PUT'])
def update_rd_expense(id):
    """更新研发投入记录"""
    record = RdExpense.query.get_or_404(id)
    data = request.get_json()
    
    if 'revenue' in data:
        record.revenue = data['revenue']
    if 'rd_expense' in data:
        record.rd_expense = data['rd_expense']
    if 'rd_ratio' in data:
        record.rd_ratio = data['rd_ratio']
    if 'rd_growth' in data:
        record.rd_growth = data['rd_growth']
    if 'rd_return' in data:
        record.rd_return = data['rd_return']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/rd_expense/<int:id>', methods=['DELETE'])
def delete_rd_expense(id):
    """删除研发投入记录"""
    record = RdExpense.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/rd_expense/export', methods=['GET'])
def export_rd_expense():
    """导出 Excel 数据"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)

    query = RdExpense.query.join(Company)

    if company_id:
        query = query.filter(RdExpense.company_id == company_id)
    if year_from:
        query = query.filter(RdExpense.year >= year_from)
    if year_to:
        query = query.filter(RdExpense.year <= year_to)

    records = query.order_by(RdExpense.year.desc(), Company.code).all()

    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            '主营收入 (元)': r.revenue,
            '研发费用 (元)': r.rd_expense,
            '研发费用占比 (%)': r.rd_ratio,
            '费用增长率': r.rd_growth,
            '费用回报率': r.rd_return
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
        download_name='rd_expense_export.xlsx'
    )
