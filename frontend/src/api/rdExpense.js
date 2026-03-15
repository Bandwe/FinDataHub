import request from './request'

export const getRdExpenses = (params) => {
  return request({
    url: '/rd_expense',
    method: 'get',
    params
  })
}

export const createRdExpense = (data) => {
  return request({
    url: '/rd_expense',
    method: 'post',
    data
  })
}

export const updateRdExpense = (id, data) => {
  return request({
    url: `/rd_expense/${id}`,
    method: 'put',
    data
  })
}

export const deleteRdExpense = (id) => {
  return request({
    url: `/rd_expense/${id}`,
    method: 'delete'
  })
}

export const exportRdExpense = (params) => {
  return request({
    url: '/rd_expense/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
