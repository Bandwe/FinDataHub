import request from './request'

export const getPeValuations = (params) => {
  return request({
    url: '/pe_valuation',
    method: 'get',
    params
  })
}

export const createPeValuation = (data) => {
  return request({
    url: '/pe_valuation',
    method: 'post',
    data
  })
}

export const updatePeValuation = (id, data) => {
  return request({
    url: `/pe_valuation/${id}`,
    method: 'put',
    data
  })
}

export const deletePeValuation = (id) => {
  return request({
    url: `/pe_valuation/${id}`,
    method: 'delete'
  })
}

export const exportPeValuation = (params) => {
  return request({
    url: '/pe_valuation/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
