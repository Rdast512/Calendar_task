from datetime import datetime
from .models import ALLOWED_EVENT_TYPES, APPROVAL_REQUIRED_TYPES
from datetime import datetime
from flask import Blueprint, jsonify, request
from . import db
from .models import Employee, RoleEnum, Position, Department, Team, Project, EmployeeProject, EmployeePresence
from .decorators import admin_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_

bp = Blueprint('api', __name__, url_prefix='/api')


def validate_ids(data):
    """Проверяет, существуют ли ID, переданные в запросе, в базе данных."""
    if 'position_id' in data and data['position_id'] and not Position.query.get(data['position_id']):
        return f"Position with id {data['position_id']} not found."
    if 'main_department_id' in data and data['main_department_id'] and not Department.query.get(data['main_department_id']):
        return f"Department with id {data['main_department_id']} not found."
    if 'main_team_id' in data and data['main_team_id'] and not Team.query.get(data['main_team_id']):
        return f"Team with id {data['main_team_id']} not found."
    return None


@bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"msg": "Admins only!"}), 403

    return jsonify(data="Welcome to the admin dashboard!"), 200


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', None)
    password = data.get('password', None)

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    employee = Employee.query.filter_by(email=email).first()

    if not employee or not employee.check_password(password):
        return jsonify({"msg": "Bad email or password"}), 401

    # Создаем токен с дополнительными данными о роли
    additional_claims = {"role": employee.role.value}
    access_token = create_access_token(identity=str(employee.employee_id), additional_claims=additional_claims)

    return jsonify(access_token=access_token)


# CREATE: Создание нового пользователя (только админ)
@bp.route('/users', methods=['POST'])
@admin_required()
def create_user():
    data = request.get_json()
    if not all(k in data for k in ['email', 'password', 'full_name']):
        return jsonify(msg="Missing required fields: email, password, full_name"), 400

    if Employee.query.filter_by(email=data['email']).first():
        return jsonify(msg="User with this email already exists"), 409

    error = validate_ids(data)
    if error:
        return jsonify(msg=error), 400

    # Создание основного объекта Employee
    new_employee = Employee(
        email=data['email'],
        full_name=data['full_name'],
        role=RoleEnum(data.get('role', 'user')),
        work_mode=data.get('work_mode', 'office'),
        work_schedule=data.get('work_schedule'),
        position_id=data.get('position_id'),
        main_department_id=data.get('main_department_id'),
        main_team_id=data.get('main_team_id')
    )
    new_employee.set_password(data['password'])

    # Обработка связей Many-to-Many

    if 'additional_department_ids' in data:
        for dept_id in data['additional_department_ids']:
            dept = Department.query.get(dept_id)
            if dept:
                new_employee.departments.append(dept)

    # Участие в проектах (ожидаем список объектов: [{"project_id": X, "participation_percentage": Y}])
    if 'projects' in data:
        for proj_data in data['projects']:
            project = Project.query.get(proj_data.get('project_id'))
            if project:
                association = EmployeeProject(
                    project=project,
                    participation_percentage=proj_data.get('participation_percentage', 0)
                )
                new_employee.projects_association.append(association)

    db.session.add(new_employee)
    db.session.commit()

    return jsonify(new_employee.to_dict()), 201


# READ: Получение своего профиля (любой залогиненный пользователь)
@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    current_user_id = get_jwt_identity()
    employee = Employee.query.get(current_user_id)
    if not employee:
        return jsonify(msg="User not found"), 404
    return jsonify(employee.to_dict())


# READ: Получение профиля по ID (только админ)
@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_by_id(user_id):
    employee = Employee.query.get(user_id)
    if not employee:
        return jsonify(msg="User not found"), 404

    return jsonify(employee.to_dict())


# UPDATE: Изменение профиля по ID (только админ)
@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    employee = Employee.query.get(user_id)
    if not employee:
        return jsonify(msg="User not found"), 404

    data = request.get_json()

    error = validate_ids(data)
    if error:
        return jsonify(msg=error), 400

    employee.full_name = data.get('full_name', employee.full_name)
    employee.email = data.get('email', employee.email)
    employee.role = RoleEnum(data.get('role', employee.role.value))
    employee.work_mode = RoleEnum(data.get('work_mode', employee.work_mode.value))
    employee.work_schedule = data.get('work_schedule', employee.work_schedule)
    employee.position_id = data.get('position_id', employee.position_id)
    employee.main_department_id = data.get('main_department_id', employee.main_department_id)
    employee.main_team_id = data.get('main_team_id', employee.main_team_id)

    if 'password' in data and data['password']:
        employee.set_password(data['password'])

    # Обновляем связи M2M
    if 'additional_department_ids' in data:
        employee.departments.clear()  # Очищаем старые связи
        for dept_id in data['additional_department_ids']:
            dept = Department.query.get(dept_id)
            if dept:
                employee.departments.append(dept)

    if 'projects' in data:
        employee.projects_association.clear()
        for proj_data in data['projects']:
            project = Project.query.get(proj_data.get('project_id'))
            if project:
                association = EmployeeProject(
                    employee=employee,
                    project=project,
                    participation_percentage=proj_data.get('participation_percentage', 0)
                )
                db.session.add(association)  # Добавляем новую связь

    db.session.commit()
    return jsonify(employee.to_dict())


