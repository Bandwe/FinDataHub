import request from './request'

export const getShareholderCounts = (params) => {
  return request({
    url: '/shareholder_count',
    method: 'get',
    params
  })
}

export const createShareholderCount = (data) => {
  return request({
    url: '/shareholder_count',
    method: 'post',
    data
  })
}

export const updateShareholderCount = (id, data) => {
  return request({
    url: `/shareholder_count/${id}`,
    method: 'put',
    data
  })
}

export const deleteShareholderCount = (id) => {
  return request({
    url: `/shareholder_count/${id}`,
    method: 'delete'
  })
}

export const exportShareholderCount = (params) => {
  return request({
    url: '/shareholder_count/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
