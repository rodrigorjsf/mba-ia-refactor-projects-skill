"""Reporting use cases (aggregation lives here, not in the routes)."""
from datetime import timedelta

from models.task import Task
from models.user import User, utcnow
from models.category import Category


def _completion_rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


def summary_report():
    all_tasks = Task.query.all()

    by_status = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    by_priority = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    now = utcnow()
    seven_days_ago = now - timedelta(days=7)
    recent_tasks = 0
    recent_done = 0

    # Group tasks per user in one pass (avoids the per-user N+1 query).
    per_user = {}
    for task in all_tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
        if task.priority in by_priority:
            by_priority[task.priority] += 1
        if task.is_overdue():
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (now - task.due_date).days,
            })
        if task.created_at and task.created_at >= seven_days_ago:
            recent_tasks += 1
        if task.status == 'done' and task.updated_at and task.updated_at >= seven_days_ago:
            recent_done += 1
        bucket = per_user.setdefault(task.user_id, {'total': 0, 'done': 0})
        bucket['total'] += 1
        if task.status == 'done':
            bucket['done'] += 1

    user_stats = []
    for user in User.query.all():
        bucket = per_user.get(user.id, {'total': 0, 'done': 0})
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': bucket['total'],
            'completed_tasks': bucket['done'],
            'completion_rate': _completion_rate(bucket['done'], bucket['total']),
        })

    report = {
        'generated_at': str(now),
        'overview': {
            'total_tasks': len(all_tasks),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': {
            'pending': by_status['pending'],
            'in_progress': by_status['in_progress'],
            'done': by_status['done'],
            'cancelled': by_status['cancelled'],
        },
        'tasks_by_priority': {
            'critical': by_priority[1],
            'high': by_priority[2],
            'medium': by_priority[3],
            'low': by_priority[4],
            'minimal': by_priority[5],
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return report, 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    report = {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': len(tasks),
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': _completion_rate(counts['done'], len(tasks)),
        },
    }
    return report, 200
