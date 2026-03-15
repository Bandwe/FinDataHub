import request from './request'

export const getProfitRates = (params) => {
  return request({
    url: '/profit_rate',
    method: 'get',
    params
  })
}

export const createProfitRate = (data) => {
  return request({
    url: '/profit_rate',
    method: 'post',
    data
  })
}

export const updateProfitRate = (id, data) => {
  return request({
    url: `/profit_rate/${id}`,
    method: 'put',
    data
  })
}

export const deleteProfitRate = (id) => {
  return request({
    url: `/profit_rate/${id}`,
    method: 'delete'
  })
}

export const importProfitRate = (formData, preview = false) => {
  return request({
    url: `/profit_rate/import${preview ? '?preview=true' : ''}`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const exportProfitRate = (params) => {
  return request({
    url: '/profit_rate/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
