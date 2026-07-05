# -*- coding: utf-8 -*-
"""
行业模板数据API
"""
from flask import jsonify, request, send_file

from . import api_bp
from services.industry_templates import (
    ServiceError,
    compare_industry_data,
    create_industry_record,
    delete_industry_record,
    export_industry_data,
    import_industry_data,
    list_industry_data,
    update_industry_record,
)


def success(data=None, message='获取成功'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def failure(error):
    if isinstance(error, ServiceError):
        return jsonify({'code': error.status_code, 'message': error.message}), error.status_code
    return jsonify({'code': 500, 'message': str(error)}), 500


@api_bp.route('/industry-data/<string:template_code>', methods=['GET'])
def get_industry_data(template_code):
    try:
        return success(list_industry_data(template_code, request.args))
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>', methods=['POST'])
def create_industry_data(template_code):
    try:
        return success(create_industry_record(template_code, request.get_json() or {}), '创建成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>/<int:record_id>', methods=['PUT'])
def update_industry_data(template_code, record_id):
    try:
        return success(update_industry_record(template_code, record_id, request.get_json() or {}), '更新成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>/<int:record_id>', methods=['DELETE'])
def delete_industry_data(template_code, record_id):
    try:
        delete_industry_record(template_code, record_id)
        return success(None, '删除成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>/import', methods=['POST'])
def import_industry_records(template_code):
    try:
        result = import_industry_data(template_code, request.files.get('file'))
        return success(result, f'导入完成: 成功{result["success"]}条, 失败{result["error"]}条')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>/export', methods=['GET'])
def export_industry_records(template_code):
    try:
        output = export_industry_data(template_code)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{template_code}_export.xlsx'
        )
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-data/<string:template_code>/compare', methods=['POST'])
def compare_industry_records(template_code):
    try:
        return success(compare_industry_data(template_code, request.get_json() or {}))
    except Exception as exc:
        return failure(exc)
