<template>
  <div class="module-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="个股名称/代码" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>{{ moduleInfo?.name || '自定义模块' }}数据</span>
          <div class="table-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>新增
            </el-button>
            <el-button type="success" @click="handleImport">
              <el-icon><Upload /></el-icon>导入
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon><Download /></el-icon>导出
            </el-button>
            <el-button type="info" @click="handleCompare">
              <el-icon><DataLine /></el-icon>
              公司对比
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="company_code" label="代码" width="100" />
        <el-table-column prop="company_name" label="个股名称" width="150" />
        <el-table-column prop="year" label="年份" width="80" />
        
        <!-- 动态生成列 -->
        <el-table-column
          v-for="keyword in moduleKeywords"
          :key="keyword.keyword"
          :prop="keyword.keyword"
          :label="keyword.label"
          min-width="120"
        >
          <template #default="{ row }">
            <span v-if="keyword.data_type === 'number' && row[keyword.keyword] !== undefined">
              {{ formatNumber(row[keyword.keyword]) }}
            </span>
            <span v-else>{{ row[keyword.keyword] }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 数据可视化图表 -->
    <el-card class="chart-card">
      <template #header>
        <div class="chart-header">
          <span>数据可视化</span>
          <div class="chart-controls">
            <el-select v-model="chartConfig.metric" placeholder="选择指标" size="small" @change="updateChart">
              <el-option
                v-for="keyword in numberKeywords"
                :key="keyword.keyword"
                :label="keyword.label"
                :value="keyword.keyword"
              />
            </el-select>
            <el-select v-model="chartConfig.type" placeholder="图表类型" size="small" @change="updateChart">
              <el-option label="折线图" value="line" />
              <el-option label="柱状图" value="bar" />
            </el-select>
            <el-button type="success" @click="exportChart" style="margin-left: 10px">
              <el-icon><Download /></el-icon>
              导出图表
            </el-button>
          </div>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" label-width="120px">
        <el-form-item label="公司" required>
          <div style="display: flex; gap: 10px; align-items: center;">
            <el-select
              v-model="formData.company_id"
              filterable
              placeholder="选择公司"
              allow-create
              default-first-option
              @change="handleCompanyChange"
              style="flex: 1;"
            >
              <el-option
                v-for="company in companies"
                :key="company.id"
                :label="`${company.code} - ${company.name}`"
                :value="company.id"
              />
            </el-select>
            <el-button type="primary" @click="showAddCompanyDialog">
              <el-icon><Plus /></el-icon>
              新增公司
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="年份" required>
          <el-input-number v-model="formData.year" :min="2000" :max="2100" />
        </el-form-item>
        
        <!-- 动态生成表单字段 -->
        <el-form-item
          v-for="keyword in moduleKeywords"
          :key="keyword.keyword"
          :label="keyword.label"
          :required="keyword.is_required"
        >
          <el-input
            v-if="keyword.data_type === 'string'"
            v-model="formData[keyword.keyword]"
            :placeholder="`请输入${keyword.label}`"
          />
          <el-input-number
            v-else-if="keyword.data_type === 'number'"
            v-model="formData[keyword.keyword]"
            :placeholder="`请输入${keyword.label}`"
            style="width: 100%"
          />
          <el-date-picker
            v-else-if="keyword.data_type === 'date'"
            v-model="formData[keyword.keyword]"
            type="date"
            :placeholder="`请选择${keyword.label}`"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增公司对话框 -->
    <el-dialog v-model="addCompanyDialogVisible" title="新增公司" width="500px">
      <el-form ref="companyFormRef" :model="companyFormData" :rules="companyFormRules" label-width="100px">
        <el-form-item label="个股名称" prop="name">
          <el-input
            v-model="companyFormData.name"
            placeholder="请输入个股名称"
            maxlength="50"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item label="代码" prop="code">
          <el-input
            v-model="companyFormData.code"
            placeholder="请输入代码（如：600584）"
            maxlength="20"
            clearable
          />
          <div class="form-tip">支持 A 股（6 位数字）、港股、美股等代码格式</div>
        </el-form-item>
        <el-form-item label="主营业务">
          <el-input
            v-model="companyFormData.business"
            type="textarea"
            rows="2"
            placeholder="请输入主营业务（选填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="companyFormData.remark"
            type="textarea"
            rows="2"
            placeholder="请输入备注（选填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCompanyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddCompanySubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入数据" width="500px">
      <el-upload
        ref="uploadRef"
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">
            请上传 Excel 文件，文件需包含以下列：代码、个股名称、年份
            <br>
            以及模块自定义字段：{{ moduleKeywords.map(k => k.label).join('、') }}
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">导入</el-button>
      </template>
    </el-dialog>

    <!-- 公司对比对话框 -->
    <CompanyCompareDialog
      v-model="compareDialogVisible"
      :module-type="moduleCode"
      :fetch-module-data="fetchCompareData"
      :metrics="compareMetrics"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Upload, Download, DataLine } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getCustomModules } from '../api/customModule'
