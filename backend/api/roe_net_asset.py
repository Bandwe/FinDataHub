# -*- coding: utf-8 -*-
"""
ROE与净资产模块API
"""
from flask import request, jsonify
from sqlalchemy import or_
from . import api_bp
from models import db, RoeNetAsset, Company
import pandas as pd
import io


@api_bp.route('/roe_net_asset', methods=['GET'])
def get_roe_net_assets():
    """获取ROE与净资产数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = RoeNetAsset.query.join(Company)
    
    if company_id:
        query = query.filter(RoeNetAsset.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(RoeNetAsset.year >= year_from)
    if year_to:
        query = query.filter(RoeNetAsset.year <= year_to)
    
    pagination = query.order_by(RoeNetAsset.year.desc(), Company.code).paginate(
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


@api_bp.route('/roe_net_asset', methods=['POST'])
def create_roe_net_asset():
    """新增ROE与净资产记录"""
    data = request.get_json()
    
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    existing = RoeNetAsset.query.filter_by(
        company_id=data['company_id'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份的记录已存在'}), 400
    
    record = RoeNetAsset(
        company_id=data['company_id'],
        year=data['year'],
        roe=data.get('roe'),
        net_asset_per_share=data.get('net_asset_per_share')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/roe_net_asset/<int:id>', methods=['PUT'])
def update_roe_net_asset(id):
    """更新ROE与净资产记录"""
    record = RoeNetAsset.query.get_or_404(id)
    data = request.get_json()
    
    if 'roe' in data:
        record.roe = data['roe']
    if 'net_asset_per_share' in data:
        record.net_asset_per_share = data['net_asset_per_share']
    if 'year' in data:
        record.year = data['year']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/roe_net_asset/<int:id>', methods=['DELETE'])
def delete_roe_net_asset(id):
    """删除ROE与净资产记录"""
    record = RoeNetAsset.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/roe_net_asset/export', methods=['GET'])
def export_roe_net_asset():
    """导出Excel数据"""
    records = RoeNetAsset.query.join(Company).order_by(RoeNetAsset.year.desc(), Company.code).all()
    
    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            'ROE(%)': r.roe,
            '每股净资产(元)': r.net_asset_per_share
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
        download_name='roe_net_asset_export.xlsx'
    )
