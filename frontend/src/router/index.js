import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import ProfitRate from '../views/ProfitRate.vue'
import NonRecurring from '../views/NonRecurring.vue'
import RoeNetAsset from '../views/RoeNetAsset.vue'
import PeValuation from '../views/PeValuation.vue'
import ShareholderStructure from '../views/ShareholderStructure.vue'
import ShareholderCount from '../views/ShareholderCount.vue'
import RdExpense from '../views/RdExpense.vue'
import RdStaff from '../views/RdStaff.vue'
import CompanyManage from '../views/CompanyManage.vue'
import DataImport from '../views/DataImport.vue'
import ModuleManage from '../views/ModuleManage.vue'
import CustomModuleView from '../views/CustomModuleView.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/profit-rate',
    children: [
      {
        path: 'profit-rate',
        name: 'ProfitRate',
        component: ProfitRate,
        meta: { title: '毛利率与净利率', icon: 'TrendCharts' }
      },
      {
        path: 'non-recurring',
        name: 'NonRecurring',
        component: NonRecurring,
        meta: { title: '扣非净利润增长', icon: 'Money' }
      },
      {
        path: 'roe-net-asset',
        name: 'RoeNetAsset',
        component: RoeNetAsset,
        meta: { title: 'ROE与净资产', icon: 'Wallet' }
      },
      {
        path: 'pe-valuation',
        name: 'PeValuation',
        component: PeValuation,
        meta: { title: 'PE估值', icon: 'DataAnalysis' }
      },
      {
        path: 'shareholder-structure',
        name: 'ShareholderStructure',
        component: ShareholderStructure,
        meta: { title: '股东结构', icon: 'UserFilled' }
      },
      {
        path: 'shareholder-count',
        name: 'ShareholderCount',
        component: ShareholderCount,
        meta: { title: '股东户数', icon: 'User' }
      },
      {
        path: 'rd-expense',
        name: 'RdExpense',
        component: RdExpense,
        meta: { title: '研发投入', icon: 'Coin' }
      },
      {
        path: 'rd-staff',
        name: 'RdStaff',
        component: RdStaff,
        meta: { title: '研发团队', icon: 'Avatar' }
      },
      {
        path: 'companies',
        name: 'CompanyManage',
        component: CompanyManage,
        meta: { title: '公司管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'data-import',
        name: 'DataImport',
        component: DataImport,
        meta: { title: '数据导入', icon: 'UploadFilled' }
      },
      {
        path: 'module-manage',
        name: 'ModuleManage',
        component: ModuleManage,
        meta: { title: '模块管理', icon: 'Grid' }
      },
      {
        path: 'module/:moduleCode',
        name: 'CustomModule',
        component: CustomModuleView,
        meta: { title: '自定义模块', icon: 'Grid' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
