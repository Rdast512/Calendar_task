from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum as SQLAlchemyEnum, CheckConstraint, ForeignKey
import enum


# Типы, которые требуют утверждения
APPROVAL_REQUIRED_TYPES = {'vacation', 'business_trip'}

# Типы, которые являются фактом (отчет по факту)
FACTUAL_TYPES = {'sick_leave', 'day_off', 'meeting'}

# Приватные типы
PRIVATE_PRESENCE_TYPES = {'sick_leave', 'day_off'}

# Все разрешенные для создания типы "особых случаев"
ALLOWED_EVENT_TYPES = APPROVAL_REQUIRED_TYPES.union(FACTUAL_TYPES)

# ============================================================================
# 1. Python ENUMs для соответствия типам данных в PostgreSQL
# ============================================================================

class RoleEnum(enum.Enum):
    user = 'user'
    admin = 'admin'


class WorkModeEnum(enum.Enum):
    office = 'office'
    remote = 'remote'
    hybrid = 'hybrid'


# ============================================================================
# 2. Ассоциативные таблицы для связей "многие-ко-многим" (без доп. полей)
# ============================================================================

# Связь Сотрудник <-> Отдел
employee_departments_association = db.Table('employee_departments', db.metadata,
                                            db.Column('employee_id', db.Integer, db.ForeignKey('employees.employee_id'),
                                                      primary_key=True),
                                            db.Column('department_id', db.Integer,
                                                      db.ForeignKey('departments.department_id'), primary_key=True)
                                            )

# Связь Сотрудник <-> Команда
employee_teams_association = db.Table('employee_teams', db.metadata,
                                      db.Column('employee_id', db.Integer, db.ForeignKey('employees.employee_id'),
                                                primary_key=True),
                                      db.Column('team_id', db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
                                      )


# ============================================================================
# 3. "one" сторона в связях
# ============================================================================

class Position(db.Model):
    __tablename__ = 'positions'
    position_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    # Обратная связь: позволяет получить всех сотрудников с этой должностью
    employees = db.relationship('Employee', back_populates='position')

    def to_dict(self):
        return {'id': self.position_id, 'name': self.name}


class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    # Обратная связь для M2M: все сотрудники в отделе (не только как в основном)
    employees = db.relationship('Employee', secondary=employee_departments_association, back_populates='departments')

    def to_dict(self):
        return {'id': self.department_id, 'name': self.name}


class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    # Обратная связь для M2M: все сотрудники в команде
    employees = db.relationship('Employee', secondary=employee_teams_association, back_populates='teams')

    def to_dict(self):
        return {'id': self.team_id, 'name': self.name}


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Обратная связь через Association Object
    employee_associations = db.relationship('EmployeeProject', back_populates='project', cascade="all, delete-orphan")

    def to_dict(self):
        return {'id': self.project_id, 'name': self.name, 'start_date': self.start_date, 'end_date': self.end_date}


# ============================================================================
# 4. Основная модель Employee (Сотрудник)
# ============================================================================

class Employee(db.Model):
    __tablename__ = 'employees'

    # --- Основные поля ---
    employee_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    termination_date = db.Column(db.Date)
    work_schedule = db.Column(db.Text)

    # --- Поля с ENUM типами ---
    role = db.Column(SQLAlchemyEnum(RoleEnum, name='role_type'), nullable=False, default=RoleEnum.user)
    work_mode = db.Column(SQLAlchemyEnum(WorkModeEnum, name='work_mode_type'), nullable=False,
                          default=WorkModeEnum.office)

    # --- Связи One-to-Many (внешние ключи) ---
    position_id = db.Column(db.Integer, db.ForeignKey('positions.position_id'))
    main_department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    main_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))

    # --- "Объектные" представления связей ---

    # One-to-Many
    position = db.relationship('Position', back_populates='employees')
    # Указываем `foreign_keys`, чтобы SQLAlchemy не путался между этой связью и M2M
    main_department = db.relationship('Department', foreign_keys=[main_department_id])
    main_team = db.relationship('Team', foreign_keys=[main_team_id])

    # Many-to-Many (простые)
    departments = db.relationship('Department', secondary=employee_departments_association, back_populates='employees')
    teams = db.relationship('Team', secondary=employee_teams_association, back_populates='employees')

    # Many-to-Many (через Association Object для хранения доп. данных)
    projects_association = db.relationship('EmployeeProject', back_populates='employee', cascade="all, delete-orphan")

    # One-to-Many (для событий присутствия)
    presence_records = db.relationship('EmployeePresence', back_populates='employee', lazy='dynamic',
                                       cascade="all, delete-orphan")

    # --- Методы ---
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Полное представление сотрудника для API."""
        return {
            'id': self.employee_id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role.value,
            'work_mode': self.work_mode.value,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'position': self.position.to_dict() if self.position else None,
            'main_department': self.main_department.to_dict() if self.main_department else None,
            'main_team': self.main_team.to_dict() if self.main_team else None,
            # Сериализуем M2M связи
            'additional_departments': [d.to_dict() for d in self.departments],
            'additional_teams': [t.to_dict() for t in self.teams],
            # Особая сериализация для связи с проектами
            'projects': [
                {
                    'project': assoc.project.to_dict(),
                    'participation_percentage': assoc.participation_percentage
                } for assoc in self.projects_association
            ]
        }


# ============================================================================
# 5. Association Object для связи Сотрудник <-> Проект
#    (нужен отдельный класс, т.к. есть доп. поле `participation_percentage`)
# ============================================================================

class EmployeeProject(db.Model):
    __tablename__ = 'employee_projects'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)
    participation_percentage = db.Column(db.Integer, nullable=False)

    # Ограничение на уровне БД
    __table_args__ = (
        CheckConstraint(
            'participation_percentage > 0 AND participation_percentage <= 100 AND participation_percentage % 10 = 0',
            name='chk_participation_percentage'),
    )

    # Связи обратно к Employee и Project
    employee = db.relationship('Employee', back_populates='projects_association')
    project = db.relationship('Project', back_populates='employee_associations')


# ============================================================================
# 6. Модели для учёта времени
# ============================================================================

class EmployeePresence(db.Model):
    __tablename__ = 'employee_presence'
    presence_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    presence_type = db.Column(db.String(50), nullable=False)
    start_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    end_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='planned')  # Можно тоже сделать Enum
    comment = db.Column(db.Text)

    employee = db.relationship('Employee', back_populates='presence_records')



    def to_dict(self, is_viewer_admin=False, viewer_id=None):
        PRIVATE_PRESENCE_TYPES = {'sick_leave', 'day_off'}
        """
        Возвращает данные о присутствии в виде словаря.
        Скрывает чувствительную информацию от обычных пользователей.
        """
        is_owner = self.employee_id == viewer_id

        # Если тип приватный И просматривающий не админ И не владелец записи
        if self.presence_type in PRIVATE_PRESENCE_TYPES and not is_viewer_admin and not is_owner:
            # Для других сотрудников заменяем приватный статус на обобщенный 'absence'
            public_presence_type = 'absence'
            public_comment = 'Сотрудник отсутствует'  # Общий комментарий
        else:
            # Админ или владелец видят всё как есть
            public_presence_type = self.presence_type
            public_comment = self.comment
        print("dwaddwadad")
        return {
            'id': self.presence_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'presence_type': public_presence_type,
            'start_date': self.start_datetime.date().isoformat() if self.start_datetime else None,
            'end_date': self.end_datetime.date().isoformat() if self.end_datetime else None,
            'status': self.status,
            # Комментарий показываем только админам и владельцу
            'comment': public_comment
        }