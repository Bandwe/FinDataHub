import request from './request'

export const getCompanies = (params) => {
  return request({
    url: '/companies',
    method: 'get',
    params
  })
}

export const getAllCompanies = () => {
  return request({
    url: '/companies/all',
    method: 'get'
  })
}

export const createCompany = (data) => {
  return request({
    url: '/companies',
    method: 'post',
    data
  })
}

export const updateCompany = (id, data) => {
  return request({
    url: `/companies/${id}`,
    method: 'put',
    data
  })
}

export const deleteCompany = (id) => {
  return request({
    url: `/companies/${id}`,
    method: 'delete'
  })
}
