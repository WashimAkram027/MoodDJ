import api from './api';

export const testBackendConnection = async () => {
  try {
    await api.get('/api/health');
    return true;
  } catch (error) {
    return false;
  }
};
