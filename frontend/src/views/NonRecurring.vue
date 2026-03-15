<template>
  <div class="module-container">
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="个股名称/代码" clearable />
        </el-form-item>
        <el-form-item label="年份">
          <el-date-picker v-model="searchForm.yearRange" type="yearrange" start-placeholder="开始年份" end-placeholder="结束年份" value-format="YYYY" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon>查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>扣非净利润数据</span>
          <div class="table-actions">
            <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon>新增</el-button>
            <el-button type="success" @click="handleImport"><el-icon><Upload /></el-icon>导入</el-button>
            <el-button type="warning" @click="handleExport"><el-icon><Download /></el-icon>导出</el-button>
            <el-button type="info" @click="handleCompare">
              <el-icon><DataLine /></el-icon>
              公司对比
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="company_code" label="代码" width="100" />
        <el-table-column prop="company_name" label="个股名称" width="150" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="non_recurring_profit" label="扣非净利润(亿元)" width="150" />
        <el-table-column prop="non_recurring_growth" label="扣非增长率" width="120">
          <template #default="{ row }">
            <span :class="row.non_recurring_growth > 0 ? 'text-success' : 'text-danger'">
              {{ row.non_recurring_growth ? (row.non_recurring_growth * 100).toFixed(2) + '%' : '-' }}
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
      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" class="pagination" @size-change="handleSizeChange" @current-change="handlePageChange" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="formData" label-width="140px">
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
              <el-option v-for="company in companies" :key="company.id" :label="`${company.code} - ${company.name}`" :value="company.id" />
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
        <el-form-item label="扣非净利润(亿元)">
          <el-input-number v-model="formData.non_recurring_profit" :precision="2" :step="0.1" />
        </el-form-item>
        <el-form-item label="扣非增长率">
          <el-input-number v-model="formData.non_recurring_growth" :precision="4" :step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 数据可视化图表 -->
    <el-card class="chart-card">
      <template #header>
        <div class="chart-header">
          <span>数据可视化</span>
          <div class="chart-controls">
            <el-select v-model="chartConfig.metric" style="width: 150px; margin-right: 10px">
              <el-option label="扣非净利润" value="non_recurring_profit" />
              <el-option label="扣非增长率" value="non_recurring_growth" />
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

    <!-- 公司对比对话框 -->
    <CompanyCompareDialog
      v-model="compareDialogVisible"
      module-type="non_recurring"
      :fetch-module-data="getNonRecurrings"
      :metrics="compareMetrics"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine } from '@element-plus/icons-vue'
import request from '../api/request'
import { getAllCompanies } from '../api/company'
import { getNonRecurrings, exportNonRecurring } from '../api/nonRecurring'
import CompanyCompareDialog from '../components/CompanyCompareDialog.vue'

const router = useRouter()

const searchForm = reactive({ keyword: '', yearRange: [] })
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, per_page: 20, total: 0 })
const companies = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive({ 
  id: null, 
  company_id: null, 
  year: null, 
  non_recurring_profit: null, 
  non_recurring_growth: null,
  new_company_name: ''
})

// 对比对话框
const compareDialogVisible = ref(false)
const compareMetrics = [
  { key: 'non_recurring_profit', label: '扣非净利润(亿元)' },
  { key: 'non_recurring_growth', label: '扣非增长率' }
]

// 新增公司对话框相关
const addCompanyDialogVisible = ref(false)
const companyFormRef = ref(null)
const submitting = ref(false)
const companyFormData = reactive({
  name: '',
  code: '',
  business: '',
  remark: ''
})

// 表单验证规则
const companyFormRules = {
  name: [
    { required: true, message: '请输入个股名称', trigger: 'blur' },
    { min: 1, max: 50, message: '个股名称长度不能超过 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入代码', trigger: 'blur' },
    { 
      pattern: /^[A-Za-z0-9]{1,20}$/, 
      message: '代码格式不正确，支持 1-20 位字母或数字', 
      trigger: 'blur' 
    }
  ]
}

