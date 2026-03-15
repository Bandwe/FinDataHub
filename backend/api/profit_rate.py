# -*- coding: utf-8 -*-
"""
毛利率与净利率模块API
"""
from flask import request, jsonify
from sqlalchemy import and_, or_
from . import api_bp
from models import db, ProfitRate, Company
from utils.excel_parser import parse_profit_rate_excel
import pandas as pd
import io


@api_bp.route('/profit_rate', methods=['GET'])
def get_profit_rates():
    """获取利润率数据列表"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    gross_min = request.args.get('gross_min', type=float)
    gross_max = request.args.get('gross_max', type=float)
    net_min = request.args.get('net_min', type=float)
    net_max = request.args.get('net_max', type=float)
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ProfitRate.query.join(Company)
    
    if company_id:
        query = query.filter(ProfitRate.company_id == company_id)
    
    if keyword:
        query = query.filter(
            or_(
                Company.name.contains(keyword),
                Company.code.contains(keyword)
            )
        )
    
    if year_from:
        query = query.filter(ProfitRate.year >= year_from)
    if year_to:
        query = query.filter(ProfitRate.year <= year_to)
    
    if gross_min is not None:
        query = query.filter(ProfitRate.gross_profit_margin >= gross_min)
    if gross_max is not None:
        query = query.filter(ProfitRate.gross_profit_margin <= gross_max)
    
    if net_min is not None:
        query = query.filter(ProfitRate.net_profit_margin >= net_min)
    if net_max is not None:
        query = query.filter(ProfitRate.net_profit_margin <= net_max)
    
    pagination = query.order_by(ProfitRate.year.desc(), Company.code).paginate(
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


@api_bp.route('/profit_rate', methods=['POST'])
def create_profit_rate():
    """新增利润率记录"""
    data = request.get_json()
    
    # 校验
    if not data.get('company_id') or not data.get('year'):
        return jsonify({'code': 400, 'message': '公司ID和年份不能为空'}), 400
    
    # 检查是否已存在
    existing = ProfitRate.query.filter_by(
        company_id=data['company_id'],
        year=data['year']
    ).first()
    
    if existing:
        return jsonify({'code': 400, 'message': '该公司该年份的记录已存在'}), 400
    
    record = ProfitRate(
        company_id=data['company_id'],
        year=data['year'],
        gross_profit_margin=data.get('gross_profit_margin'),
        net_profit_margin=data.get('net_profit_margin')
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': record.to_dict()
    })


@api_bp.route('/profit_rate/<int:id>', methods=['PUT'])
def update_profit_rate(id):
    """更新利润率记录"""
    record = ProfitRate.query.get_or_404(id)
    data = request.get_json()
    
    if 'gross_profit_margin' in data:
        record.gross_profit_margin = data['gross_profit_margin']
    if 'net_profit_margin' in data:
        record.net_profit_margin = data['net_profit_margin']
    if 'year' in data:
        record.year = data['year']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@api_bp.route('/profit_rate/<int:id>', methods=['DELETE'])
def delete_profit_rate(id):
    """删除利润率记录"""
    record = ProfitRate.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@api_bp.route('/profit_rate/import', methods=['POST'])
def import_profit_rate():
    """导入Excel数据"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'code': 400, 'message': '仅支持Excel文件'}), 400
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 解析数据
        records = parse_profit_rate_excel(df)
        
        # 预览模式（不实际入库）
        preview = request.args.get('preview', 'false').lower() == 'true'
        
        if preview:
            return jsonify({
                'code': 200,
                'data': {
                    'preview': records,
                    'total': len(records)
                }
            })
        
        # 实际导入
        success_count = 0
        error_count = 0
        errors = []
        
        for record in records:
            try:
                # 查找公司ID
                company = Company.query.filter_by(code=record['code']).first()
                if not company:
                    error_count += 1
                    errors.append(f"未找到公司代码: {record['code']}")
                    continue
                
                # 检查是否已存在
                existing = ProfitRate.query.filter_by(
                    company_id=company.id,
                    year=record['year']
                ).first()
                
                if existing:
                    # 更新
                    existing.gross_profit_margin = record.get('gross_profit_margin')
                    existing.net_profit_margin = record.get('net_profit_margin')
                else:
                    # 新增
                    new_record = ProfitRate(
                        company_id=company.id,
                        year=record['year'],
                        gross_profit_margin=record.get('gross_profit_margin'),
                        net_profit_margin=record.get('net_profit_margin')
                    )
                    db.session.add(new_record)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"处理记录失败: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '导入完成',
            'data': {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导入失败: {str(e)}'}), 500


@api_bp.route('/profit_rate/export', methods=['GET'])
def export_profit_rate():
    """导出Excel数据"""
    company_id = request.args.get('company_id', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    
    query = ProfitRate.query.join(Company)
    
    if company_id:
        query = query.filter(ProfitRate.company_id == company_id)
    if year_from:
        query = query.filter(ProfitRate.year >= year_from)
    if year_to:
        query = query.filter(ProfitRate.year <= year_to)
    
    records = query.order_by(ProfitRate.year.desc(), Company.code).all()
    
    # 转换为DataFrame
    data = []
    for r in records:
        data.append({
            '代码': r.company.code if r.company else '',
            '个股名称': r.company.name if r.company else '',
            '年份': r.year,
            '销售毛利率(%)': r.gross_profit_margin,
            '销售净利率(%)': r.net_profit_margin
        })
    
    df = pd.DataFrame(data)
    
    # 生成Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    from flask import send_file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='profit_rate_export.xlsx'
    )
