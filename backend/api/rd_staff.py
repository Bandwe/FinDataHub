# -*- coding: utf-8 -*-
"""
研发人员模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, RdStaff, Company
import pandas as pd
import io


@api_bp.route('/rd_staff', methods=['GET'])
def get_rd_staffs():
    """获取研发人员数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = RdStaff.query.join(Company)
    
    if company_id:
        query = query.filter(RdStaff.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(RdStaff.year >= year_from)
    if year_to:
        query = query.filter(RdStaff.year <= year_to)
    
    pagination = query.order_by(RdStaff.year.desc(), Company.code).paginate(
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


@api_bp.route('/rd_staff', methods=['POST'])
def create_rd_staff():
    """新增研发人员记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    existing = RdStaff.query.filter_by(
        company_id=data['company_id'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份的记录已存在'}), 400
    
    record = RdStaff(
        company_id=data['company_id'],
        year=data['year'],
        staff_count=data.get('staff_count'),
        growth=data.get('growth'),
        percent_of_total=data.get('percent_of_total'),
        bachelor=data.get('bachelor'),
        master=data.get('master'),
        bachelor_master_ratio=data.get('bachelor_master_ratio'),
        remark=data.get('remark', '')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/rd_staff/<int:id>', methods=['PUT'])
def update_rd_staff(id):
    """更新研发人员记录"""
    record = RdStaff.query.get_or_404(id)
    data = request.get_json()
    
    if 'staff_count' in data:
        record.staff_count = data['staff_count']
    if 'growth' in data:
        record.growth = data['growth']
    if 'percent_of_total' in data:
        record.percent_of_total = data['percent_of_total']
    if 'bachelor' in data:
        record.bachelor = data['bachelor']
    if 'master' in data:
        record.master = data['master']
    if 'bachelor_master_ratio' in data:
        record.bachelor_master_ratio = data['bachelor_master_ratio']
    if 'remark' in data:
        record.remark = data['remark']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/rd_staff/<int:id>', methods=['DELETE'])
def delete_rd_staff(id):
    """删除研发人员记录"""
    record = RdStaff.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/rd_staff/export', methods=['GET'])
def export_rd_staff():
    """导出 Excel 数据"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)

    query = RdStaff.query.join(Company)

    if company_id:
        query = query.filter(RdStaff.company_id == company_id)
    if year_from:
        query = query.filter(RdStaff.year >= year_from)
    if year_to:
        query = query.filter(RdStaff.year <= year_to)

    records = query.order_by(RdStaff.year.desc(), Company.code).all()

    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            '研发人员规模': r.staff_count,
            '同比增长': r.growth,
            '占员工总数 (%)': r.percent_of_total,
            '本科人数': r.bachelor,
            '硕士人数': r.master,
            '本科 + 硕士占比 (%)': r.bachelor_master_ratio,
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
        download_name='rd_staff_export.xlsx'
    )
