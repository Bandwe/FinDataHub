import {
  createModuleRecord,
  deleteModuleRecord,
  exportModuleRecords,
  listModuleRecords,
  updateModuleRecord
} from './moduleCrud'

const endpoint = '/rd_expense'

export const getRdExpenses = (params) => {
  return listModuleRecords(endpoint, params)
}

export const createRdExpense = (data) => {
  return createModuleRecord(endpoint, data)
}

export const updateRdExpense = (id, data) => {
  return updateModuleRecord(endpoint, id, data)
}

export const deleteRdExpense = (id) => {
  return deleteModuleRecord(endpoint, id)
}

export const exportRdExpense = (params) => {
  return exportModuleRecords(endpoint, params)
}
