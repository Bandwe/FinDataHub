import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'

const ProfitRate = () => import('../views/ProfitRate.vue')
const NonRecurring = () => import('../views/NonRecurring.vue')
const RoeNetAsset = () => import('../views/RoeNetAsset.vue')
const PeValuation = () => import('../views/PeValuation.vue')
const ShareholderStructure = () => import('../views/ShareholderStructure.vue')
const ShareholderCount = () => import('../views/ShareholderCount.vue')
const RdExpense = () => import('../views/RdExpense.vue')
const RdStaff = () => import('../views/RdStaff.vue')
const CompanyManage = () => import('../views/CompanyManage.vue')
const DataImport = () => import('../views/DataImport.vue')
const ModuleManage = () => import('../views/ModuleManage.vue')
const CustomModuleView = () => import('../views/CustomModuleView.vue')

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
        meta: { title: '行业模板', icon: 'Grid' }
      },
      {
        path: 'module/:moduleCode',
        name: 'CustomModule',
        component: CustomModuleView,
        meta: { title: '行业数据', icon: 'Grid' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
