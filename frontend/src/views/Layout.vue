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
        <el-menu-item v-for="route in routes" :key="route.path" :index="route.path">
          <el-icon size="22">
            <component :is="route.meta.icon" />
          </el-icon>
          <span class="menu-text">{{ route.meta.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <div class="page-icon">
            <el-icon size="24" color="#409EFF">
              <component :is="$route.meta.icon" />
            </el-icon>
          </div>
          <div class="header-title">{{ $route.meta.title }}</div>
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const routes = computed(() => {
  return router.getRoutes()
    .find(r => r.path === '/')
    ?.children || []
})

const goToCompanyManage = () => {
  router.push('/companies')
}
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
