# -*- coding: utf-8 -*-
"""
初始化示例数据
"""
from datetime import date
from app import app
from models import db, Company, ProfitRate, NonRecurring, RoeNetAsset, PeValuation
from models import ShareholderStructure, ShareholderCount, RdExpense, RdStaff


def init_data():
    with app.app_context():
        # 创建表
        db.create_all()
        
        # 检查是否已有数据
        if Company.query.first():
            print("数据已存在，跳过初始化")
            return
        
        # 创建示例公司
        companies = [
            Company(name='长电科技', code='600584', business='集成电路封装测试', remark='半导体封测龙头'),
            Company(name='华天科技', code='002185', business='集成电路封装测试', remark='国内封测三强之一'),
            Company(name='通富微电', code='002156', business='集成电路封装测试', remark='AMD核心封测伙伴'),
            Company(name='中芯国际', code='688981', business='集成电路晶圆代工', remark='国内晶圆代工龙头'),
            Company(name='北方华创', code='002371', business='半导体设备', remark='国产设备龙头'),
        ]
        
        for c in companies:
            db.session.add(c)
        db.session.commit()
        
        print(f"创建了 {len(companies)} 家公司")
        
        # 获取公司ID
        cjkj = Company.query.filter_by(code='600584').first()
        htkj = Company.query.filter_by(code='002185').first()
        tfwd = Company.query.filter_by(code='002156').first()
        zxgj = Company.query.filter_by(code='688981').first()
        bfhc = Company.query.filter_by(code='002371').first()
        
        # 利润率数据
        profit_rates = [
            ProfitRate(company_id=cjkj.id, year=2024, gross_profit_margin=18.52, net_profit_margin=8.35),
            ProfitRate(company_id=cjkj.id, year=2023, gross_profit_margin=17.85, net_profit_margin=7.92),
            ProfitRate(company_id=cjkj.id, year=2022, gross_profit_margin=16.23, net_profit_margin=6.85),
            ProfitRate(company_id=htkj.id, year=2024, gross_profit_margin=16.78, net_profit_margin=6.52),
            ProfitRate(company_id=htkj.id, year=2023, gross_profit_margin=15.92, net_profit_margin=5.88),
            ProfitRate(company_id=tfwd.id, year=2024, gross_profit_margin=15.35, net_profit_margin=5.25),
            ProfitRate(company_id=zxgj.id, year=2024, gross_profit_margin=22.15, net_profit_margin=12.58),
            ProfitRate(company_id=bfhc.id, year=2024, gross_profit_margin=38.65, net_profit_margin=15.22),
        ]
        
        for p in profit_rates:
            db.session.add(p)
        
        # 扣非净利润数据
        non_recurrings = [
            NonRecurring(company_id=cjkj.id, year=2024, non_recurring_profit=25.85, non_recurring_growth=0.1523),
            NonRecurring(company_id=cjkj.id, year=2023, non_recurring_profit=22.42, non_recurring_growth=-0.0832),
            NonRecurring(company_id=htkj.id, year=2024, non_recurring_profit=8.52, non_recurring_growth=0.1256),
            NonRecurring(company_id=tfwd.id, year=2024, non_recurring_profit=6.35, non_recurring_growth=0.0852),
            NonRecurring(company_id=zxgj.id, year=2024, non_recurring_profit=45.62, non_recurring_growth=0.1856),
        ]
        
        for n in non_recurrings:
            db.session.add(n)
        
        # ROE与净资产数据
        roe_net_assets = [
            RoeNetAsset(company_id=cjkj.id, year=2024, roe=12.58, net_asset_per_share=8.52),
            RoeNetAsset(company_id=cjkj.id, year=2023, roe=11.25, net_asset_per_share=7.85),
            RoeNetAsset(company_id=htkj.id, year=2024, roe=8.52, net_asset_per_share=5.35),
            RoeNetAsset(company_id=tfwd.id, year=2024, roe=7.85, net_asset_per_share=4.92),
            RoeNetAsset(company_id=zxgj.id, year=2024, roe=6.52, net_asset_per_share=15.85),
            RoeNetAsset(company_id=bfhc.id, year=2024, roe=15.25, net_asset_per_share=28.65),
        ]
        
        for r in roe_net_assets:
            db.session.add(r)
        
        # PE估值数据
        pe_valuations = [
            PeValuation(company_id=cjkj.id, year=2024, pe_high=35.50, pe_mid=28.50, pe_low=22.00, eps=1.25, type='actual', remark=''),
            PeValuation(company_id=cjkj.id, year=2025, pe_high=38.00, pe_mid=30.00, pe_low=25.00, eps=1.45, type='forecast', remark='预测值'),
            PeValuation(company_id=htkj.id, year=2024, pe_high=28.50, pe_mid=22.50, pe_low=18.00, eps=0.85, type='actual', remark=''),
            PeValuation(company_id=tfwd.id, year=2024, pe_high=32.00, pe_mid=26.50, pe_low=20.00, eps=0.95, type='actual', remark=''),
        ]
        
        for p in pe_valuations:
            db.session.add(p)
        
        # 股东结构数据
        shareholder_structures = [
            ShareholderStructure(company_id=cjkj.id, stat_date=date(2024, 6, 30), shareholder_type='产业资本', holding_ratio=35.50, change_ratio=2.10),
            ShareholderStructure(company_id=cjkj.id, stat_date=date(2024, 6, 30), shareholder_type='公募基金', holding_ratio=12.50, change_ratio=-1.50),
            ShareholderStructure(company_id=cjkj.id, stat_date=date(2024, 6, 30), shareholder_type='北向资金', holding_ratio=8.50, change_ratio=0.80),
            ShareholderStructure(company_id=htkj.id, stat_date=date(2024, 6, 30), shareholder_type='产业资本', holding_ratio=42.00, change_ratio=1.50),
        ]
        
        for s in shareholder_structures:
            db.session.add(s)
        
        # 股东户数数据
        shareholder_counts = [
            ShareholderCount(company_id=cjkj.id, stat_date=date(2024, 6, 30), total_holders=125680, change=-0.0187),
            ShareholderCount(company_id=cjkj.id, stat_date=date(2024, 3, 31), total_holders=128080, change=0.0256),
            ShareholderCount(company_id=htkj.id, stat_date=date(2024, 6, 30), total_holders=85620, change=-0.0125),
            ShareholderCount(company_id=tfwd.id, stat_date=date(2024, 6, 30), total_holders=68250, change=0.0085),
        ]
        
        for s in shareholder_counts:
            db.session.add(s)
        
        # 研发投入数据
        rd_expenses = [
            RdExpense(company_id=cjkj.id, year=2024, revenue=2850000000, rd_expense=125000000, rd_ratio=4.38, rd_growth=0.1523, rd_return=0.1856),
            RdExpense(company_id=cjkj.id, year=2023, revenue=2450000000, rd_expense=108500000, rd_ratio=4.43, rd_growth=0.0852, rd_return=0.1652),
            RdExpense(company_id=htkj.id, year=2024, revenue=1250000000, rd_expense=62500000, rd_ratio=5.00, rd_growth=0.1256, rd_return=0.1452),
            RdExpense(company_id=zxgj.id, year=2024, revenue=4500000000, rd_expense=850000000, rd_ratio=18.89, rd_growth=0.1856, rd_return=0.2256),
            RdExpense(company_id=bfhc.id, year=2024, revenue=1850000000, rd_expense=285000000, rd_ratio=15.41, rd_growth=0.2256, rd_return=0.2856),
        ]
        
        for r in rd_expenses:
            db.session.add(r)
        
        # 研发人员数据
        rd_staffs = [
            RdStaff(company_id=cjkj.id, year=2024, staff_count=2850, growth=0.125, percent_of_total=25.50, bachelor=1520, master=850, bachelor_master_ratio=83.20, remark=''),
            RdStaff(company_id=cjkj.id, year=2023, staff_count=2535, growth=0.085, percent_of_total=24.20, bachelor=1350, master=750, bachelor_master_ratio=82.80, remark=''),
            RdStaff(company_id=htkj.id, year=2024, staff_count=1850, growth=0.095, percent_of_total=22.50, bachelor=980, master=520, bachelor_master_ratio=81.20, remark=''),
            RdStaff(company_id=zxgj.id, year=2024, staff_count=4500, growth=0.185, percent_of_total=35.80, bachelor=2150, master=1850, bachelor_master_ratio=88.90, remark=''),
            RdStaff(company_id=bfhc.id, year=2024, staff_count=3200, growth=0.225, percent_of_total=42.50, bachelor=1520, master=1280, bachelor_master_ratio=87.50, remark=''),
        ]
        
        for r in rd_staffs:
            db.session.add(r)
        
        db.session.commit()
        print("示例数据初始化完成！")


if __name__ == '__main__':
    init_data()
