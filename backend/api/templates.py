# -*- coding: utf-8 -*-
"""
模板下载API
"""
from flask import send_file, jsonify
from . import api_bp
from services.module_registry import MODULE_SCHEMA, template_columns, template_sample
import pandas as pd
import io


@api_bp.route('/templates/<module_name>', methods=['GET'])
def download_template(module_name):
    """下载指定模块的Excel模板"""
    if module_name not in MODULE_SCHEMA:
        return jsonify({'code': 404, 'message': '模板不存在'}), 404
    
    template = MODULE_SCHEMA[module_name]
    
    # 创建DataFrame
    df = pd.DataFrame(template_sample(module_name), columns=template_columns(module_name))
    
    # 生成Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=template['filename']
    )
