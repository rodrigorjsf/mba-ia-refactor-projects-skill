"""Task use cases: validation, orchestration and serialization.

Controllers return (payload, status_code). Routes stay thin (parse + jsonify).
Unexpected DB errors propagate to the centralized error handler.
"""
from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db, commit
from models.task import Task, VALID_STATUSES, MIN_PRIORITY, MAX_PRIORITY
from models.user import User
from models.category import Category

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200


def _parse_due_date(value):
    # Strict ISO parsing (modern replacement for strptime for ISO dates).
    return datetime.fromisoformat(value)


def _serialize_with_relations(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [_serialize_with_relations(t) for t in tasks], 200


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data, 200


def _validate_title(title):
    if len(title) < MIN_TITLE_LENGTH:
        return 'Título muito curto'
    if len(title) > MAX_TITLE_LENGTH:
        return 'Título muito longo'
    return None


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400
    title_error = _validate_title(title)
    if title_error:
        return {'error': title_error}, 400

    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')

    if status not in VALID_STATUSES:
        return {'error': 'Status inválido'}, 400
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
    if user_id and not User.query.get(user_id):
        return {'error': 'Usuário não encontrado'}, 404
    if category_id and not Category.query.get(category_id):
        return {'error': 'Categoria não encontrada'}, 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = _parse_due_date(due_date)
        except ValueError:
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    commit()
    return task.to_dict(), 201


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        title_error = _validate_title(data['title'])
        if title_error:
            return {'error': title_error}, 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return {'error': 'Status inválido'}, 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < MIN_PRIORITY or data['priority'] > MAX_PRIORITY:
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            return {'error': 'Usuário não encontrado'}, 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            return {'error': 'Categoria não encontrada'}, 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = _parse_due_date(data['due_date'])
            except ValueError:
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    commit()
    return task.to_dict(), 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    db.session.delete(task)
    commit()
    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(query, status, priority, user_id):
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'),
                   Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in tasks.all()], 200


def task_stats():
    total = Task.query.count()
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
    stats = {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': Task.query.filter_by(status='done').count(),
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((Task.query.filter_by(status='done').count() / total) * 100, 2) if total > 0 else 0,
    }
    return stats, 200
