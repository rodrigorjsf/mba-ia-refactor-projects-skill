"""User use cases: validation, orchestration and serialization."""
import re

from database import db, commit
from models.user import User
from models.task import Task

EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
VALID_ROLES = ['user', 'admin', 'manager']
MIN_PASSWORD_LENGTH = 4


def list_users():
    result = []
    for user in User.query.all():
        data = user.to_dict()
        data['task_count'] = len(user.tasks)
        result.append(data)
    return result, 200


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in
                     Task.query.filter_by(user_id=user_id).all()]
    return data, 200


def create_user(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return {'error': 'Nome é obrigatório'}, 400
    if not email:
        return {'error': 'Email é obrigatório'}, 400
    if not password:
        return {'error': 'Senha é obrigatória'}, 400
    if not EMAIL_RE.match(email):
        return {'error': 'Email inválido'}, 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400
    if User.query.filter_by(email=email).first():
        return {'error': 'Email já cadastrado'}, 409
    if role not in VALID_ROLES:
        return {'error': 'Role inválido'}, 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    commit()
    return user.to_dict(), 201


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not EMAIL_RE.match(data['email']):
            return {'error': 'Email inválido'}, 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return {'error': 'Senha muito curta'}, 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return {'error': 'Role inválido'}, 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    commit()
    return user.to_dict(), 200


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    # Referential integrity: remove the user's tasks within the same transaction.
    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)
    db.session.delete(user)
    commit()
    return {'message': 'Usuário deletado com sucesso'}, 200


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    result = []
    for task in Task.query.filter_by(user_id=user_id).all():
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue(),
        })
    return result, 200
