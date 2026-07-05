import request from './request'

export const getIndustryTemplates = () => {
  return request({
    url: '/industry-templates',
    method: 'get'
  })
}

export const getAllIndustryTemplates = () => {
  return request({
    url: '/industry-templates/all',
    method: 'get'
  })
}

export const createIndustryTemplate = (data) => {
  return request({
    url: '/industry-templates',
    method: 'post',
    data
  })
}

export const updateIndustryTemplate = (id, data) => {
  return request({
    url: `/industry-templates/${id}`,
    method: 'put',
    data
  })
}

export const confirmIndustryTemplate = (id) => {
  return request({
    url: `/industry-templates/${id}/confirm`,
    method: 'post'
  })
}

export const cloneIndustryTemplate = (id, data = {}) => {
  return request({
    url: `/industry-templates/${id}/clone`,
    method: 'post',
    data
  })
}

export const deleteIndustryTemplate = (id) => {
  return request({
    url: `/industry-templates/${id}`,
    method: 'delete'
  })
}

export const downloadIndustryTemplate = (code) => {
  return request({
    url: `/industry-templates/${code}/template`,
    method: 'get',
    responseType: 'blob'
  })
}
