<template>
  <el-container class="layout-container">
    <el-aside width="260px" class="sidebar">
      <div class="logo">
        <div class="logo-icon-wrapper">
          <el-icon size="36" color="#409EFF"><DataAnalysis /></el-icon>
        </div>
        <span class="logo-text">FinDataHub</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        background-color="#2b3a4f"
        text-color="#b8c7ce"
        active-text-color="#fff"
      >
        <!-- 固定路由菜单 -->
        <el-menu-item v-for="item in staticMenuItems" :key="item.path" :index="item.path">
          <el-icon size="22">
            <component :is="item.icon" />
          </el-icon>
          <span class="menu-text">{{ item.title }}</span>
        </el-menu-item>
        
        <!-- 自定义模块菜单 -->
        <el-menu-item 
          v-for="module in customModules" 
          :key="'/module/' + module.code" 
          :index="'/module/' + module.code"
        >
          <el-icon size="22">
            <component :is="module.icon" />
          </el-icon>
          <span class="menu-text">{{ module.name }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <div class="page-icon">
            <el-icon size="24" color="#409EFF">
              <component :is="currentIcon" />
            </el-icon>
          </div>
          <div class="header-title">{{ currentTitle }}</div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="goToCompanyManage" class="action-btn">
            <el-icon><OfficeBuilding /></el-icon>
            公司管理
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataAnalysis, TrendCharts, Money, Wallet,
  UserFilled, User, Coin, Avatar, OfficeBuilding,
  UploadFilled, Grid
} from '@element-plus/icons-vue'
import { getCustomModules } from '../api/customModule'

const route = useRoute()
const router = useRouter()

// 自定义模块列表
const customModules = ref([])

// 静态菜单项（避免使用计算属性动态获取路由）
const staticMenuItems = [
  { path: '/profit-rate', title: '毛利率与净利率', icon: 'TrendCharts' },
  { path: '/non-recurring', title: '扣非净利润增长', icon: 'Money' },
  { path: '/roe-net-asset', title: 'ROE与净资产', icon: 'Wallet' },
  { path: '/pe-valuation', title: 'PE估值', icon: 'DataAnalysis' },
  { path: '/shareholder-structure', title: '股东结构', icon: 'UserFilled' },
  { path: '/shareholder-count', title: '股东户数', icon: 'User' },
  { path: '/rd-expense', title: '研发投入', icon: 'Coin' },
  { path: '/rd-staff', title: '研发团队', icon: 'Avatar' },
  { path: '/companies', title: '公司管理', icon: 'OfficeBuilding' },
  { path: '/data-import', title: '数据导入', icon: 'UploadFilled' },
  { path: '/module-manage', title: '模块管理', icon: 'Grid' }
]

// 当前页面图标
const currentIcon = computed(() => {
  // 如果是自定义模块路由
  if (route.path.startsWith('/module/')) {
    const moduleCode = route.params.moduleCode
    const module = customModules.value.find(m => m.code === moduleCode)
    return module?.icon || 'Grid'
  }
  // 固定路由
  const menuItem = staticMenuItems.find(item => item.path === route.path)
  return menuItem?.icon || 'Grid'
})

// 当前页面标题
const currentTitle = computed(() => {
  // 如果是自定义模块路由
  if (route.path.startsWith('/module/')) {
    const moduleCode = route.params.moduleCode
    const module = customModules.value.find(m => m.code === moduleCode)
    return module?.name || '自定义模块'
  }
  // 固定路由
  const menuItem = staticMenuItems.find(item => item.path === route.path)
  return menuItem?.title || ''
})

// 获取自定义模块列表
const fetchCustomModules = async () => {
  try {
    const modules = await getCustomModules()
    customModules.value = modules || []
  } catch (error) {
    console.error('获取自定义模块失败:', error)
  }
}

const goToCompanyManage = () => {
  router.push('/companies')
}

onMounted(() => {
  fetchCustomModules()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #2b3a4f 0%, #1f2d3d 100%);
  color: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  border-right: none;
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.logo-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.sidebar-menu {
  border-right: none;
  padding-top: 12px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 260px;
}

.sidebar-menu .el-menu-item {
  height: 56px;
  line-height: 56px;
  margin: 4px 12px;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(64, 158, 255, 0.15) !important;
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, #409EFF 0%, #337ecc 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 14px;
  vertical-align: middle;
}

.menu-text {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.header {
  background: linear-gradient(90deg, #fff 0%, #f8fafc 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 68px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  border-radius: 12px;
  border: 2px solid #409EFF;
}

.header-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2d3d;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35);
}

.main-content {
  background: linear-gradient(180deg, #f0f2f5 0%, #e8eaed 100%);
  padding: 28px;
  overflow-y: auto;
}
</style>