export const fixedFinancialModules = {
  profit_rate: { title: '毛利率与净利率', route: '/profit-rate', icon: 'TrendCharts' },
  non_recurring: { title: '扣非净利润增长', route: '/non-recurring', icon: 'Money' },
  roe_net_asset: { title: 'ROE与净资产', route: '/roe-net-asset', icon: 'Wallet' },
  pe_valuation: { title: 'PE估值', route: '/pe-valuation', icon: 'DataAnalysis' },
  shareholder_structure: { title: '股东结构', route: '/shareholder-structure', icon: 'UserFilled' },
  shareholder_count: { title: '股东户数', route: '/shareholder-count', icon: 'User' },
  rd_expense: { title: '研发投入', route: '/rd-expense', icon: 'Coin' },
  rd_staff: { title: '研发团队', route: '/rd-staff', icon: 'Avatar' }
}

export const fixedModuleOptions = Object.fromEntries(
  Object.entries(fixedFinancialModules).map(([key, value]) => [key, value.title])
)

export const fixedModuleMenuItems = Object.values(fixedFinancialModules).map(item => ({
  path: item.route,
  title: item.title,
  icon: item.icon
}))
