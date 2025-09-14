import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth Service
export const authService = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Students Service
export const studentsService = {
  getStudents: async (params = {}) => {
    const response = await api.get('/students/', { params });
    return response.data;
  },

  getStudent: async (studentId) => {
    const response = await api.get(`/students/${studentId}`);
    return response.data;
  },

  createStudent: async (studentData) => {
    const response = await api.post('/students/', studentData);
    return response.data;
  },

  updateStudent: async (studentId, studentData) => {
    const response = await api.put(`/students/${studentId}`, studentData);
    return response.data;
  },

  deleteStudent: async (studentId) => {
    const response = await api.delete(`/students/${studentId}`);
    return response.data;
  },

  assignMentor: async (studentId, mentorId) => {
    const response = await api.post(`/students/${studentId}/assign-mentor`, { mentor_id: mentorId });
    return response.data;
  },

  getStudentsByMentor: async (mentorId) => {
    const response = await api.get(`/students/mentor/${mentorId}`);
    return response.data;
  },
};

// Performance Service
export const performanceService = {
  createPerformanceRecord: async (performanceData) => {
    const response = await api.post('/performance/', performanceData);
    return response.data;
  },

  getStudentPerformanceHistory: async (studentId, params = {}) => {
    const response = await api.get(`/performance/${studentId}/history`, { params });
    return response.data;
  },

  getStudentPerformanceStats: async (studentId, params = {}) => {
    const response = await api.get(`/performance/${studentId}/stats`, { params });
    return response.data;
  },

  updatePerformanceRecord: async (performanceId, performanceData) => {
    const response = await api.put(`/performance/${performanceId}`, performanceData);
    return response.data;
  },

  deletePerformanceRecord: async (performanceId) => {
    const response = await api.delete(`/performance/${performanceId}`);
    return response.data;
  },
};

// Predictions Service
export const predictionsService = {
  predictStudentRisk: async (studentId) => {
    const response = await api.get(`/predict/${studentId}`);
    return response.data;
  },

  getStudentTimeline: async (studentId, days = 30) => {
    const response = await api.get(`/predict/${studentId}/timeline`, { 
      params: { days } 
    });
    return response.data;
  },

  trainModel: async () => {
    const response = await api.post('/predict/train');
    return response.data;
  },

  getBatchPredictions: async (mentorId) => {
    const response = await api.get(`/predict/batch/${mentorId}`);
    return response.data;
  },
};

// Alerts Service
export const alertsService = {
  getAlerts: async (params = {}) => {
    const response = await api.get('/alerts/', { params });
    return response.data;
  },

  getAlert: async (alertId) => {
    const response = await api.get(`/alerts/${alertId}`);
    return response.data;
  },

  updateAlert: async (alertId, alertData) => {
    const response = await api.put(`/alerts/${alertId}`, alertData);
    return response.data;
  },

  acknowledgeAlert: async (alertId, notes = null) => {
    const response = await api.post(`/alerts/${alertId}/acknowledge`, { notes });
    return response.data;
  },

  resolveAlert: async (alertId, notes = null) => {
    const response = await api.post(`/alerts/${alertId}/resolve`, { notes });
    return response.data;
  },

  escalateOverdueAlerts: async () => {
    const response = await api.post('/alerts/escalate-overdue');
    return response.data;
  },

  getAlertStats: async () => {
    const response = await api.get('/alerts/stats/overview');
    return response.data;
  },
};

export default api;
