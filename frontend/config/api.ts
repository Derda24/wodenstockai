// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://wodenstockai.onrender.com' 
  : 'http://localhost:8000';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
  },
  STOCK: {
    GET: `${API_BASE_URL}/api/stock`,
    UPDATE: `${API_BASE_URL}/api/stock/update`,
    REMOVE: `${API_BASE_URL}/api/stock/remove`,
    ADD_PRODUCT: `${API_BASE_URL}/api/stock/add-product`,
  },
  SALES: {
    UPLOAD: `${API_BASE_URL}/api/sales/upload`,
  },
  ANALYSIS: {
    GET: `${API_BASE_URL}/api/analysis`,
    TEST_DATA: `${API_BASE_URL}/api/test/sales-data`,
  },
  RECOMMENDATIONS: {
    GET: `${API_BASE_URL}/api/recommendations`,
    CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
  },
  DAILY_CONSUMPTION: {
    APPLY: `${API_BASE_URL}/api/daily-consumption/apply`,
  },
};

export default API_BASE_URL;
