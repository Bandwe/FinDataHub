import request from './request'

export const getIndustryData = (templateCode, params) => {
  return request({
    url: `/industry-data/${templateCode}`,
    method: 'get',
    params
  })
}

export const createIndustryData = (templateCode, data) => {
  return request({
    url: `/industry-data/${templateCode}`,
    method: 'post',
    data
  })
}

export const updateIndustryData = (templateCode, recordId, data) => {
  return request({
    url: `/industry-data/${templateCode}/${recordId}`,
    method: 'put',
    data
  })
}

export const deleteIndustryData = (templateCode, recordId) => {
  return request({
    url: `/industry-data/${templateCode}/${recordId}`,
    method: 'delete'
  })
}

export const importIndustryData = (templateCode, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/industry-data/${templateCode}/import`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const exportIndustryData = (templateCode) => {
  return request({
    url: `/industry-data/${templateCode}/export`,
    method: 'get',
    responseType: 'blob'
  })
}

export const compareIndustryData = (templateCode, data) => {
  return request({
    url: `/industry-data/${templateCode}/compare`,
    method: 'post',
    data
  })
}