import {
  getCustomModuleData,
  createCustomModuleData,
  updateCustomModuleData,
  deleteCustomModuleData,
  exportCustomModuleData,
  importCustomModuleData,
  compareCustomModuleData
} from '../api/customModuleData'
import { getAllCompanies } from '../api/company'
import request from '../api/request'
import CompanyCompareDialog from '../components/CompanyCompareDialog.vue'

const route = useRoute()

// 模块信息
const moduleInfo = ref(null)
const moduleKeywords = ref([])
const moduleCode = computed(() => route.params.moduleCode)

// 搜索和表格
const searchForm = reactive({ keyword: '' })
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

// 公司列表
const companies = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const importDialogVisible = ref(false)
const compareDialogVisible = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  company_id: null,
  year: new Date().getFullYear(),
  new_company_name: ''
})

// 新增公司对话框
const addCompanyDialogVisible = ref(false)
const companyFormRef = ref(null)
const submitting = ref(false)
const companyFormData = reactive({ name: '', code: '', business: '', remark: '' })
const companyFormRules = {
  name: [
    { required: true, message: '请输入个股名称', trigger: 'blur' },
    { min: 1, max: 50, message: '个股名称长度不能超过 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入代码', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]{1,20}$/, message: '代码格式不正确，支持 1-20 位字母或数字', trigger: 'blur' }
  ]
}

// 导入
const uploadRef = ref(null)
const importFile = ref(null)
const importLoading = ref(false)

// 图表
const chartRef = ref(null)
let chartInstance = null
const chartConfig = reactive({ metric: '', type: 'line' })

// 数字类型的关键词（用于图表）
const numberKeywords = computed(() => {
  return moduleKeywords.value.filter(k => k.data_type === 'number')
})

// 对比指标
const compareMetrics = computed(() => {
  return moduleKeywords.value.map(k => ({ key: k.keyword, label: k.label }))
})

// 获取模块信息
const fetchModuleInfo = async () => {
  try {
    const modules = await getCustomModules()
    const module = modules.find(m => m.code === moduleCode.value)
    if (module) {
      moduleInfo.value = module
      moduleKeywords.value = module.keywords || []
      // 设置默认图表指标
      if (numberKeywords.value.length > 0) {
        chartConfig.metric = numberKeywords.value[0].keyword
      }
      // 初始化表单字段
      moduleKeywords.value.forEach(kw => {
        formData[kw.keyword] = kw.data_type === 'number' ? 0 : ''
      })
    }
  } catch (error) {
    console.error('获取模块信息失败:', error)
    ElMessage.error('获取模块信息失败')
  }
}

