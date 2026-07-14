# -*- coding: utf-8 -*-
"""
SQLAlchemy 数据模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def _float_or_none(value):
    return float(value) if value is not None else None


class Company(db.Model):
    """公司基础信息表"""
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='个股名称')
    code = db.Column(db.String(20), nullable=False, unique=True, comment='代码')
    business = db.Column(db.Text, comment='主营业务')
    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    profit_rates = db.relationship('ProfitRate', backref='company', lazy=True, cascade='all, delete-orphan')
    non_recurrings = db.relationship('NonRecurring', backref='company', lazy=True, cascade='all, delete-orphan')
    roe_net_assets = db.relationship('RoeNetAsset', backref='company', lazy=True, cascade='all, delete-orphan')
    pe_valuations = db.relationship('PeValuation', backref='company', lazy=True, cascade='all, delete-orphan')
    shareholder_structures = db.relationship('ShareholderStructure', backref='company', lazy=True, cascade='all, delete-orphan')
    shareholder_counts = db.relationship('ShareholderCount', backref='company', lazy=True, cascade='all, delete-orphan')
    rd_expenses = db.relationship('RdExpense', backref='company', lazy=True, cascade='all, delete-orphan')
    rd_staffs = db.relationship('RdStaff', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'business': self.business,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class ProfitRate(db.Model):
    """利润率表（毛利率与净利率）"""
    __tablename__ = 'profit_rate'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    gross_profit_margin = db.Column(db.Float, comment='销售毛利率%')
    net_profit_margin = db.Column(db.Float, comment='销售净利率%')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', name='unique_company_year_profit'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'gross_profit_margin': _float_or_none(self.gross_profit_margin),
            'net_profit_margin': _float_or_none(self.net_profit_margin),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class NonRecurring(db.Model):
    """扣非净利润增长表"""
    __tablename__ = 'non_recurring'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    non_recurring_profit = db.Column(db.Float, comment='扣非净利润（亿元）')
    non_recurring_growth = db.Column(db.Float, comment='扣非增长率（例如-0.8332表示-83.32%）')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', name='unique_company_year_nonrec'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'non_recurring_profit': _float_or_none(self.non_recurring_profit),
            'non_recurring_growth': _float_or_none(self.non_recurring_growth),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RoeNetAsset(db.Model):
    """ROE与净资产表"""
    __tablename__ = 'roe_net_asset'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    roe = db.Column(db.Float, comment='净资产收益率%')
    net_asset_per_share = db.Column(db.Float, comment='每股净资产（元）')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', name='unique_company_year_roe'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'roe': _float_or_none(self.roe),
            'net_asset_per_share': _float_or_none(self.net_asset_per_share),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class PeValuation(db.Model):
    """PE估值表"""
    __tablename__ = 'pe_valuation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    pe_high = db.Column(db.Float, comment='PE最高值')
    pe_mid = db.Column(db.Float, comment='PE中间值')
    pe_low = db.Column(db.Float, comment='PE最低值')
    eps = db.Column(db.Float, comment='每股收益')
    type = db.Column(db.Enum('actual', 'forecast'), default='actual', comment='实际或预测')
    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', 'type', name='unique_company_year_type_pe'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'pe_high': _float_or_none(self.pe_high),
            'pe_mid': _float_or_none(self.pe_mid),
            'pe_low': _float_or_none(self.pe_low),
            'eps': _float_or_none(self.eps),
            'type': self.type,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class ShareholderStructure(db.Model):
    """股东结构表"""
    __tablename__ = 'shareholder_structure'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    stat_date = db.Column(db.Date, nullable=False, comment='统计日期')
    shareholder_type = db.Column(db.String(50), comment='股东类型（如产业资本、公募基金等）')
    holding_ratio = db.Column(db.Float, comment='持股比例%')
    change_ratio = db.Column(db.Float, comment='变动比例%（较上期）')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'stat_date', 'shareholder_type', name='unique_company_date_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.stat_date.year if self.stat_date else None,
            'stat_date': self.stat_date.strftime('%Y-%m-%d') if self.stat_date else None,
            'shareholder_type': self.shareholder_type,
            'holding_ratio': _float_or_none(self.holding_ratio),
            'change_ratio': _float_or_none(self.change_ratio),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class ShareholderCount(db.Model):
    """股东户数表"""
    __tablename__ = 'shareholder_count'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    stat_date = db.Column(db.Date, nullable=False, comment='统计日期')
    total_holders = db.Column(db.Integer, comment='股东总人数')
    change = db.Column(db.Float, comment='较上期变化（例如-0.0187表示-1.87%）')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'stat_date', name='unique_company_date_count'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.stat_date.year if self.stat_date else None,
            'stat_date': self.stat_date.strftime('%Y-%m-%d') if self.stat_date else None,
            'total_holders': self.total_holders,
            'change': _float_or_none(self.change),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RdExpense(db.Model):
    """研发投入表"""
    __tablename__ = 'rd_expense'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Float, comment='主营收入（元）')
    rd_expense = db.Column(db.Float, comment='研发费用（元）')
    rd_ratio = db.Column(db.Float, comment='研发费用占比%')
    rd_growth = db.Column(db.Float, comment='费用增长率%（如-0.121表示-12.1%）')
    rd_return = db.Column(db.Float, comment='费用回报率%（可选）')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', name='unique_company_year_rdexp'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'revenue': _float_or_none(self.revenue),
            'rd_expense': _float_or_none(self.rd_expense),
            'rd_ratio': _float_or_none(self.rd_ratio),
            'rd_growth': _float_or_none(self.rd_growth),
            'rd_return': _float_or_none(self.rd_return),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class RdStaff(db.Model):
    """研发人员表"""
    __tablename__ = 'rd_staff'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    staff_count = db.Column(db.Integer, comment='研发人员规模')
    growth = db.Column(db.Float, comment='同比增长（如0.3表示30%）')
    percent_of_total = db.Column(db.Float, comment='占员工总数%')
    bachelor = db.Column(db.Integer, comment='本科人数')
    master = db.Column(db.Integer, comment='硕士人数')
    bachelor_master_ratio = db.Column(db.Float, comment='本科+硕士占研发人员比例%')
    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'year', name='unique_company_year_rdstaff'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'staff_count': self.staff_count,
            'growth': _float_or_none(self.growth),
            'percent_of_total': _float_or_none(self.percent_of_total),
            'bachelor': self.bachelor,
            'master': self.master,
            'bachelor_master_ratio': _float_or_none(self.bachelor_master_ratio),
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class CustomModule(db.Model):
    """自定义模块/行业模板表"""
    __tablename__ = 'custom_module'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='模块名称')
    code = db.Column(db.String(30), nullable=False, unique=True, comment='模块代码')
    icon = db.Column(db.String(50), default='Grid', comment='模块图标')
    description = db.Column(db.Text, comment='模块描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    is_locked = db.Column(db.Boolean, default=True, comment='模板是否已确认锁定')
    locked_at = db.Column(db.DateTime, comment='模板锁定时间')
    version = db.Column(db.Integer, default=1, comment='模板版本')
    source_module_id = db.Column(db.Integer, comment='复制来源模板ID')
    created_by = db.Column(db.String(50), comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    keywords = db.relationship('ModuleKeyword', backref='module', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'icon': self.icon,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'locked_at': self.locked_at.strftime('%Y-%m-%d %H:%M:%S') if self.locked_at else None,
            'version': self.version,
            'source_module_id': self.source_module_id,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'keywords': [
                k.to_dict() for k in sorted(self.keywords, key=lambda item: item.sort_order or 0)
                if k.keyword not in {'code', 'name', 'year'}
            ] if self.keywords else []
        }


class ModuleKeyword(db.Model):
    """模块表格关键词表"""
    __tablename__ = 'module_keyword'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('custom_module.id'), nullable=False)
    keyword = db.Column(db.String(50), nullable=False, comment='关键词')
    label = db.Column(db.String(100), comment='显示标签')
    data_type = db.Column(db.String(20), default='string', comment='数据类型(string/number/date)')
    is_required = db.Column(db.Boolean, default=False, comment='是否必填')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('module_id', 'keyword', name='unique_module_keyword'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'keyword': self.keyword,
            'label': self.label,
            'data_type': self.data_type,
            'is_required': self.is_required,
            'sort_order': self.sort_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class CustomModuleData(db.Model):
    """自定义模块数据表"""
    __tablename__ = 'custom_module_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('custom_module.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    # 动态数据字段存储为JSON
    data = db.Column(db.JSON, default=dict, comment='动态数据字段')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    company = db.relationship('Company', backref='custom_module_data', lazy=True)
    module = db.relationship('CustomModule', backref='data_records', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('module_id', 'company_id', 'year', name='unique_module_company_year'),
    )
    
    def to_dict(self):
        result = {
            'id': self.id,
            'module_id': self.module_id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'company_code': self.company.code if self.company else None,
            'year': self.year,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        # 合并动态数据字段
        if self.data:
            result.update(self.data)
        return result
