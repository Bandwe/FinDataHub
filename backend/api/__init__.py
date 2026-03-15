# -*- coding: utf-8 -*-
"""
API蓝图初始化
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入各模块路由
from . import companies, profit_rate, non_recurring, roe_net_asset
from . import pe_valuation, shareholder_structure, shareholder_count
from . import rd_expense, rd_staff, templates, data_import
