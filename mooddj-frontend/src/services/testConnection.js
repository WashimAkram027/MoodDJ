import api from './api';

export const testBackendConnection = async () => {
  try {
    const response = await api.get('/api/health');
    console.log('✅ Backend connection successful:', response);
    return true;
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
};