# DELETE: Удаление профиля по ID (только админ)
@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    employee = Employee.query.get(user_id)
    if not employee:
        return jsonify(msg="User not found"), 404

    db.session.delete(employee)
    db.session.commit()

    return jsonify(msg=f"User with id {user_id} deleted successfully"), 200




@bp.route('/calendar/events', methods=['GET'])
@jwt_required()
def get_calendar_events():

    # /calendar/events?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD

    claims = get_jwt()
    is_admin = claims.get("role") == "admin"
    viewer_id = get_jwt_identity()

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = EmployeePresence.query
    print("Wdadawd")
    if start_date_str and end_date_str:
        try:
            # Используем strptime для явного указания формата
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Находим события, которые пересекаются с заданным диапазоном
            query = query.filter(
                or_(
                    EmployeePresence.start_datetime.between(start_date, end_date),
                    EmployeePresence.end_datetime.between(start_date, end_date),
                    (EmployeePresence.start_datetime <= start_date) & (EmployeePresence.end_datetime >= end_date)
                )
            )
        except ValueError:
            # Эта обработка ошибок остается на всякий случай, если формат будет совсем неверным
            return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Фильтрация по статусу


    query = query.filter(EmployeePresence.status.in_(['approved', 'completed']))

    all_events = query.order_by(EmployeePresence.start_datetime.asc()).all()

    # Сериализуем данные, передавая флаг админа и ID смотрящего в to_dict()
    result = [event.to_dict(is_viewer_admin=is_admin, viewer_id=viewer_id) for event in all_events]

    return jsonify(result)


@bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    data = request.get_json()
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    is_admin = claims.get("role") == "admin"

    target_employee_id = data.get('employee_id', current_user_id)
    if not is_admin and int(target_employee_id) != current_user_id:
        return jsonify({"msg": "You can only create events for yourself"}), 403

    event_type = data.get('event_type')
    if event_type not in ALLOWED_EVENT_TYPES:
        return jsonify({"msg": f"Invalid event_type. Allowed types: {list(ALLOWED_EVENT_TYPES)}"}), 400

    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    if not start_date_str or not end_date_str: return jsonify({"msg": "Dates required"}), 400
    start_datetime = datetime.fromisoformat(start_date_str)
    end_datetime = datetime.fromisoformat(end_date_str).replace(hour=23, minute=59, second=59)

    # определяем статус на основе типа события
    initial_status = 'planned' if event_type in APPROVAL_REQUIRED_TYPES else 'completed'

    new_event = EmployeePresence(
        employee_id=target_employee_id,
        presence_type=event_type,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        status=initial_status,
        comment=data.get('comment')
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify(new_event.to_dict(is_viewer_admin=is_admin, viewer_id=current_user_id)), 201


# READ: Получение списка событий
@bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    claims = get_jwt()
    # Эти данные должны быть доступны всем
    is_admin = True
    viewer_id = get_jwt_identity()

    query = EmployeePresence.query

    if is_admin:
        if 'employee_id' in request.args:
            query = query.filter_by(employee_id=request.args.get('employee_id'))
    else:
        query = query.filter_by(employee_id=viewer_id)

    if 'event_type' in request.args:
        query = query.filter(EmployeePresence.presence_type == request.args.get('event_type'))
    if 'status' in request.args:
        query = query.filter_by(status=request.args.get('status'))

    events = query.order_by(EmployeePresence.start_datetime.desc()).all()

    result = [e.to_dict(is_viewer_admin=is_admin, viewer_id=viewer_id) for e in events]
    return jsonify(result)


# UPDATE: Изменение статуса события (утверждение/отклонение)
@bp.route('/events/<int:event_id>/status', methods=['PUT'])
@admin_required()
def update_event_status(event_id):

    event = EmployeePresence.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    # Убедимся, что мы меняем статус только у тех событий, которые требуют утверждения
    if event.presence_type not in APPROVAL_REQUIRED_TYPES:
        return jsonify({"msg": f"Event type '{event.presence_type}' does not require approval."}), 400

    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['approved', 'rejected']:
        return jsonify({"msg": "Invalid status. Must be 'approved' or 'rejected'"}), 400

    event.status = new_status
    db.session.commit()

    return jsonify(event.to_dict(is_viewer_admin=True, viewer_id=get_jwt_identity()))


# DELETE: Удаление/отмена события
@bp.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    event = EmployeePresence.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    claims = get_jwt()
    current_user_id = get_jwt_identity()
    is_admin = claims.get("role") == "admin"
    is_owner = event.employee_id == current_user_id

    if not is_admin and not is_owner:
        return jsonify({"msg": "Forbidden"}), 403
    if not is_admin and event.status != 'planned':
        return jsonify({"msg": f"Cannot delete a request with status '{event.status}'"}), 403

    db.session.delete(event)
    db.session.commit()
    return jsonify({"msg": f"Event {event_id} deleted successfully"})
