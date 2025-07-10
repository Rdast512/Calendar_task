import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // Если пользователь не аутентифицирован, перенаправляем его на страницу входа.
    // Мы также сохраняем его текущее местоположение, чтобы после входа вернуть его обратно.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Если все в порядке, отображаем дочерний компонент (нашу страницу).
  return children;
}

export default ProtectedRoute;