// 获取数据列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getCustomModuleData(moduleCode.value, {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword
    })
    tableData.value = res.items || []
    pagination.total = res.total || 0
    nextTick(() => {
      updateChart()
    })
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 获取公司列表
const fetchCompanies = async () => {
  try {
    companies.value = await getAllCompanies()
  } catch (error) {
    console.error('获取公司列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.per_page = size
  fetchData()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增记录'
  formData.id = null
  formData.company_id = null
  formData.year = new Date().getFullYear()
  formData.new_company_name = ''
  moduleKeywords.value.forEach(kw => {
    formData[kw.keyword] = kw.data_type === 'number' ? 0 : ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = '编辑记录'
  formData.id = row.id
  formData.company_id = row.company_id
  formData.year = row.year
  formData.new_company_name = ''
  moduleKeywords.value.forEach(kw => {
    formData[kw.keyword] = row[kw.keyword] !== undefined ? row[kw.keyword] : (kw.data_type === 'number' ? 0 : '')
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' })
    await deleteCustomModuleData(moduleCode.value, row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    let companyId = formData.company_id

    // 如果是手动输入的公司名称
    if (typeof formData.company_id === 'string' && formData.new_company_name) {
      let code = ''
      let name = formData.new_company_name

      if (formData.company_id.includes(' - ')) {
        const parts = formData.company_id.split(' - ')
        code = parts[0]
        name = parts[1]
      } else {
        name = formData.company_id
      }

      try {
        const companyRes = await request({
          url: '/companies',
          method: 'post',
          data: { code, name }
        })
        companyId = companyRes.id
        ElMessage.success('公司创建成功')
        await fetchCompanies()
      } catch (err) {
        console.error('创建公司失败:', err)
        ElMessage.error('创建公司失败')
        return
      }
    }

    if (!companyId) {
      ElMessage.warning('请选择或输入公司')
      return
    }

    // 构建提交数据
    const submitData = {
      company_id: companyId,
      year: formData.year
    }
    moduleKeywords.value.forEach(kw => {
      if (formData[kw.keyword] !== undefined && formData[kw.keyword] !== '') {
        submitData[kw.keyword] = formData[kw.keyword]
      }
    })

    if (formData.id) {
      await updateCustomModuleData(moduleCode.value, formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createCustomModuleData(moduleCode.value, submitData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '提交失败')
  }
}

// 公司选择变化
const handleCompanyChange = (value) => {
  if (typeof value === 'string') {
    formData.new_company_name = value
    const parts = value.split(' - ')
    if (parts.length === 2) {
      formData.new_company_name = parts[1]
    }
  } else {
    formData.new_company_name = ''
  }
}

// 显示新增公司对话框
const showAddCompanyDialog = () => {
  companyFormData.name = ''
  companyFormData.code = ''
  companyFormData.business = ''
  companyFormData.remark = ''
  addCompanyDialogVisible.value = true
}

// 提交新增公司
const handleAddCompanySubmit = async () => {
  if (!companyFormRef.value) return

  await companyFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const data = {
        name: companyFormData.name,
        code: companyFormData.code,
        business: companyFormData.business,
        remark: companyFormData.remark
      }

      const res = await request({
        url: '/companies',
        method: 'post',
        data
      })

      ElMessage.success('公司创建成功')
      addCompanyDialogVisible.value = false
      await fetchCompanies()
      formData.company_id = res.id
    } catch (error) {
      console.error('创建公司失败:', error)
      ElMessage.error('创建公司失败')
    } finally {
      submitting.value = false
    }
  })
}

// 导入
const handleImport = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importLoading.value = true
  try {
    const res = await importCustomModuleData(moduleCode.value, importFile.value)
    ElMessage.success(res.message || '导入成功')
    importDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error(error.message || '导入失败')
  } finally {
    importLoading.value = false
  }
}

// 导出
const handleExport = async () => {
  try {
    const response = await exportCustomModuleData(moduleCode.value)
    const blob = response
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${moduleCode.value}_export.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 公司对比
const handleCompare = () => {
  compareDialogVisible.value = true
}

const fetchCompareData = async (params) => {
  return await compareCustomModuleData(moduleCode.value, params)
}

// 图表初始化
const initChart = () => {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || tableData.value.length === 0 || !chartConfig.metric) return

  // 按公司分组数据
  const companyData = {}
  tableData.value.forEach(item => {
    if (!companyData[item.company_name]) {
      companyData[item.company_name] = []
    }
    companyData[item.company_name].push({
      year: item.year,
      value: item[chartConfig.metric]
    })
  })

  // 获取所有年份
  const years = [...new Set(tableData.value.map(item => item.year))].sort((a, b) => a - b)

  // 构建系列数据
  const series = Object.entries(companyData).map(([name, data]) => ({
    name,
    type: chartConfig.type,
    data: years.map(year => {
      const item = data.find(d => d.year === year)
      return item ? item.value : null
    })
  }))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: Object.keys(companyData),
      type: 'scroll',
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: years,
      name: '年份'
    },
    yAxis: {
      type: 'value',
      name: '数值'
    },
    series,
    dataZoom: [
      { type: 'slider', start: 0, end: 100 },
      { type: 'inside', start: 0, end: 100 }
    ]
  }

  chartInstance.setOption(option, true)
}

// 导出图表
const exportChart = () => {
  if (!chartInstance) {
    ElMessage.warning('图表未加载')
    return
  }

  try {
    const url = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    const link = document.createElement('a')
    link.download = `${moduleCode.value}_chart_${new Date().toISOString().slice(0, 10)}.png`
    link.href = url
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('图表导出成功')
  } catch (error) {
    console.error('导出图表失败:', error)
    ElMessage.error('导出图表失败')
  }
}

// 格式化数字
const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  if (typeof num === 'number') {
    return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
  }
  return num
}

// 监听路由变化
watch(() => route.params.moduleCode, () => {
  fetchModuleInfo()
  fetchData()
}, { immediate: true })

onMounted(() => {
  fetchCompanies()
  nextTick(() => {
    initChart()
  })
})

// 监听窗口大小变化
window.addEventListener('resize', () => {
  if (chartInstance) {
    chartInstance.resize()
  }
})
</script>

<style scoped>
.module-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}

.chart-card {
  margin-top: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }
}
</style>