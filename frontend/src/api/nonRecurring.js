import request from './request'

export const getNonRecurrings = (params) => {
  return request({
    url: '/non_recurring',
    method: 'get',
    params
  })
}

export const createNonRecurring = (data) => {
  return request({
    url: '/non_recurring',
    method: 'post',
    data
  })
}

export const updateNonRecurring = (id, data) => {
  return request({
    url: `/non_recurring/${id}`,
    method: 'put',
    data
  })
}

export const deleteNonRecurring = (id) => {
  return request({
    url: `/non_recurring/${id}`,
    method: 'delete'
  })
}

export const exportNonRecurring = (params) => {
  return request({
    url: '/non_recurring/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
