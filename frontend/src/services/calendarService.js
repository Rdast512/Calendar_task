import axios from 'axios';

// Настраиваем axios для автоматической отправки токена с каждым запросом
const apiClient = axios.create({
  baseURL: '/api',
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});


const getCalendarEvents = (startDate, endDate) => {
  return apiClient.get('/calendar/events', {
    params: {
      start_date: startDate,
      end_date: endDate,
    }
  });
};

const calendarService = {
  getCalendarEvents,
};

export default calendarService;