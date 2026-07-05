# -*- coding: utf-8 -*-
"""
行业模板管理API
"""
from flask import jsonify, request, send_file

from . import api_bp
from models import db
from services.industry_templates import (
    ServiceError,
    clone_template,
    confirm_template,
    create_template,
    delete_or_disable_template,
    get_template,
    get_template_by_code,
    list_templates,
    make_template_workbook,
    serialize_template,
    update_template,
)


def success(data=None, message='获取成功'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def failure(error):
    db.session.rollback()
    if isinstance(error, ServiceError):
        return jsonify({'code': error.status_code, 'message': error.message}), error.status_code
    return jsonify({'code': 500, 'message': str(error)}), 500


@api_bp.route('/industry-templates', methods=['GET'])
def get_industry_templates():
    try:
        return success(list_templates(include_inactive=False, locked_only=True))
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/all', methods=['GET'])
def get_all_industry_templates():
    try:
        return success(list_templates(include_inactive=True, locked_only=False))
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<int:template_id>', methods=['GET'])
def get_industry_template(template_id):
    try:
        return success(serialize_template(get_template(template_id)))
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates', methods=['POST'])
def create_industry_template():
    try:
        return success(create_template(request.get_json() or {}), '创建成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<int:template_id>', methods=['PUT'])
def update_industry_template(template_id):
    try:
        return success(update_template(template_id, request.get_json() or {}), '更新成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<int:template_id>/confirm', methods=['POST'])
def confirm_industry_template(template_id):
    try:
        return success(confirm_template(template_id), '模板已确认')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<int:template_id>/clone', methods=['POST'])
def clone_industry_template(template_id):
    try:
        return success(clone_template(template_id, request.get_json() or {}), '复制成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<int:template_id>', methods=['DELETE'])
def delete_industry_template(template_id):
    try:
        result = delete_or_disable_template(template_id)
        return success(result, '停用成功' if result.get('disabled') else '删除成功')
    except Exception as exc:
        return failure(exc)


@api_bp.route('/industry-templates/<string:template_code>/template', methods=['GET'])
def download_industry_template(template_code):
    try:
        module = get_template_by_code(template_code, require_active=True, require_locked=True)
        output = make_template_workbook(module)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{module.code}_template.xlsx'
        )
    except Exception as exc:
        return failure(exc)
