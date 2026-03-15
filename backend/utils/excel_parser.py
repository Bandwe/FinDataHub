# -*- coding: utf-8 -*-
"""
Excel解析工具
支持将宽表格式转换为长表格式
"""
import pandas as pd
import re


def parse_profit_rate_excel(df):
    """
    解析利润率Excel文件
    支持两种格式：
    1. 长表格式：代码、个股名称、年份、销售毛利率(%)、销售净利率(%)
    2. 宽表格式：代码、个股名称、2024毛利率、2024净利率、2023毛利率...
    """
    records = []
    
    # 检测是否为长表格式
    if '年份' in df.columns or 'year' in df.columns:
        # 长表格式直接读取
        for _, row in df.iterrows():
            code = str(row.get('代码', '')).strip()
            if not code or code == 'nan':
                continue
            
            year = row.get('年份') or row.get('year')
            if pd.isna(year):
                continue
            
            records.append({
                'code': code,
                'year': int(year),
                'gross_profit_margin': parse_decimal(row.get('销售毛利率(%)')),
                'net_profit_margin': parse_decimal(row.get('销售净利率(%)'))
            })
    else:
        # 宽表格式需要转换
        # 假设列名格式为：代码、个股名称、2024销售毛利率(%)、2024销售净利率(%)、...
        year_cols = {}
        
        for col in df.columns:
            col_str = str(col)
            # 匹配年份+指标的模式
            match = re.match(r'(\d{4}).*?(毛利率|净利率)', col_str)
            if match:
                year = int(match.group(1))
                metric = 'gross' if '毛利' in match.group(2) else 'net'
                if year not in year_cols:
                    year_cols[year] = {}
                year_cols[year][metric] = col
        
        # 转换数据
        for _, row in df.iterrows():
            code = str(row.get('代码', '')).strip()
            if not code or code == 'nan':
                continue
            
            for year, cols in year_cols.items():
                gross_col = cols.get('gross')
                net_col = cols.get('net')
                
                if gross_col and not pd.isna(row.get(gross_col)):
                    records.append({
                        'code': code,
                        'year': year,
                        'gross_profit_margin': parse_decimal(row.get(gross_col)),
                        'net_profit_margin': parse_decimal(row.get(net_col)) if net_col else None
                    })
    
    return records


def parse_decimal(value):
    """解析数值，处理各种格式"""
    if pd.isna(value):
        return None
    try:
        # 处理百分比格式（如 "25.5%"）
        if isinstance(value, str) and '%' in value:
            return float(value.replace('%', ''))
        return float(value)
    except (ValueError, TypeError):
        return None


def validate_data(record, module_type):
    """
    数据校验
    """
    errors = []
    
    if module_type == 'profit_rate':
        # 毛利率和净利率范围校验
        gross = record.get('gross_profit_margin')
        net = record.get('net_profit_margin')
        
        if gross is not None and (gross < -100 or gross > 100):
            errors.append(f"毛利率超出合理范围: {gross}")
        
        if net is not None and (net < -100 or net > 100):
            errors.append(f"净利率超出合理范围: {net}")
    
    return errors
