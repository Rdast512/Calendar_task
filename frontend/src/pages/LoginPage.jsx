import React from 'react'; // Убрали useState
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

import './LoginPage.css';

// Схема валидации
const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Некорректный формат email')
    .required('Email обязателен для заполнения'),
  password: Yup.string()
    .min(6, 'Пароль должен содержать минимум 6 символов')
    .required('Пароль обязателен для заполнения'),
});

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  // Больше нет нужды в useState для email, password, error, isLoading!

  const handleSubmit = async (values, { setSubmitting, setFieldError }) => {
    try {
      await login(values.email, values.password);
      navigate('/');
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Ошибка входа. Попробуйте снова.';
      // Устанавливаем общую ошибку для формы через setFieldError
      // 'general' - вымышленное имя поля для отображения общей ошибки
      setFieldError('general', errorMessage);
    } finally {
      // Formik сам управляет состоянием загрузки
      setSubmitting(false);
    }
  };

  return (
    <div className="login-container">
      {/* 1. Оборачиваем все в компонент Formik */}
      <Formik
        initialValues={{ email: '', password: '' }}
        validationSchema={LoginSchema}
        onSubmit={handleSubmit}
      >
        {/* 2. Используем рендер-проп, который дает доступ к состоянию формы */}
        {({ isSubmitting, errors }) => (
          // 3. Используем компонент <Form> вместо <form>
          <Form className="login-form">
            <h2>Вход в систему</h2>
            
            <div className="form-group">
              <label htmlFor="email">Эл. почта</label>
              {/* 4. Используем <Field> вместо <input> */}
              <Field type="email" name="email" id="email" />
              {/* 5. Используем <ErrorMessage> для вывода ошибок валидации */}
              <ErrorMessage name="email" component="div" className="error-message" />
            </div>

            <div className="form-group">
              <label htmlFor="password">Пароль</label>
              <Field type="password" name="password" id="password" />
              <ErrorMessage name="password" component="div" className="error-message" />
            </div>
            
            {/* Отображение общей ошибки от сервера */}
            {errors.general && <div className="error-message general-error">{errors.general}</div>}

            <button type="submit" className="login-button" disabled={isSubmitting}>
              {isSubmitting ? 'Вход...' : 'Войти'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
}

export default LoginPage;