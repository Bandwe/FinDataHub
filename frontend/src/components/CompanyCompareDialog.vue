<template>
  <el-dialog
    v-model="visible"
    title="公司数据对比"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 公司选择区域 -->
    <el-card class="select-card">
      <template #header>
        <div class="card-header">
          <span>选择公司</span>
          <el-button type="primary" size="small" @click="handleCompare" :disabled="selectedCompanies.length < 2">
            <el-icon><DataLine /></el-icon>
            开始对比
          </el-button>
        </div>
      </template>
      <el-select
        v-model="selectedCompanies"
        multiple
        filterable
        placeholder="请选择要对比的公司（至少选择2个）"
        style="width: 100%"
        collapse-tags
        collapse-tags-tooltip
      >
        <el-option
          v-for="company in companies"
          :key="company.id"
          :label="`${company.code} - ${company.name}`"
          :value="company.id"
        />
      </el-select>
    </el-card>

    <!-- 对比结果区域 -->
    <el-card v-if="showResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>对比结果</span>
          <div class="result-controls">
            <el-select v-model="resultConfig.metric" style="width: 150px; margin-right: 10px">
              <el-option
                v-for="option in metricOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            <el-select v-model="resultConfig.viewType" style="width: 120px">
              <el-option label="表格视图" value="table" />
              <el-option label="图表视图" value="chart" />
            </el-select>
          </div>
        </div>
      </template>

      <!-- 表格视图 -->
      <div v-if="resultConfig.viewType === 'table'" class="table-view">
        <el-table :data="compareTableData" border stripe>
          <el-table-column prop="year" label="年份" width="80" fixed />
          <el-table-column
            v-for="company in selectedCompanyDetails"
            :key="company.id"
            :label="`${company.code} - ${company.name}`"
            min-width="150"
          >
            <template #default="{ row }">
              <span :class="getValueClass(row[company.id])">
                {{ formatValue(row[company.id]) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 图表视图 -->
      <div v-else class="chart-view">
        <div ref="compareChartRef" class="chart-container"></div>
      </div>
    </el-card>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleExport" v-if="showResult">
        <el-icon><Download /></el-icon>
        导出对比结果
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { DataLine, Download } from '@element-plus/icons-vue'
import { getAllCompanies } from '../api/company'
import * as XLSX from 'xlsx'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  moduleType: {
    type: String,
    required: true
  },
  fetchModuleData: {
    type: Function,
    required: true
  },
  metrics: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// 状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const companies = ref([])
const selectedCompanies = ref([])
const showResult = ref(false)
const compareData = ref([])
const compareChartRef = ref(null)
let compareChartInstance = null

// 配置
const resultConfig = reactive({
  metric: '',
  viewType: 'table'
})

// 指标选项
const metricOptions = computed(() => {
  return props.metrics.map(m => ({
    label: m.label,
    value: m.key
  }))
})

// 选中的公司详情
const selectedCompanyDetails = computed(() => {
  return companies.value.filter(c => selectedCompanies.value.includes(c.id))
})

// 对比表格数据
const compareTableData = computed(() => {
  if (!compareData.value.length) return []
  
  const years = [...new Set(compareData.value.map(d => d.year))].sort()
  
  return years.map(year => {
    const row = { year }
    selectedCompanyDetails.value.forEach(company => {
      const data = compareData.value.find(d => d.year === year && d.company_id === company.id)
      row[company.id] = data ? data[resultConfig.metric] : null
    })
    return row
  })
})

// 获取公司列表
const fetchCompanies = async () => {
  try {
    const res = await getAllCompanies()
    companies.value = res || []
  } catch (error) {
    ElMessage.error('获取公司列表失败')
  }
}

// 开始对比
const handleCompare = async () => {
  if (selectedCompanies.value.length < 2) {
    ElMessage.warning('请至少选择2个公司进行对比')
    return
  }

  try {
      const allData = []
      for (const companyId of selectedCompanies.value) {
        const res = await props.fetchModuleData({
          company_id: companyId,
          per_page: 100
        })
        allData.push(...(res.items || []))
      }
      compareData.value = allData
    
    if (props.metrics.length && !resultConfig.metric) {
      resultConfig.metric = props.metrics[0].key
    }
    
    showResult.value = true
    
    await nextTick()
    if (resultConfig.viewType === 'chart') {
      initCompareChart()
    }
  } catch (error) {
    ElMessage.error('获取对比数据失败')
  }
}

// 初始化对比图表
const initCompareChart = () => {
  if (!compareChartRef.value) return
  
  if (compareChartInstance) {
    compareChartInstance.dispose()
  }
  
  compareChartInstance = echarts.init(compareChartRef.value)
  
  const years = [...new Set(compareData.value.map(d => d.year))].sort()
  
  const series = selectedCompanyDetails.value.map(company => {
    const companyData = years.map(year => {
      const data = compareData.value.find(d => d.year === year && d.company_id === company.id)
      return data ? data[resultConfig.metric] : null
    })
    
    return {
      name: `${company.code} - ${company.name}`,
      type: 'line',
      data: companyData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8
    }
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: selectedCompanyDetails.value.map(c => `${c.code} - ${c.name}`),
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: years
    },
    yAxis: {
      type: 'value',
      name: metricOptions.value.find(m => m.value === resultConfig.metric)?.label || ''
    },
    series
  }
  
  compareChartInstance.setOption(option)
}

// 格式化数值
const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  return value
}

// 获取数值样式类
const getValueClass = (value) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') {
    return value >= 0 ? 'positive-value' : 'negative-value'
  }
  return ''
}

