# -*- coding: utf-8 -*-
"""
Shared fixed financial module metadata.
"""
from models import (
    NonRecurring,
    PeValuation,
    ProfitRate,
    RdExpense,
    RdStaff,
    RoeNetAsset,
    ShareholderCount,
    ShareholderStructure,
)


MODULE_SCHEMA = {
    'profit_rate': {
        'label': '毛利率与净利率',
        'filename': '利润率模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['销售毛利率(%)', '销售净利率(%)'],
        'sample': ['000001', '示例公司', 2024, 25.5, 15.2],
        'model': ProfitRate,
        'key_fields': ['company_id', 'year'],
        'field_mapping': {
            '销售毛利率(%)': 'gross_profit_margin',
            '销售净利率(%)': 'net_profit_margin'
        },
        'sheet_names': ['利润率', '毛利率']
    },
    'non_recurring': {
        'label': '扣非净利润增长',
        'filename': '扣非净利润模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['扣非净利润(亿元)', '扣非增长率'],
        'sample': ['000001', '示例公司', 2024, 10.5, 0.15],
        'model': NonRecurring,
        'key_fields': ['company_id', 'year'],
        'field_mapping': {
            '扣非净利润(亿元)': 'non_recurring_profit',
            '扣非增长率': 'non_recurring_growth'
        },
        'sheet_names': ['扣非净利润', '扣非']
    },
    'roe_net_asset': {
        'label': 'ROE与净资产',
        'filename': 'ROE与净资产模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['ROE(%)', '每股净资产(元)'],
        'sample': ['000001', '示例公司', 2024, 12.5, 8.5],
        'model': RoeNetAsset,
        'key_fields': ['company_id', 'year'],
        'field_mapping': {
            'ROE(%)': 'roe',
            '每股净资产(元)': 'net_asset_per_share'
        },
        'sheet_names': ['ROE与净资产', 'ROE', '净资产']
    },
    'pe_valuation': {
        'label': 'PE估值',
        'filename': 'PE估值模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['PE最高值', 'PE中间值', 'PE最低值', '每股收益', '类型(actual/forecast)', '备注'],
        'sample': ['000001', '示例公司', 2024, 25.0, 20.0, 15.0, 2.5, 'actual', ''],
        'model': PeValuation,
        'key_fields': ['company_id', 'year', 'type'],
        'field_mapping': {
            'PE最高值': 'pe_high',
            'PE中间值': 'pe_mid',
            'PE最低值': 'pe_low',
            '每股收益': 'eps',
            '类型(actual/forecast)': 'type',
            '备注': 'remark'
        },
        'sheet_names': ['PE估值', 'PE']
    },
    'shareholder_structure': {
        'label': '股东结构',
        'filename': '股东结构模板.xlsx',
        'required_fields': ['代码', '个股名称', '统计日期(YYYY-MM-DD)'],
        'optional_fields': ['股东类型', '持股比例(%)', '变动比例(%)'],
        'sample': ['000001', '示例公司', '2024-06-30', '产业资本', 35.5, 2.1],
        'model': ShareholderStructure,
        'key_fields': ['company_id', 'stat_date', 'shareholder_type'],
        'field_mapping': {
            '统计日期(YYYY-MM-DD)': 'stat_date',
            '股东类型': 'shareholder_type',
            '持股比例(%)': 'holding_ratio',
            '变动比例(%)': 'change_ratio'
        },
        'sheet_names': ['股东结构']
    },
    'shareholder_count': {
        'label': '股东户数',
        'filename': '股东户数模板.xlsx',
        'required_fields': ['代码', '个股名称', '统计日期(YYYY-MM-DD)'],
        'optional_fields': ['股东总人数', '较上期变化'],
        'sample': ['000001', '示例公司', '2024-06-30', 50000, -0.05],
        'model': ShareholderCount,
        'key_fields': ['company_id', 'stat_date'],
        'field_mapping': {
            '统计日期(YYYY-MM-DD)': 'stat_date',
            '股东总人数': 'total_holders',
            '较上期变化': 'change'
        },
        'sheet_names': ['股东户数']
    },
    'rd_expense': {
        'label': '研发投入',
        'filename': '研发投入模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['主营收入(元)', '研发费用(元)', '研发费用占比(%)', '费用增长率', '费用回报率'],
        'sample': ['000001', '示例公司', 2024, 100000000, 10000000, 10.0, 0.15, 0.25],
        'model': RdExpense,
        'key_fields': ['company_id', 'year'],
        'field_mapping': {
            '主营收入(元)': 'revenue',
            '研发费用(元)': 'rd_expense',
            '研发费用占比(%)': 'rd_ratio',
            '费用增长率': 'rd_growth',
            '费用回报率': 'rd_return'
        },
        'sheet_names': ['研发投入', '研发']
    },
    'rd_staff': {
        'label': '研发团队',
        'filename': '研发人员模板.xlsx',
        'required_fields': ['代码', '个股名称', '年份'],
        'optional_fields': ['研发人员规模', '同比增长', '占员工总数(%)', '本科人数', '硕士人数', '本科+硕士占比(%)', '备注'],
        'sample': ['000001', '示例公司', 2024, 500, 0.1, 25.0, 300, 150, 90.0, ''],
        'model': RdStaff,
        'key_fields': ['company_id', 'year'],
        'field_mapping': {
            '研发人员规模': 'staff_count',
            '同比增长': 'growth',
            '占员工总数(%)': 'percent_of_total',
            '本科人数': 'bachelor',
            '硕士人数': 'master',
            '本科+硕士占比(%)': 'bachelor_master_ratio',
            '备注': 'remark'
        },
        'sheet_names': ['研发人员', '研发人员']
    }
}


SHEET_NAME_TO_MODULE = {}
for module_key, schema in MODULE_SCHEMA.items():
    for sheet_name in schema.get('sheet_names', []):
        SHEET_NAME_TO_MODULE[sheet_name] = module_key


def template_columns(module_name):
    schema = MODULE_SCHEMA[module_name]
    return schema['required_fields'] + schema['optional_fields']


def template_sample(module_name):
    return [MODULE_SCHEMA[module_name]['sample']]