const handleCompanyChange = (value) => {
  // 检查是否是手动输入的新公司（不是数字 ID）
  if (typeof value === 'string') {
    formData.new_company_name = value
    // 提取个股名称（去掉代码部分）
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

const fetchData = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/non_recurring', method: 'get', params: { page: pagination.page, per_page: pagination.per_page, keyword: searchForm.keyword, year_from: searchForm.yearRange?.[0], year_to: searchForm.yearRange?.[1] }})
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { console.error(error) }
  finally { loading.value = false }
}

const fetchCompanies = async () => {
  try { companies.value = await getAllCompanies() } catch (error) { console.error(error) }
}

// 图表相关
const chartRef = ref(null)
let chartInstance = null
const chartConfig = reactive({ metric: 'non_recurring_profit', type: 'line' })

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
    legend: { data: Object.keys(companyData), type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: years, name: '年份' },
    yAxis: { 
      type: 'value', 
      name: chartConfig.metric === 'non_recurring_growth' ? '%' : '亿元',
      axisLabel: {
        formatter: chartConfig.metric === 'non_recurring_growth' ? '{value}%' : '{value}'
      }
    },
    series,
    dataZoom: [{ type: 'slider', start: 0, end: 100 }],
    responsive: true
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
    link.download = `扣非净利润图表_${new Date().toISOString().slice(0, 10)}.png`
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

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => { searchForm.keyword = ''; searchForm.yearRange = []; handleSearch() }
const handleSizeChange = (size) => { pagination.per_page = size; fetchData() }
const handlePageChange = (page) => { pagination.page = page; fetchData() }
const handleAdd = () => {
  dialogTitle.value = '新增记录'
  Object.assign(formData, { id: null, company_id: null, year: null, non_recurring_profit: null, non_recurring_growth: null, is_manual_company: false, manual_company_name: '' })
  dialogVisible.value = true
}
const handleEdit = (row) => {
  dialogTitle.value = '编辑记录'
  Object.assign(formData, { id: row.id, company_id: row.company_id, year: String(row.year), non_recurring_profit: row.non_recurring_profit, non_recurring_growth: row.non_recurring_growth, is_manual_company: false, manual_company_name: '' })
  dialogVisible.value = true
}
const handleSubmit = async () => {
  try {
    let companyId = formData.company_id
    
    // 如果是手动输入的个股名称，需要先创建公司
    if (typeof formData.company_id === 'string' && formData.new_company_name) {
      // 提取代码（如果有的话）
      let code = ''
      let name = formData.new_company_name
      
      // 如果是 "代码 - 名称" 格式
      if (formData.company_id.includes(' - ')) {
        const parts = formData.company_id.split(' - ')
        code = parts[0]
        name = parts[1]
      } else {
        name = formData.company_id
      }
      
      // 创建新公司
      try {
        const companyRes = await request({
          url: '/companies',
          method: 'post',
          data: { code, name }
        })
        companyId = companyRes.id
        ElMessage.success('公司创建成功')
        // 刷新公司列表
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
    
    const data = { company_id: companyId, year: parseInt(formData.year), non_recurring_profit: formData.non_recurring_profit, non_recurring_growth: formData.non_recurring_growth }
    if (formData.id) { await request({ url: `/non_recurring/${formData.id}`, method: 'put', data }); ElMessage.success('更新成功') }
    else { await request({ url: '/non_recurring', method: 'post', data }); ElMessage.success('创建成功') }
    dialogVisible.value = false; fetchData()
  } catch (error) { console.error(error) }
}
const handleDelete = async (row) => {
  try { await ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' }); await request({ url: `/non_recurring/${row.id}`, method: 'delete' }); ElMessage.success('删除成功'); fetchData() }
  catch (error) { if (error !== 'cancel') console.error(error) }
}
const handleImport = () => { router.push('/data-import') }
const handleExport = async () => {
  try {
    const response = await exportNonRecurring()
    const blob = response.data
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'non_recurring_export.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
  }
}
const handleCompare = () => {
  compareDialogVisible.value = true
}

onMounted(() => { fetchData(); fetchCompanies(); nextTick(() => initChart()) })
</script>

<style scoped>
.module-container { display: flex; flex-direction: column; gap: 20px; }
.table-header { display: flex; justify-content: space-between; align-items: center; }
.table-actions { display: flex; gap: 10px; }
.pagination { margin-top: 20px; justify-content: flex-end; }
.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
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
  align-items: center;
}
.chart-container {
  height: 400px;
  width: 100%;
}
@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }
  .chart-controls {
    flex-wrap: wrap;
    gap: 10px;
  }
  .chart-controls .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
}
</style>
