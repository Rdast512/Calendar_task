import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import LoginPage from './pages/LoginPage';
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext'; 

import HomePage from './pages/HomePage'; // Импортируем главную страницу
import ProtectedRoute from './components/ProtectedRoute'; // Импортируем защищенный роут

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Защищенный роут для главной страницы */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          } 
        />
        
        {/* Здесь будут другие защищенные роуты */}

      </Routes>
    </AuthProvider>
  );
}

export default App