import React, { useState, useEffect } from 'react';
import calendarService from '../services/calendarService';
import './HomePage.css';

// --- Вспомогательные функции ---

// Генератор дат для заголовков таблицы
const generateDateRange = (start, end) => {
  const dates = [];
  let currentDate = new Date(start);
  while (currentDate <= end) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  return dates;
};

// Преобразователь данных из API в удобную для рендера структуру
const processEventsData = (events) => {
  const employeesData = {};

  events.forEach(event => {
    // Если сотрудника еще нет в нашем объекте, добавляем его
    if (!employeesData[event.employee_id]) {
      employeesData[event.employee_id] = {
        name: event.employee_name,
        dates: {},
      };
    }

    // Заполняем все дни события
    let currentDate = new Date(event.start_date);
    const endDate = new Date(event.end_date);
    
    while (currentDate <= endDate) {
        const dateString = currentDate.toISOString().split('T')[0]; // YYYY-MM-DD
        employeesData[event.employee_id].dates[dateString] = {
            type: event.presence_type,
            status: event.status
        };
        currentDate.setDate(currentDate.getDate() + 1);
    }
  });

  return employeesData;
};

// --- Основной компонент ---

function HomePage() {
  const [employeesData, setEmployeesData] = useState({});
  const [dateRange, setDateRange] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 7); // Начнем с прошлой недели
    
    const endDate = new Date(today);
    endDate.setMonth(today.getMonth() + 3); // И на 3 месяца вперед

    const formattedStartDate = startDate.toISOString().split('T')[0];
    const formattedEndDate = endDate.toISOString().split('T')[0];

    setDateRange(generateDateRange(startDate, endDate));

    const fetchData = async () => {
      try {
        const response = await calendarService.getCalendarEvents(formattedStartDate, formattedEndDate);
        const processedData = processEventsData(response.data);
        setEmployeesData(processedData);
      } catch (err) {
        setError('Не удалось загрузить данные календаря.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);
  
  // Функция для получения CSS-класса ячейки в зависимости от типа события
  const getCellClass = (event) => {
    if (!event) return 'cell-workday'; // По умолчанию рабочий день
    
    switch(event.type) {
      case 'vacation': return 'cell-vacation';
      case 'sick_leave': return 'cell-sick-leave';
      case 'business_trip': return 'cell-business-trip';
      case 'day_off': return 'cell-day-off';
      case 'meeting': return 'cell-meeting';
      case 'absence': return 'cell-absence'; // Скрытый тип
      default: return 'cell-workday';
    }
  };

  if (isLoading) return <div>Загрузка календаря...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="calendar-container">
      <h1>Календарь команды</h1>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th className="sticky-col">Сотрудник</th>
              {dateRange.map(date => (
                <th key={date.toISOString()}>
                  {date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.values(employeesData).map(employee => (
              <tr key={employee.name}>
                <td className="sticky-col">{employee.name}</td>
                {dateRange.map(date => {
                  const dateString = date.toISOString().split('T')[0];
                  const event = employee.dates[dateString];
                  return (
                    <td 
                      key={dateString} 
                      className={getCellClass(event)}
                      title={event ? `${event.type} (${event.status})` : 'Рабочий день'}
                    >
                       
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HomePage;