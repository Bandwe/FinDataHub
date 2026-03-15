import request from './request'

export const getRdStaffs = (params) => {
  return request({
    url: '/rd_staff',
    method: 'get',
    params
  })
}

export const createRdStaff = (data) => {
  return request({
    url: '/rd_staff',
    method: 'post',
    data
  })
}

export const updateRdStaff = (id, data) => {
  return request({
    url: `/rd_staff/${id}`,
    method: 'put',
    data
  })
}

export const deleteRdStaff = (id) => {
  return request({
    url: `/rd_staff/${id}`,
    method: 'delete'
  })
}

export const exportRdStaff = (params) => {
  return request({
    url: '/rd_staff/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
