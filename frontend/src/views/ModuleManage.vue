<template>
  <div class="module-manage-container">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Grid /></el-icon>
            <span class="header-title">自定义模块管理</span>
          </div>
          <el-button type="primary" @click="handleAddModule">
            <el-icon><Plus /></el-icon>
            新增模块
          </el-button>
        </div>
      </template>

      <el-alert
        title="模块管理说明"
        type="info"
        description="您可以在此添加、编辑或删除自定义模块。每个模块创建后会自动生成默认的表格关键词，您可以在关键词配置中进行自定义。"
        show-icon
        :closable="false"
        class="module-info"
      />

      <el-table
        :data="moduleList"
        border
        stripe
        v-loading="loading"
        class="module-table"
      >
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="模块名称" min-width="150">
          <template #default="{ row }">
            <div class="module-name-cell">
              <el-icon class="module-icon"><component :is="row.icon" /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="模块代码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="keywords" label="关键词数量" width="120" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.keywords?.length || 0 }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="100" align="center" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" size="small" @click="handleEditKeywords(row)">
                <el-icon><Setting /></el-icon>
                关键词
              </el-button>
              <el-button type="warning" size="small" @click="handleEditModule(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDeleteModule(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑模块对话框 -->
    <el-dialog
      v-model="moduleDialogVisible"
      :title="isEdit ? '编辑模块' : '新增模块'"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="moduleFormRef"
        :model="moduleForm"
        :rules="moduleRules"
        label-width="100px"
      >
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="模块代码" prop="code">
          <el-input
            v-model="moduleForm.code"
            placeholder="请输入模块代码（英文）"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="模块图标" prop="icon">
          <el-select v-model="moduleForm.icon" placeholder="请选择图标" style="width: 100%">
            <el-option
              v-for="icon in iconOptions"
              :key="icon.value"
              :label="icon.label"
              :value="icon.value"
            >
              <div class="icon-option">
                <el-icon><component :is="icon.value" /></el-icon>
                <span>{{ icon.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模块描述" prop="description">
          <el-input
            v-model="moduleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模块描述"
          />
        </el-form-item>
        <el-form-item label="排序顺序" prop="sort_order">
          <el-input-number v-model="moduleForm.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="moduleForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveModule" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 关键词配置对话框 -->
    <el-dialog
      v-model="keywordDialogVisible"
      title="表格关键词配置"
      width="700px"
      destroy-on-close
    >
      <div class="keyword-header">
        <div class="keyword-info">
          <span class="module-title">{{ currentModule?.name }}</span>
          <span class="module-code">({{ currentModule?.code }})</span>
        </div>
        <el-button type="primary" size="small" @click="handleAddKeyword">
          <el-icon><Plus /></el-icon>
          添加关键词
        </el-button>
      </div>

      <el-table
        :data="keywordList"
        border
        stripe
        size="small"
        class="keyword-table"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="keyword" label="关键词" width="150">
          <template #default="{ row }">
            <el-input v-if="row.isEditing" v-model="row.keyword" size="small" />
            <span v-else>{{ row.keyword }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="label" label="显示标签" width="150">
          <template #default="{ row }">
            <el-input v-if="row.isEditing" v-model="row.label" size="small" />
            <span v-else>{{ row.label }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="data_type" label="数据类型" width="120">
          <template #default="{ row }">
            <el-select v-if="row.isEditing" v-model="row.data_type" size="small">
              <el-option label="字符串" value="string" />
              <el-option label="数字" value="number" />
              <el-option label="日期" value="date" />
            </el-select>
            <el-tag v-else :type="getDataTypeTag(row.data_type)">
              {{ getDataTypeLabel(row.data_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_required" label="必填" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-if="row.isEditing" v-model="row.is_required" size="small" />
            <el-icon v-else :color="row.is_required ? '#67C23A' : '#909399'">
              <CircleCheck v-if="row.is_required" />
              <CircleClose v-else />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row, $index }">
            <template v-if="row.isEditing">
              <el-button type="success" size="small" @click="handleSaveKeyword(row)">
                保存
              </el-button>
              <el-button size="small" @click="handleCancelEdit(row, $index)">
                取消
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="small" @click="handleEditKeyword(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" size="small" @click="handleDeleteKeyword(row, $index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="keywordDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid, Plus, Edit, Delete, Setting,
  CircleCheck, CircleClose, TrendCharts, Money,
  Wallet, DataAnalysis, UserFilled, User, Coin,
  Avatar, OfficeBuilding, UploadFilled, Document,
  Folder, FolderOpened, Files, List, Memo,
  Collection, Notebook, Calendar, Timer, Watch,
  AlarmClock, FirstAidKit, Box, Goods, Shop,
  Sell, ShoppingBag, ShoppingCart, Present, Trophy,
  Medal, WarningFilled, CircleCheckFilled
} from '@element-plus/icons-vue'
import {
  getAllModules, createCustomModule, updateCustomModule, deleteCustomModule
} from '../api/customModule'
import {
  getModuleKeywords, createModuleKeyword, updateModuleKeyword,
  deleteModuleKeyword, batchUpdateKeywords
} from '../api/customModule'

const loading = ref(false)
const saveLoading = ref(false)
const moduleList = ref([])
const moduleDialogVisible = ref(false)
const keywordDialogVisible = ref(false)
const isEdit = ref(false)
const currentModule = ref(null)
const keywordList = ref([])

const moduleFormRef = ref(null)
const moduleForm = reactive({
  name: '',
  code: '',
  icon: 'Grid',
  description: '',
  sort_order: 0,
  is_active: true
})

const moduleRules = {
  name: [{ required: true, message: '请输入模块名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入模块代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '代码必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  icon: [{ required: true, message: '请选择图标', trigger: 'change' }]
}

const iconOptions = [
  { value: 'Grid', label: '网格' },
  { value: 'TrendCharts', label: '趋势图' },
  { value: 'Money', label: '货币' },
  { value: 'Wallet', label: '钱包' },
  { value: 'DataAnalysis', label: '数据分析' },
  { value: 'UserFilled', label: '用户(填充)' },
  { value: 'User', label: '用户' },
  { value: 'Coin', label: '硬币' },
  { value: 'Avatar', label: '头像' },
  { value: 'OfficeBuilding', label: '办公楼' },
  { value: 'UploadFilled', label: '上传' },
  { value: 'Document', label: '文档' },
  { value: 'Folder', label: '文件夹' },
  { value: 'FolderOpened', label: '打开的文件夹' },
  { value: 'Files', label: '文件' },
  { value: 'List', label: '列表' },
  { value: 'Memo', label: '备忘录' },
  { value: 'Collection', label: '集合' },
  { value: 'Notebook', label: '笔记本' },
  { value: 'Calendar', label: '日历' },
  { value: 'Timer', label: '计时器' },
  { value: 'Watch', label: '手表' },
  { value: 'AlarmClock', label: '闹钟' },
  { value: 'FirstAidKit', label: '急救箱' },
  { value: 'Box', label: '盒子' },
  { value: 'Goods', label: '商品' },
  { value: 'Shop', label: '商店' },
  { value: 'Sell', label: '销售' },
  { value: 'ShoppingBag', label: '购物袋' },
  { value: 'ShoppingCart', label: '购物车' },
  { value: 'Present', label: '礼物' },
  { value: 'Trophy', label: '奖杯' },
  { value: 'Medal', label: '奖牌' },
  { value: 'WarningFilled', label: '警告' }
]

const fetchModules = async () => {
  loading.value = true
  try {
    const data = await getAllModules()
    moduleList.value = data || []
  } catch (error) {
    console.error('获取模块列表失败:', error)
    ElMessage.error('获取模块列表失败')
  } finally {
    loading.value = false
  }
}

const handleAddModule = () => {
  isEdit.value = false
  Object.assign(moduleForm, {
    name: '',
    code: '',
    icon: 'Grid',
    description: '',
    sort_order: moduleList.value.length,
    is_active: true
  })
  moduleDialogVisible.value = true
}

const handleEditModule = (row) => {
  isEdit.value = true
  Object.assign(moduleForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    icon: row.icon,
    description: row.description,
    sort_order: row.sort_order,
    is_active: row.is_active
  })
  moduleDialogVisible.value = true
}

const handleSaveModule = async () => {
  const valid = await moduleFormRef.value.validate().catch(() => false)
  if (!valid) return

  saveLoading.value = true
  try {
    if (isEdit.value) {
      await updateCustomModule(moduleForm.id, moduleForm)
      ElMessage.success('更新成功')
    } else {
      await createCustomModule(moduleForm)
      ElMessage.success('创建成功')
    }
    moduleDialogVisible.value = false
    fetchModules()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saveLoading.value = false
  }
}

const handleDeleteModule = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模块 "${row.name}" 吗？此操作将同时删除该模块的所有关键词配置。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteCustomModule(row.id)
    ElMessage.success('删除成功')
    fetchModules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleStatusChange = async (row, val) => {
  try {
    await updateCustomModule(row.id, { is_active: val })
    ElMessage.success(val ? '模块已启用' : '模块已禁用')
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
    row.is_active = !val
  }
}

const handleEditKeywords = async (row) => {
  currentModule.value = row
  keywordDialogVisible.value = true
  await fetchKeywords(row.id)
}

const fetchKeywords = async (moduleId) => {
  try {
    const data = await getModuleKeywords(moduleId)
    keywordList.value = (data || []).map(k => ({ ...k, isEditing: false }))
  } catch (error) {
    console.error('获取关键词失败:', error)
    ElMessage.error('获取关键词失败')
  }
}

const handleAddKeyword = () => {
  const newKeyword = {
    id: null,
    keyword: '',
    label: '',
    data_type: 'string',
    is_required: false,
    sort_order: keywordList.value.length,
    isEditing: true,
    isNew: true
  }
  keywordList.value.push(newKeyword)
}

const handleEditKeyword = (row) => {
  row.isEditing = true
  row._original = { ...row }
}

const handleSaveKeyword = async (row) => {
  if (!row.keyword || !row.label) {
    ElMessage.warning('关键词和显示标签不能为空')
    return
  }

  try {
    const data = {
      keyword: row.keyword,
      label: row.label,
      data_type: row.data_type,
      is_required: row.is_required,
      sort_order: row.sort_order
    }

    if (row.isNew) {
      await createModuleKeyword(currentModule.value.id, data)
      ElMessage.success('添加成功')
    } else {
      await updateModuleKeyword(currentModule.value.id, row.id, data)
      ElMessage.success('更新成功')
    }

    row.isEditing = false
    row.isNew = false
    delete row._original
    await fetchKeywords(currentModule.value.id)
  } catch (error) {
    console.error('保存关键词失败:', error)
    ElMessage.error(error.message || '保存失败')
  }
}

const handleCancelEdit = (row, index) => {
  if (row.isNew) {
    keywordList.value.splice(index, 1)
  } else {
    Object.assign(row, row._original)
    row.isEditing = false
    delete row._original
  }
}

const handleDeleteKeyword = async (row, index) => {
  if (row.isNew) {
    keywordList.value.splice(index, 1)
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除关键词 "${row.label}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteModuleKeyword(currentModule.value.id, row.id)
    ElMessage.success('删除成功')
    keywordList.value.splice(index, 1)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除关键词失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const getDataTypeTag = (type) => {
  const map = { string: '', number: 'success', date: 'warning' }
  return map[type] || ''
}

const getDataTypeLabel = (type) => {
  const map = { string: '字符串', number: '数字', date: '日期' }
  return map[type] || type
}

onMounted(() => {
  fetchModules()
})
</script>

<style scoped>
.module-manage-container {
  padding: 20px;
}

.module-card {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 22px;
  color: #409EFF;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.module-info {
  margin-bottom: 20px;
}

.module-table {
  margin-top: 10px;
}

.module-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-icon {
  font-size: 18px;
  color: #409EFF;
}

.icon-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.keyword-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #EBEEF5;
}

.keyword-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.module-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.module-code {
  font-size: 14px;
  color: #909399;
}

.keyword-table {
  margin-top: 10px;
}
</style>