// 导出对比结果
const handleExport = async () => {
  if (!showResult.value || !compareData.value.length) {
    ElMessage.warning('没有可导出的对比数据')
    return
  }

  try {
    // 显示导出选项对话框
    const exportOptions = await showExportOptions()
    if (!exportOptions) return

    const { format, includeChart } = exportOptions

    switch (format) {
      case 'excel':
        await exportToExcel()
        break
      case 'csv':
        await exportToCSV()
        break
      case 'pdf':
        await exportToPDF(includeChart)
        break
      case 'image':
        await exportChartAsImage()
        break
      default:
        ElMessage.warning('不支持的导出格式')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + (error.message || '未知错误'))
  }
}

// 显示导出选项对话框
const showExportOptions = () => {
  return new Promise((resolve) => {
    const h = ElMessageBox
    let selectedFormat = 'excel'
    let includeChart = false

    ElMessageBox({
      title: '导出选项',
      message: h('div', { style: 'padding: 10px 0' }, [
        h('div', { style: 'margin-bottom: 15px' }, [
          h('div', { style: 'font-weight: bold; margin-bottom: 8px' }, '选择导出格式:'),
          h('div', { style: 'display: flex; flex-direction: column; gap: 8px' }, [
            h('label', { style: 'cursor: pointer; display: flex; align-items: center' }, [
              h('input', {
                type: 'radio',
                name: 'format',
                value: 'excel',
                checked: true,
                style: 'margin-right: 8px',
                onChange: () => { selectedFormat = 'excel' }
              }),
              'Excel (.xlsx) - 包含完整数据'
            ]),
            h('label', { style: 'cursor: pointer; display: flex; align-items: center' }, [
              h('input', {
                type: 'radio',
                name: 'format',
                value: 'csv',
                style: 'margin-right: 8px',
                onChange: () => { selectedFormat = 'csv' }
              }),
              'CSV (.csv) - 纯文本数据'
            ]),
            h('label', { style: 'cursor: pointer; display: flex; align-items: center' }, [
              h('input', {
                type: 'radio',
                name: 'format',
                value: 'image',
                style: 'margin-right: 8px',
                onChange: () => { selectedFormat = 'image' }
              }),
              'PNG图片 (.png) - 仅图表'
            ])
          ])
        ]),
        resultConfig.viewType === 'chart' ? h('div', { style: 'margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee' }, [
          h('label', { style: 'cursor: pointer; display: flex; align-items: center' }, [
            h('input', {
              type: 'checkbox',
              style: 'margin-right: 8px',
              onChange: (e) => { includeChart = e.target.checked }
            }),
            '包含图表（仅Excel和PDF）'
          ])
        ]) : null
      ]),
      showCancelButton: true,
      confirmButtonText: '导出',
      cancelButtonText: '取消',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          resolve({ format: selectedFormat, includeChart })
        } else {
          resolve(null)
        }
        done()
      }
    })
  })
}

// 导出为Excel
const exportToExcel = () => {
  const data = prepareExportData()
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  
  // 设置列宽
  const colWidths = Object.keys(data[0] || {}).map(() => ({ wch: 15 }))
  ws['!cols'] = colWidths
  
  XLSX.utils.book_append_sheet(wb, ws, '对比结果')
  
  const fileName = `公司对比结果_${new Date().toISOString().slice(0, 10)}.xlsx`
  XLSX.writeFile(wb, fileName)
  
  ElMessage.success('Excel导出成功')
}

