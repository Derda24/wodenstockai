// API Configuration
// Prefer explicit public env var, then detect localhost, else fallback to production URL
const explicitBase = process.env.NEXT_PUBLIC_API_BASE_URL;
const isBrowser = typeof window !== 'undefined';
const runningOnLocalhost = isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const API_BASE_URL = explicitBase
  ? explicitBase
  : (runningOnLocalhost ? 'http://localhost:8000' : (process.env.NODE_ENV === 'production' ? 'https://wodenstockai.onrender.com' : 'http://localhost:8000'));

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
    REFRESH: `${API_BASE_URL}/api/refresh-data`,
  },
  RECOMMENDATIONS: {
    GET: `${API_BASE_URL}/api/recommendations`,
    CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
  },
  SCHEDULER: {
    BARISTAS: {
      GET: `${API_BASE_URL}/api/baristas`,
      CREATE: `${API_BASE_URL}/api/baristas`,
      UPDATE: (id: string) => `${API_BASE_URL}/api/baristas/${id}`,
      DELETE: (id: string) => `${API_BASE_URL}/api/baristas/${id}`,
    },
    SCHEDULES: {
      GET: `${API_BASE_URL}/api/schedules`,
      GENERATE: `${API_BASE_URL}/api/schedules/generate`,
      SHIFTS: (id: string) => `${API_BASE_URL}/api/schedules/${id}/shifts`,
      PUBLISH: (id: string) => `${API_BASE_URL}/api/schedules/${id}/publish`,
    },
    TIME_OFF: {
      GET: `${API_BASE_URL}/api/time-off-requests`,
      CREATE: `${API_BASE_URL}/api/time-off-requests`,
      UPDATE: (id: string) => `${API_BASE_URL}/api/time-off-requests/${id}`,
    },
  },
  DAILY_CONSUMPTION: {
    APPLY: `${API_BASE_URL}/api/daily-consumption/apply`,
  },
};

export default API_BASE_URL;
