import api from './api'

export const register   = (data)        => api.post('/auth/register', data)
export const login      = (data)        => api.post('/auth/login', data)
export const getMe      = ()            => api.get('/auth/me')
export const logout     = ()            => api.post('/auth/logout')

// Feature 10: TOTP
export const setupTotp   = ()           => api.post('/auth/totp/setup')
export const verifyTotp  = (code)       => api.post('/auth/totp/verify',  { code })
export const disableTotp = (code)       => api.post('/auth/totp/disable', { code })
