<template>
  <div class="template-manage">
    <el-card class="template-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Grid /></el-icon>
            <span class="header-title">行业模板管理</span>
          </div>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增行业
          </el-button>
        </div>
      </template>

      <el-alert
        title="行业模板说明"
        type="info"
        description="每个行业对应一套固定字段。草稿模板可以编辑字段，确认模板后字段锁定，并会出现在左侧菜单中用于录入、导入和分析数据。"
        show-icon
        :closable="false"
        class="template-info"
      />

      <el-table :data="templates" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="行业名称" min-width="160">
          <template #default="{ row }">
            <div class="name-cell">
              <el-icon><component :is="row.icon || 'Grid'" /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="行业代码" width="150" />
        <el-table-column prop="version" label="版本" width="80" align="center" />
        <el-table-column label="状态" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_locked ? 'success' : 'warning'">
              {{ row.is_locked ? '已确认' : '草稿' }}
            </el-tag>
            <el-tag v-if="!row.is_active" type="info" class="status-tag">停用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="字段" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.keywords?.length || 0 }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="390" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                {{ row.is_locked ? '查看' : '编辑' }}
              </el-button>
              <el-button v-if="!row.is_locked" type="success" size="small" @click="handleConfirm(row)">
                <el-icon><CircleCheck /></el-icon>
                确认
              </el-button>
              <el-button v-if="row.is_locked" type="warning" size="small" @click="handleClone(row)">
                <el-icon><Document /></el-icon>
                复制版本
              </el-button>
              <el-button v-if="row.is_locked && row.is_active" type="info" size="small" @click="handleDownload(row)">
                <el-icon><Download /></el-icon>
                模板
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                {{ row.is_active ? '停用/删' : '删除' }}
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="860px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="行业名称" prop="name">
              <el-input v-model="form.name" placeholder="例如：半导体设备" :disabled="form.is_locked" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行业代码" prop="code">
              <el-input
                v-model="form.code"
                placeholder="例如：semiconductor_equipment"
                :disabled="isEdit || form.is_locked"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="图标">
              <el-select v-model="form.icon" style="width: 100%" :disabled="form.is_locked">
                <el-option v-for="icon in iconOptions" :key="icon" :label="icon" :value="icon" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" :disabled="form.is_locked" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="说明该行业模板的适用范围" :disabled="form.is_locked" />
        </el-form-item>

        <el-form-item label="启用">
          <el-switch v-model="form.is_active" :disabled="form.is_locked" />
        </el-form-item>
      </el-form>

      <div class="field-header">
        <div>
          <span class="field-title">模板字段</span>
          <el-tag v-if="form.is_locked" type="success" class="status-tag">字段已锁定</el-tag>
          <el-tag v-else type="warning" class="status-tag">草稿可编辑</el-tag>
        </div>
        <el-button type="primary" size="small" :disabled="form.is_locked" @click="addField">
          <el-icon><Plus /></el-icon>
          添加字段
        </el-button>
      </div>

      <el-table :data="form.fields" border size="small" class="field-table">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="字段代码" min-width="170">
          <template #default="{ row }">
            <el-input v-model="row.keyword" size="small" :disabled="form.is_locked" placeholder="english_key" />
          </template>
        </el-table-column>
        <el-table-column label="显示名称" min-width="170">
          <template #default="{ row }">
            <el-input v-model="row.label" size="small" :disabled="form.is_locked" placeholder="中文字段名" />
          </template>
        </el-table-column>
        <el-table-column label="类型" width="130">
          <template #default="{ row }">
            <el-select v-model="row.data_type" size="small" :disabled="form.is_locked">
              <el-option label="文本" value="string" />
              <el-option label="数字" value="number" />
              <el-option label="日期" value="date" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_required" size="small" :disabled="form.is_locked" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link :disabled="form.is_locked" @click="removeField($index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="!form.is_locked" type="primary" :loading="saving" @click="handleSave">保存草稿</el-button>
        <el-button v-if="isEdit && !form.is_locked" type="success" :loading="saving" @click="handleSaveAndConfirm">
          保存并确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Plus, Edit, Delete, CircleCheck, Document, Download } from '@element-plus/icons-vue'
import {
  cloneIndustryTemplate,
  confirmIndustryTemplate,
  createIndustryTemplate,
  deleteIndustryTemplate,
  downloadIndustryTemplate,
  getAllIndustryTemplates,
  updateIndustryTemplate
} from '../api/industryTemplate'

const loading = ref(false)
const saving = ref(false)
const templates = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formRef = ref(null)

const iconOptions = ['Grid', 'DataAnalysis', 'TrendCharts', 'Money', 'Wallet', 'OfficeBuilding', 'Document']

