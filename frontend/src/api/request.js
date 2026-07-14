import axios from 'axios'
import { ElMessage } from 'element-plus'

const responseMessage = async (error, fallback) => {
  const data = error?.response?.data

  if (data instanceof Blob) {
    try {
      const text = await data.text()
      const parsed = JSON.parse(text)
      return parsed.message || fallback
    } catch {
      return fallback
    }
  }

  return data?.message || error?.message || fallback
}

const notifyError = (error, message, status) => {
  const requestError = error instanceof Error ? error : new Error(message)
  requestError.message = message
  requestError.status = status
  requestError.isNotified = true
  ElMessage.error(message)
  return requestError
}

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 处理 blob 类型响应（导出功能）
    if (response.config.responseType === 'blob') {
      return response.data
    }

    const res = response.data
    if (res.code !== 200) {
      const message = res.message || '请求失败'
      return Promise.reject(notifyError(new Error(message), message, res.code))
    }
    return res.data
  },
  async error => {
    const message = await responseMessage(error, '网络错误')
    return Promise.reject(notifyError(error, message, error?.response?.status))
  }
)

export default request
