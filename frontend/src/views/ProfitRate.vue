<template>
  <div class="module-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="个股名称/代码" clearable />
        </el-form-item>
        <el-form-item label="年份">
          <el-date-picker
            v-model="searchForm.yearRange"
            type="yearrange"
            start-placeholder="开始年份"
            end-placeholder="结束年份"
            value-format="YYYY"
          />
        </el-form-item>
        <el-form-item label="毛利率">
          <el-input-number v-model="searchForm.grossMin" placeholder="最小值" :precision="2" />
          <span style="margin: 0 10px">-</span>
          <el-input-number v-model="searchForm.grossMax" placeholder="最大值" :precision="2" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>数据列表</span>
          <div class="table-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增
            </el-button>
            <el-button type="success" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button @click="handleDownloadTemplate">
              <el-icon><Document /></el-icon>
              下载模板
            </el-button>
            <el-button type="info" @click="handleCompare">
              <el-icon><DataLine /></el-icon>
              公司对比
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column type="selection" width="55" />
        <el-table-column prop="company_code" label="代码" width="100" />
        <el-table-column prop="company_name" label="个股名称" width="150" />
        <el-table-column prop="year" label="年份" width="80" sortable />
        <el-table-column prop="gross_profit_margin" label="销售毛利率(%)" width="130">
          <template #default="{ row }">
            <span :class="getMarginClass(row.gross_profit_margin)">
              {{ row.gross_profit_margin?.toFixed(2) || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="net_profit_margin" label="销售净利率(%)" width="130">
          <template #default="{ row }">
            <span :class="getMarginClass(row.net_profit_margin)">
              {{ row.net_profit_margin?.toFixed(2) || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 图表区域 -->
    <el-card class="chart-card">
      <template #header>
        <div class="chart-header">
          <span>数据可视化</span>
          <div class="chart-controls">
            <el-select v-model="chartConfig.metric" style="width: 150px; margin-right: 10px">
              <el-option label="销售毛利率" value="gross_profit_margin" />
              <el-option label="销售净利率" value="net_profit_margin" />
            </el-select>
            <el-select v-model="chartConfig.type" style="width: 120px">
              <el-option label="折线图" value="line" />
              <el-option label="柱状图" value="bar" />
            </el-select>
            <el-button type="primary" @click="updateChart" style="margin-left: 10px">
              刷新图表
            </el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
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
          <el-date-picker v-model="formData.year" type="year" value-format="YYYY" placeholder="选择年份" />
        </el-form-item>
        <el-form-item label="销售毛利率(%)">
          <el-input-number v-model="formData.gross_profit_margin" :precision="2" :step="0.1" />
        </el-form-item>
        <el-form-item label="销售净利率(%)">
          <el-input-number v-model="formData.net_profit_margin" :precision="2" :step="0.1" />
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
        <el-form-item label="个股名称" required>
          <el-input v-model="companyFormData.name" placeholder="请输入个股名称" maxlength="50" show-word-limit clearable />
        </el-form-item>
        <el-form-item label="代码" required>
          <el-input v-model="companyFormData.code" placeholder="请输入代码（如：600584）" maxlength="20" clearable />
          <div class="form-tip">支持 A 股（6 位数字）、港股、美股等代码格式</div>
        </el-form-item>
        <el-form-item label="主营业务">
          <el-input v-model="companyFormData.business" type="textarea" rows="2" placeholder="请输入主营业务（选填）" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="companyFormData.remark" type="textarea" rows="2" placeholder="请输入备注（选填）" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCompanyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddCompanySubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入数据" width="600px">
      <el-upload
        ref="uploadRef"
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .xlsx, .xls 格式文件，请先下载模板
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit">导入</el-button>
      </template>
    </el-dialog>

    <!-- 公司对比对话框 -->
    <CompanyCompareDialog
      v-model="compareDialogVisible"
      module-type="profit_rate"
      :fetch-module-data="getProfitRates"
      :metrics="compareMetrics"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { DataLine, Document, Download, Plus, Search, Upload, View } from '@element-plus/icons-vue'
import { getProfitRates, createProfitRate, updateProfitRate, deleteProfitRate, importProfitRate, exportProfitRate } from '../api/profitRate'
import { getAllCompanies } from '../api/company'
import request from '../api/request'
import CompanyCompareDialog from '../components/CompanyCompareDialog.vue'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  yearRange: [],
  grossMin: null,
  grossMax: null
})

// 表格数据
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 公司列表
const companies = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive({
  id: null,
  company_id: null,
  year: null,
  gross_profit_margin: null,
  net_profit_margin: null
})

// 新增公司对话框相关
const addCompanyDialogVisible = ref(false)
const companyFormRef = ref(null)
const submitting = ref(false)
const companyFormData = reactive({ name: '', code: '', business: '', remark: '' })

// 表单验证规则
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

// 导入对话框
const importDialogVisible = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)

// 图表
const chartRef = ref(null)
let chartInstance = null
const chartConfig = reactive({
  metric: 'gross_profit_margin',
  type: 'line'
})

// 对比对话框
const compareDialogVisible = ref(false)
const compareMetrics = [
  { key: 'gross_profit_margin', label: '销售毛利率(%)' },
  { key: 'net_profit_margin', label: '销售净利率(%)' }
]

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword,
      year_from: searchForm.yearRange?.[0],
      year_to: searchForm.yearRange?.[1],
      gross_min: searchForm.grossMin,
      gross_max: searchForm.grossMax
    }
    const res = await getProfitRates(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 公司选择变化处理
const handleCompanyChange = (value) => {
  if (typeof value === 'string') {
    const parts = value.split(' - ')
    if (parts.length === 2) {
      // 用户输入了"代码 - 名称"格式
    }
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

// 获取公司列表
const fetchCompanies = async () => {
  try {
    const res = await getAllCompanies()
    companies.value = res || []
  } catch (error) {
    console.error(error)
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
  searchForm.yearRange = []
  searchForm.grossMin = null
  searchForm.grossMax = null
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
  Object.assign(formData, {
    id: null,
    company_id: null,
    year: null,
    gross_profit_margin: null,
    net_profit_margin: null
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  dialogTitle.value = '编辑记录'
  Object.assign(formData, {
    id: row.id,
    company_id: row.company_id,
    year: String(row.year),
    gross_profit_margin: row.gross_profit_margin,
    net_profit_margin: row.net_profit_margin
  })
  dialogVisible.value = true
}

// 提交
const handleSubmit = async () => {
  try {
    const data = {
      company_id: formData.company_id,
      year: parseInt(formData.year),
      gross_profit_margin: formData.gross_profit_margin,
      net_profit_margin: formData.net_profit_margin
    }
    
    if (formData.id) {
      await updateProfitRate(formData.id, data)
      ElMessage.success('更新成功')
    } else {
      await createProfitRate(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' })
    await deleteProfitRate(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

// 导入 - 跳转到数据导入中心
const handleImport = () => {
  router.push('/data-import')
}

// 公司对比
const handleCompare = () => {
  compareDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    await importProfitRate(formData)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  }
}

// 导出
const handleExport = async () => {
  try {
    const response = await exportProfitRate({
      keyword: searchForm.keyword,
      year_from: searchForm.yearRange?.[0],
      year_to: searchForm.yearRange?.[1]
    })
    const blob = response.data
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'profit_rate_export.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
  }
}

// 下载模板
const handleDownloadTemplate = () => {
  window.open('/api/templates/profit_rate')
}

// 获取利润率样式
const getMarginClass = (value) => {
  if (value === null || value === undefined) return ''
  if (value > 20) return 'text-success'
  if (value < 0) return 'text-danger'
  return ''
}

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    updateChart()
  }
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

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
  const years = [...new Set(tableData.value.map(item => item.year))].sort()

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
    tooltip: { trigger: 'axis' },
    legend: { data: Object.keys(companyData) },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: '%' },
    series
  }

  chartInstance.setOption(option, true)
}

// 导出图表
const exportChart = () => {
  if (!chartInstance) {
    ElMessage.warning('图表未加载，请先刷新图表')
    return
  }

  try {
    // 获取图表的DataURL（PNG格式）
    const url = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    })

    // 创建下载链接
    const link = document.createElement('a')
    link.download = `利润率图表_${new Date().toISOString().slice(0, 10)}.png`
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

onMounted(() => {
  fetchData()
  fetchCompanies()
  nextTick(() => initChart())
})
</script>

<style scoped>
.module-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-card {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 0;
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

.chart-card {
  margin-bottom: 0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
}

.text-success {
  color: #67C23A;
  font-weight: bold;
}

.text-danger {
  color: #F56C6C;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}
</style>