const form = reactive({
  id: null,
  name: '',
  code: '',
  icon: 'Grid',
  description: '',
  sort_order: 0,
  is_active: true,
  is_locked: false,
  fields: []
})

const rules = {
  name: [{ required: true, message: '请输入行业名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入行业代码', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9_]*$/, message: '代码必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ]
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    code: '',
    icon: 'Grid',
    description: '',
    sort_order: templates.value.length,
    is_active: true,
    is_locked: false,
    fields: []
  })
}

const fetchTemplates = async () => {
  loading.value = true
  try {
    templates.value = await getAllIndustryTemplates()
  } catch (error) {
    console.error(error)
    ElMessage.error('获取行业模板失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增行业模板'
  resetForm()
  addField()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = row.is_locked ? '查看行业模板' : '编辑行业模板'
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    icon: row.icon || 'Grid',
    description: row.description || '',
    sort_order: row.sort_order || 0,
    is_active: row.is_active,
    is_locked: row.is_locked,
    fields: (row.keywords || []).map((field, index) => ({
      keyword: field.keyword,
      label: field.label,
      data_type: field.data_type || 'string',
      is_required: !!field.is_required,
      sort_order: field.sort_order ?? index
    }))
  })
  dialogVisible.value = true
}

const addField = () => {
  form.fields.push({
    keyword: '',
    label: '',
    data_type: 'string',
    is_required: false,
    sort_order: form.fields.length
  })
}

const removeField = (index) => {
  form.fields.splice(index, 1)
}

const payload = () => ({
  name: form.name,
  code: form.code,
  icon: form.icon,
  description: form.description,
  sort_order: form.sort_order,
  is_active: form.is_active,
  ...(form.is_locked ? {} : {
    fields: form.fields
      .filter((field) => field.keyword.trim() || field.label.trim())
      .map((field, index) => ({
        ...field,
        keyword: field.keyword.trim(),
        label: field.label.trim(),
        sort_order: index
      }))
  })
})

const saveTemplate = async () => {
  if (form.is_locked) return null
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return null
  saving.value = true
  try {
    const saved = isEdit.value
      ? await updateIndustryTemplate(form.id, payload())
      : await createIndustryTemplate(payload())
    ElMessage.success('保存成功')
    isEdit.value = true
    form.id = saved.id
    return saved
  } catch (error) {
    console.error(error)
    ElMessage.error(error.message || '保存失败')
    return null
  } finally {
    saving.value = false
  }
}

const handleSave = async () => {
  const saved = await saveTemplate()
  if (!saved) return
  dialogVisible.value = false
  fetchTemplates()
}

const handleSaveAndConfirm = async () => {
  const saved = await saveTemplate()
  if (!saved) return
  await handleConfirm(saved, false)
  dialogVisible.value = false
  fetchTemplates()
}

const handleConfirm = async (row, refresh = true) => {
  try {
    await ElMessageBox.confirm('确认后字段将锁定，后续需要复制新版本才能调整字段。确定确认模板吗？', '确认模板', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await confirmIndustryTemplate(row.id)
    ElMessage.success('模板已确认')
    if (refresh) fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(error.message || '确认失败')
    }
  }
}

const handleClone = async (row) => {
  try {
    const code = `${row.code}_v${(row.version || 1) + 1}`
    await cloneIndustryTemplate(row.id, { code })
    ElMessage.success('已复制为新草稿版本')
    fetchTemplates()
  } catch (error) {
    console.error(error)
    ElMessage.error(error.message || '复制失败')
  }
}

const handleDownload = async (row) => {
  try {
    const blob = await downloadIndustryTemplate(row.code)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${row.code}_template.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error(error)
    ElMessage.error('下载模板失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定处理行业模板 "${row.name}" 吗？已有数据的模板会被停用，未录入数据的模板会被删除。`,
      '停用或删除模板',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteIndustryTemplate(row.id)
    ElMessage.success('操作成功')
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(error.message || '操作失败')
    }
  }
}

onMounted(fetchTemplates)
</script>

<style scoped>
.template-manage {
  padding: 20px;
}

.template-card {
  max-width: 1480px;
  margin: 0 auto;
}

.card-header,
.header-left,
.name-cell,
.field-header {
  display: flex;
  align-items: center;
}

.card-header,
.field-header {
  justify-content: space-between;
}

.header-left,
.name-cell {
  gap: 10px;
}

.header-icon {
  color: #409EFF;
  font-size: 22px;
}

.header-title,
.field-title {
  font-size: 18px;
  font-weight: 600;
}

.template-info {
  margin-bottom: 18px;
}

.status-tag {
  margin-left: 8px;
}

.field-header {
  margin: 12px 0;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.field-table {
  margin-top: 8px;
}
</style>
