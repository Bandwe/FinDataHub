# -*- coding: utf-8 -*-
"""
模板下载API
"""
from flask import send_file, jsonify
from . import api_bp
import pandas as pd
import io


# 模板字段定义
TEMPLATES = {
    'profit_rate': {
        'filename': '利润率模板.xlsx',
        'columns': ['代码', '个股名称', '年份', '销售毛利率(%)', '销售净利率(%)'],
        'sample': [['000001', '示例公司', 2024, 25.5, 15.2]]
    },
    'non_recurring': {
        'filename': '扣非净利润模板.xlsx',
        'columns': ['代码', '个股名称', '年份', '扣非净利润(亿元)', '扣非增长率'],
        'sample': [['000001', '示例公司', 2024, 10.5, 0.15]]
    },
    'roe_net_asset': {
        'filename': 'ROE与净资产模板.xlsx',
        'columns': ['代码', '个股名称', '年份', 'ROE(%)', '每股净资产(元)'],
        'sample': [['000001', '示例公司', 2024, 12.5, 8.5]]
    },
    'pe_valuation': {
        'filename': 'PE估值模板.xlsx',
        'columns': ['代码', '个股名称', '年份', 'PE最高值', 'PE中间值', 'PE最低值', '每股收益', '类型(actual/forecast)', '备注'],
        'sample': [['000001', '示例公司', 2024, 25.0, 20.0, 15.0, 2.5, 'actual', '']]
    },
    'shareholder_structure': {
        'filename': '股东结构模板.xlsx',
        'columns': ['代码', '个股名称', '统计日期(YYYY-MM-DD)', '股东类型', '持股比例(%)', '变动比例(%)'],
        'sample': [['000001', '示例公司', '2024-06-30', '产业资本', 35.5, 2.1]]
    },
    'shareholder_count': {
        'filename': '股东户数模板.xlsx',
        'columns': ['代码', '个股名称', '统计日期(YYYY-MM-DD)', '股东总人数', '较上期变化'],
        'sample': [['000001', '示例公司', '2024-06-30', 50000, -0.05]]
    },
    'rd_expense': {
        'filename': '研发投入模板.xlsx',
        'columns': ['代码', '个股名称', '年份', '主营收入(元)', '研发费用(元)', '研发费用占比(%)', '费用增长率', '费用回报率'],
        'sample': [['000001', '示例公司', 2024, 100000000, 10000000, 10.0, 0.15, 0.25]]
    },
    'rd_staff': {
        'filename': '研发人员模板.xlsx',
        'columns': ['代码', '个股名称', '年份', '研发人员规模', '同比增长', '占员工总数(%)', '本科人数', '硕士人数', '本科+硕士占比(%)', '备注'],
        'sample': [['000001', '示例公司', 2024, 500, 0.1, 25.0, 300, 150, 90.0, '']]
    }
}


@api_bp.route('/templates/<module_name>', methods=['GET'])
def download_template(module_name):
    """下载指定模块的Excel模板"""
    if module_name not in TEMPLATES:
        return jsonify({'code': 404, 'message': '模板不存在'}), 404
    
    template = TEMPLATES[module_name]
    
    # 创建DataFrame
    df = pd.DataFrame(template['sample'], columns=template['columns'])
    
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
