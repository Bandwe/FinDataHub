# -*- coding: utf-8 -*-
"""
自定义模块数据API
"""
from flask import request, jsonify
from . import api_bp
from models import db, CustomModule, CustomModuleData, Company
from sqlalchemy import or_
import pandas as pd
from io import BytesIO


@api_bp.route('/custom-module-data/<string:module_code>', methods=['GET'])
def get_custom_module_data(module_code):
    """获取自定义模块数据列表"""
    try:
        # 获取模块信息
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '')
        
        # 构建查询
        query = CustomModuleData.query.filter_by(module_id=module.id)
        
        # 关键词搜索
        if keyword:
            query = query.join(Company).filter(
                or_(
                    Company.name.contains(keyword),
                    Company.code.contains(keyword)
                )
            )
        
        # 分页
        pagination = query.order_by(CustomModuleData.year.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>', methods=['POST'])
def create_custom_module_data(module_code):
    """创建自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('company_id') or not data.get('year'):
            return jsonify({'code': 400, 'message': '公司和年份不能为空'}), 400
        
        # 检查是否已存在
        existing = CustomModuleData.query.filter_by(
            module_id=module.id,
            company_id=data['company_id'],
            year=data['year']
        ).first()
        
        if existing:
            return jsonify({'code': 400, 'message': '该记录已存在'}), 400
        
        # 提取动态数据字段
        dynamic_data = {}
        for keyword in module.keywords:
            if keyword.keyword in data:
                dynamic_data[keyword.keyword] = data[keyword.keyword]
        
        # 创建记录
        record = CustomModuleData(
            module_id=module.id,
            company_id=data['company_id'],
            year=data['year'],
            data=dynamic_data
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': record.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>/<int:record_id>', methods=['PUT'])
def update_custom_module_data(module_code, record_id):
    """更新自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        record = CustomModuleData.query.filter_by(id=record_id, module_id=module.id).first()
        if not record:
            return jsonify({'code': 404, 'message': '记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新年份
        if 'year' in data:
            # 检查新组合是否已存在
            existing = CustomModuleData.query.filter_by(
                module_id=module.id,
                company_id=record.company_id,
                year=data['year']
            ).first()
            if existing and existing.id != record_id:
                return jsonify({'code': 400, 'message': '该记录已存在'}), 400
            record.year = data['year']
        
        # 更新动态数据字段
        dynamic_data = record.data or {}
        for keyword in module.keywords:
            if keyword.keyword in data:
                dynamic_data[keyword.keyword] = data[keyword.keyword]
        record.data = dynamic_data
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': record.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>/<int:record_id>', methods=['DELETE'])
def delete_custom_module_data(module_code, record_id):
    """删除自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        record = CustomModuleData.query.filter_by(id=record_id, module_id=module.id).first()
        if not record:
            return jsonify({'code': 404, 'message': '记录不存在'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>/export', methods=['GET'])
def export_custom_module_data(module_code):
    """导出自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        # 获取所有数据
        records = CustomModuleData.query.filter_by(module_id=module.id).all()
        
        if not records:
            return jsonify({'code': 400, 'message': '没有数据可导出'}), 400
        
        # 准备数据
        data_list = []
        for record in records:
            item = record.to_dict()
            row = {
                '代码': item.get('company_code'),
                '个股名称': item.get('company_name'),
                '年份': item.get('year')
            }
            # 添加动态字段
            for keyword in module.keywords:
                row[keyword.label] = item.get(keyword.keyword)
            data_list.append(row)
        
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        
        # 导出到Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=module.name)
        output.seek(0)
        
        return output.getvalue(), 200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': f'attachment; filename={module_code}_export.xlsx'
        }
    except Exception as e:
        return jsonify({'code': 500, 'message': f'导出失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>/import', methods=['POST'])
def import_custom_module_data(module_code):
    """导入自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '请选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'message': '请选择文件'}), 400
        
        # 读取Excel
        df = pd.read_excel(file)
        
        # 构建关键词映射
        keyword_map = {}
        for keyword in module.keywords:
            keyword_map[keyword.label] = keyword.keyword
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 获取公司信息
                company_code = str(row.get('代码', ''))
                company_name = str(row.get('个股名称', ''))
                year = int(row.get('年份', 0))
                
                if not company_code or not year:
                    continue
                
                # 查找或创建公司
                company = Company.query.filter_by(code=company_code).first()
                if not company:
                    company = Company(code=company_code, name=company_name or company_code)
                    db.session.add(company)
                    db.session.flush()
                
                # 构建动态数据
                dynamic_data = {}
                for label, keyword in keyword_map.items():
                    if label in row and pd.notna(row[label]):
                        dynamic_data[keyword] = row[label]
                
                # 检查是否已存在
                existing = CustomModuleData.query.filter_by(
                    module_id=module.id,
                    company_id=company.id,
                    year=year
                ).first()
                
                if existing:
                    # 更新
                    existing.data = dynamic_data
                else:
                    # 创建
                    record = CustomModuleData(
                        module_id=module.id,
                        company_id=company.id,
                        year=year,
                        data=dynamic_data
                    )
                    db.session.add(record)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f'第{index + 2}行: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'导入完成: 成功{success_count}条, 失败{error_count}条',
            'data': {'success': success_count, 'error': error_count, 'errors': errors}
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'导入失败: {str(e)}'}), 500


@api_bp.route('/custom-module-data/<string:module_code>/compare', methods=['POST'])
def compare_custom_module_data(module_code):
    """对比自定义模块数据"""
    try:
        module = CustomModule.query.filter_by(code=module_code, is_active=True).first()
        if not module:
            return jsonify({'code': 404, 'message': '模块不存在'}), 404
        
        data = request.get_json()
        company_ids = data.get('company_ids', [])
        years = data.get('years', [])
        metric = data.get('metric', '')
        
        if not company_ids or not years or not metric:
            return jsonify({'code': 400, 'message': '参数不完整'}), 400
        
        # 查询数据
        records = CustomModuleData.query.filter(
            CustomModuleData.module_id == module.id,
            CustomModuleData.company_id.in_(company_ids),
            CustomModuleData.year.in_(years)
        ).all()
        
        # 按公司分组
        company_data = {}
        for record in records:
            company_name = record.company.name if record.company else '未知'
            if company_name not in company_data:
                company_data[company_name] = []
            
            value = record.data.get(metric) if record.data else None
            company_data[company_name].append({
                'year': record.year,
                'value': value
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': company_data
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500