// 导出为CSV
const exportToCSV = () => {
  const data = prepareExportData()
  if (!data.length) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(h => {
      const val = row[h]
      // 处理包含逗号或引号的值
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
        return `"${val.replace(/"/g, '""')}"`
      }
      return val !== null && val !== undefined ? val : ''
    }).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `公司对比结果_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
  
  ElMessage.success('CSV导出成功')
}

// 导出为PDF（简化版，使用打印功能）
const exportToPDF = async (includeChart) => {
  // 创建临时容器用于打印
  const printContainer = document.createElement('div')
  printContainer.style.cssText = 'position: fixed; left: -9999px; top: 0; width: 210mm; padding: 20px; background: white;'
  
  // 添加标题
  const title = document.createElement('h2')
  title.textContent = '公司数据对比报告'
  title.style.cssText = 'text-align: center; margin-bottom: 20px;'
  printContainer.appendChild(title)
  
  // 添加日期
  const date = document.createElement('p')
  date.textContent = `生成日期: ${new Date().toLocaleString('zh-CN')}`
  date.style.cssText = 'text-align: right; margin-bottom: 20px;'
  printContainer.appendChild(date)
  
  // 添加表格
  const table = document.createElement('table')
  table.style.cssText = 'width: 100%; border-collapse: collapse; margin-bottom: 20px;'
  
  // 表头
  const thead = document.createElement('thead')
  const headerRow = document.createElement('tr')
  const data = prepareExportData()
  if (data.length > 0) {
    Object.keys(data[0]).forEach(key => {
      const th = document.createElement('th')
      th.textContent = key
      th.style.cssText = 'border: 1px solid #ddd; padding: 8px; background: #f5f5f5;'
      headerRow.appendChild(th)
    })
  }
  thead.appendChild(headerRow)
  table.appendChild(thead)
  
  // 表体
  const tbody = document.createElement('tbody')
  data.forEach(row => {
    const tr = document.createElement('tr')
    Object.values(row).forEach(val => {
      const td = document.createElement('td')
      td.textContent = val !== null && val !== undefined ? val : '-'
      td.style.cssText = 'border: 1px solid #ddd; padding: 8px; text-align: center;'
      tr.appendChild(td)
    })
    tbody.appendChild(tr)
  })
  table.appendChild(tbody)
  printContainer.appendChild(table)
  
  // 如果需要包含图表
  if (includeChart && resultConfig.viewType === 'chart' && compareChartInstance) {
    const chartImg = document.createElement('img')
    chartImg.src = compareChartInstance.getDataURL({ type: 'png', pixelRatio: 2 })
    chartImg.style.cssText = 'width: 100%; margin-top: 20px;'
    printContainer.appendChild(chartImg)
  }
  
  document.body.appendChild(printContainer)
  
  // 打印为PDF
  const originalTitle = document.title
  document.title = '公司对比结果'
  window.print()
  document.title = originalTitle
  
  document.body.removeChild(printContainer)
  
  ElMessage.success('PDF导出成功（通过打印功能保存为PDF）')
}

// 导出图表为图片
const exportChartAsImage = () => {
  if (resultConfig.viewType !== 'chart' || !compareChartInstance) {
    ElMessage.warning('当前不是图表视图，无法导出图片')
    return
  }

  const url = compareChartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })

  const link = document.createElement('a')
  link.download = `公司对比图表_${new Date().toISOString().slice(0, 10)}.png`
  link.href = url
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('图表导出成功')
}

// 准备导出数据
const prepareExportData = () => {
  const data = compareTableData.value
  const metricLabel = metricOptions.value.find(m => m.value === resultConfig.metric)?.label || ''
  
  return data.map(row => {
    const newRow = { 年份: row.year }
    selectedCompanyDetails.value.forEach(company => {
      const value = row[company.id]
      newRow[`${company.code}_${company.name}_${metricLabel}`] = formatValue(value)
    })
    return newRow
  })
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  showResult.value = false
  selectedCompanies.value = []
  compareData.value = []
  if (compareChartInstance) {
    compareChartInstance.dispose()
    compareChartInstance = null
  }
}

// 监听视图类型变化
watch(() => resultConfig.viewType, async (newType) => {
  if (newType === 'chart' && showResult.value) {
    await nextTick()
    initCompareChart()
  }
})

// 监听指标变化
watch(() => resultConfig.metric, () => {
  if (resultConfig.viewType === 'chart' && showResult.value) {
    initCompareChart()
  }
})

onMounted(() => {
  fetchCompanies()
  
  window.addEventListener('resize', () => {
    if (compareChartInstance) {
      compareChartInstance.resize()
    }
  })
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.select-card {
  margin-bottom: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-controls {
  display: flex;
  align-items: center;
}

.table-view {
  max-height: 400px;
  overflow-y: auto;
}

.chart-view {
  height: 400px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.positive-value {
  color: #67c23a;
}

.negative-value {
  color: #f56c6c;
}
</style>
