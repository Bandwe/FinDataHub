# -*- coding: utf-8 -*-
"""
PE估值模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, PeValuation, Company
import pandas as pd
import io


@api_bp.route('/pe_valuation', methods=['GET'])
def get_pe_valuations():
    """获取PE估值数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    type_filter = request.args.get('type')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = PeValuation.query.join(Company)
    
    if company_id:
        query = query.filter(PeValuation.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(PeValuation.year >= year_from)
    if year_to:
        query = query.filter(PeValuation.year <= year_to)
    
    if type_filter:
        query = query.filter(PeValuation.type == type_filter)
    
    pagination = query.order_by(PeValuation.year.desc(), Company.code).paginate(
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


@api_bp.route('/pe_valuation', methods=['POST'])
def create_pe_valuation():
    """新增PE估值记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    existing = PeValuation.query.filter_by(
        company_id=data['company_id'],
        year=data['year'],
        type=data.get('type', 'actual')
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份该类型的记录已存在'}), 400
    
    record = PeValuation(
        company_id=data['company_id'],
        year=data['year'],
        pe_high=data.get('pe_high'),
        pe_mid=data.get('pe_mid'),
        pe_low=data.get('pe_low'),
        eps=data.get('eps'),
        type=data.get('type', 'actual'),
        remark=data.get('remark', '')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/pe_valuation/<int:id>', methods=['PUT'])
def update_pe_valuation(id):
    """更新PE估值记录"""
    record = PeValuation.query.get_or_404(id)
    data = request.get_json()
    
    if 'pe_high' in data:
        record.pe_high = data['pe_high']
    if 'pe_mid' in data:
        record.pe_mid = data['pe_mid']
    if 'pe_low' in data:
        record.pe_low = data['pe_low']
    if 'eps' in data:
        record.eps = data['eps']
    if 'remark' in data:
        record.remark = data['remark']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/pe_valuation/<int:id>', methods=['DELETE'])
def delete_pe_valuation(id):
    """删除PE估值记录"""
    record = PeValuation.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/pe_valuation/export', methods=['GET'])
def export_pe_valuation():
    """导出 Excel 数据"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    type_filter = request.args.get('type')

    query = PeValuation.query.join(Company)

    if company_id:
        query = query.filter(PeValuation.company_id == company_id)
    if year_from:
        query = query.filter(PeValuation.year >= year_from)
    if year_to:
        query = query.filter(PeValuation.year <= year_to)
    if type_filter:
        query = query.filter(PeValuation.type == type_filter)

    records = query.order_by(PeValuation.year.desc(), Company.code).all()

    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            '类型': r.type,
            'PE 最高值': r.pe_high,
            'PE 中间值': r.pe_mid,
            'PE 最低值': r.pe_low,
            '每股收益': r.eps,
            '备注': r.remark
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
        download_name='pe_valuation_export.xlsx'
    )
