import api from './api'

export const getAlerts    = (params)      => api.get('/alerts', { params })
export const getAlert     = (id)          => api.get(`/alerts/${id}`)
export const getSummary   = ()            => api.get('/alerts/summary')
export const getCritical  = (limit = 20) => api.get('/alerts/critical', { params: { limit } })

// Feature 3: Acknowledgement
export const acknowledge   = (id, note)  => api.post(`/alerts/${id}/acknowledge`,   { note })
export const unacknowledge = (id)        => api.post(`/alerts/${id}/unacknowledge`)
