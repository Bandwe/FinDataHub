-- FinDataHub 数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS findata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE findata;

-- 公司基础信息表
CREATE TABLE IF NOT EXISTS company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '个股名称',
    code VARCHAR(20) NOT NULL UNIQUE COMMENT '代码',
    business TEXT COMMENT '主营业务',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公司基础信息表';

-- 利润率表（毛利率与净利率）
CREATE TABLE IF NOT EXISTS profit_rate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    gross_profit_margin DECIMAL(5,2) COMMENT '销售毛利率%',
    net_profit_margin DECIMAL(5,2) COMMENT '销售净利率%',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year (company_id, year),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='利润率表';

-- 扣非净利润增长表
CREATE TABLE IF NOT EXISTS non_recurring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    non_recurring_profit DECIMAL(15,2) COMMENT '扣非净利润（亿元）',
    non_recurring_growth DECIMAL(10,4) COMMENT '扣非增长率（例如-0.8332表示-83.32%）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year (company_id, year),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='扣非净利润增长表';

-- ROE与净资产表
CREATE TABLE IF NOT EXISTS roe_net_asset (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    roe DECIMAL(5,2) COMMENT '净资产收益率%',
    net_asset_per_share DECIMAL(10,2) COMMENT '每股净资产（元）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year (company_id, year),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ROE与净资产表';

-- PE估值表
CREATE TABLE IF NOT EXISTS pe_valuation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    pe_high DECIMAL(10,2) COMMENT 'PE最高值',
    pe_mid DECIMAL(10,2) COMMENT 'PE中间值',
    pe_low DECIMAL(10,2) COMMENT 'PE最低值',
    eps DECIMAL(10,2) COMMENT '每股收益',
    type ENUM('actual','forecast') DEFAULT 'actual' COMMENT '实际或预测',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year_type (company_id, year, type),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='PE估值表';

-- 股东结构表
CREATE TABLE IF NOT EXISTS shareholder_structure (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    stat_date DATE NOT NULL COMMENT '统计日期',
    shareholder_type VARCHAR(50) COMMENT '股东类型（如产业资本、公募基金等）',
    holding_ratio DECIMAL(5,2) COMMENT '持股比例%',
    change_ratio DECIMAL(5,2) COMMENT '变动比例%（较上期）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_date_type (company_id, stat_date, shareholder_type),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股东结构表';

-- 股东户数表
CREATE TABLE IF NOT EXISTS shareholder_count (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    stat_date DATE NOT NULL COMMENT '统计日期',
    total_holders INT COMMENT '股东总人数',
    change DECIMAL(10,4) COMMENT '较上期变化（例如-0.0187表示-1.87%）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_date (company_id, stat_date),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股东户数表';

-- 研发投入表
CREATE TABLE IF NOT EXISTS rd_expense (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    revenue DECIMAL(15,2) COMMENT '主营收入（元）',
    rd_expense DECIMAL(15,2) COMMENT '研发费用（元）',
    rd_ratio DECIMAL(5,2) COMMENT '研发费用占比%',
    rd_growth DECIMAL(10,4) COMMENT '费用增长率%（如-0.121表示-12.1%）',
    rd_return DECIMAL(10,4) COMMENT '费用回报率%（可选）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year (company_id, year),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研发投入表';

-- 研发人员表
CREATE TABLE IF NOT EXISTS rd_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    year INT NOT NULL,
    staff_count INT COMMENT '研发人员规模',
    growth DECIMAL(10,4) COMMENT '同比增长（如0.3表示30%）',
    percent_of_total DECIMAL(5,2) COMMENT '占员工总数%',
    bachelor INT COMMENT '本科人数',
    master INT COMMENT '硕士人数',
    bachelor_master_ratio DECIMAL(5,2) COMMENT '本科+硕士占研发人员比例%',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_company_year (company_id, year),
    FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研发人员表';

-- 插入示例公司数据
INSERT INTO company (name, code, business, remark) VALUES
('长电科技', '600584', '集成电路封装测试', '半导体封测龙头'),
('华天科技', '002185', '集成电路封装测试', '国内封测三强之一'),
('通富微电', '002156', '集成电路封装测试', 'AMD核心封测伙伴'),
('中芯国际', '688981', '集成电路晶圆代工', '国内晶圆代工龙头'),
('北方华创', '002371', '半导体设备', '国产设备龙头');

-- 插入示例利润率数据
INSERT INTO profit_rate (company_id, year, gross_profit_margin, net_profit_margin) VALUES
(1, 2024, 18.52, 8.35),
(1, 2023, 17.85, 7.92),
(1, 2022, 16.23, 6.85),
(2, 2024, 16.78, 6.52),
(2, 2023, 15.92, 5.88),
(3, 2024, 15.35, 5.25),
(4, 2024, 22.15, 12.58),
(5, 2024, 38.65, 15.22);

-- 插入示例扣非净利润数据
INSERT INTO non_recurring (company_id, year, non_recurring_profit, non_recurring_growth) VALUES
(1, 2024, 25.85, 0.1523),
(1, 2023, 22.42, -0.0832),
(2, 2024, 8.52, 0.1256),
(3, 2024, 6.35, 0.0852),
(4, 2024, 45.62, 0.1856);

-- 插入示例ROE与净资产数据
INSERT INTO roe_net_asset (company_id, year, roe, net_asset_per_share) VALUES
(1, 2024, 12.58, 8.52),
(1, 2023, 11.25, 7.85),
(2, 2024, 8.52, 5.35),
(3, 2024, 7.85, 4.92),
(4, 2024, 6.52, 15.85),
(5, 2024, 15.25, 28.65);

-- 插入示例PE估值数据
INSERT INTO pe_valuation (company_id, year, pe_high, pe_mid, pe_low, eps, type, remark) VALUES
(1, 2024, 35.50, 28.50, 22.00, 1.25, 'actual', ''),
(1, 2025, 38.00, 30.00, 25.00, 1.45, 'forecast', '预测值'),
(2, 2024, 28.50, 22.50, 18.00, 0.85, 'actual', ''),
(3, 2024, 32.00, 26.50, 20.00, 0.95, 'actual', '');

-- 插入示例股东结构数据
INSERT INTO shareholder_structure (company_id, stat_date, shareholder_type, holding_ratio, change_ratio) VALUES
(1, '2024-06-30', '产业资本', 35.50, 2.10),
(1, '2024-06-30', '公募基金', 12.50, -1.50),
(1, '2024-06-30', '北向资金', 8.50, 0.80),
(2, '2024-06-30', '产业资本', 42.00, 1.50);

-- 插入示例股东户数数据
INSERT INTO shareholder_count (company_id, stat_date, total_holders, change) VALUES
(1, '2024-06-30', 125680, -0.0187),
(1, '2024-03-31', 128080, 0.0256),
(2, '2024-06-30', 85620, -0.0125),
(3, '2024-06-30', 68250, 0.0085);

-- 插入示例研发投入数据
INSERT INTO rd_expense (company_id, year, revenue, rd_expense, rd_ratio, rd_growth, rd_return) VALUES
(1, 2024, 2850000000, 125000000, 4.38, 0.1523, 0.1856),
(1, 2023, 2450000000, 108500000, 4.43, 0.0852, 0.1652),
(2, 2024, 1250000000, 62500000, 5.00, 0.1256, 0.1452),
(4, 2024, 4500000000, 850000000, 18.89, 0.1856, 0.2256),
(5, 2024, 1850000000, 285000000, 15.41, 0.2256, 0.2856);

-- 插入示例研发人员数据
INSERT INTO rd_staff (company_id, year, staff_count, growth, percent_of_total, bachelor, master, bachelor_master_ratio, remark) VALUES
(1, 2024, 2850, 0.125, 25.50, 1520, 850, 83.20, ''),
(1, 2023, 2535, 0.085, 24.20, 1350, 750, 82.80, ''),
(2, 2024, 1850, 0.095, 22.50, 980, 520, 81.20, ''),
(4, 2024, 4500, 0.185, 35.80, 2150, 1850, 88.90, ''),
(5, 2024, 3200, 0.225, 42.50, 1520, 1280, 87.50, '');
