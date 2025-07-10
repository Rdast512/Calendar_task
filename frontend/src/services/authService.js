import axios from 'axios';

const API_URL = '/api'; // Vite proxy перенаправит это на http://localhost:5000/api

const login = async (email, password) => {
  // Отправляем POST-запрос на эндпоинт /api/login
  const response = await axios.post(`${API_URL}/login`, {
    email,
    password,
  });

  // Если запрос успешен, в response.data будет наш токен
  if (response.data.access_token) {
    // Сохраняем токен в localStorage. Это позволит "помнить" пользователя между перезагрузками
    localStorage.setItem('token', response.data.access_token);
  }

  return response.data;
};

const logout = () => {
  // Просто удаляем токен из localStorage
  localStorage.removeItem('token');
};

const authService = {
  login,
  logout,
};

export default authService;