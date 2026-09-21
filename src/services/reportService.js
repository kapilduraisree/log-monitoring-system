import api from './api'

export const getReport    = (period) => api.get('/report',       { params: { period } })
export const exportCsv    = (period) => api.get('/export/csv',   { params: { period }, responseType: 'blob' })
export const exportJson   = (period) => api.get('/export/json',  { params: { period }, responseType: 'blob' })
export const exportPdf    = (period) => api.get('/export/pdf',   { params: { period }, responseType: 'blob' })
// Feature 5
export const sendReportEmail = (period) => api.post('/report/send-email', null, { params: { period } })
