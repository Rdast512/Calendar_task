import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

// 1. Создаем контекст
const AuthContext = createContext(null);

// 2. Создаем провайдер - компонент, который будет "раздавать" состояние
export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  // При первой загрузке приложения, проверяем, есть ли токен в localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const data = await authService.login(email, password);
      setToken(data.access_token);
      return data; // Возвращаем данные для дальнейшей обработки (например, редиректа)
    } catch (error) {
      // Если логин не удался, пробрасываем ошибку дальше, чтобы компонент мог ее обработать
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setToken(null);
  };

  // 3. Передаем состояние и функции через value
  const value = {
    token,
    isAuthenticated: !!token, // Удобный флаг: true если токен есть, false если нет
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 4. Создаем кастомный хук для удобного использования контекста в компонентах
export const useAuth = () => {
  return useContext(AuthContext);
};