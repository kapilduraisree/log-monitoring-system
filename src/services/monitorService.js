import api from './api'

export const startMonitor   = (body)   => api.post('/monitor/start',  body)
export const stopMonitor    = ()       => api.post('/monitor/stop')
export const getStatus      = ()       => api.get('/monitor/status')
export const uploadLog      = (file)   => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload-log', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}

// Feature 8: Multi-target
export const getTargets     = ()       => api.get('/monitor/targets')
export const addTarget      = (body)   => api.post('/monitor/targets', body)
export const removeTarget   = (id)     => api.delete(`/monitor/targets/${id}`)
