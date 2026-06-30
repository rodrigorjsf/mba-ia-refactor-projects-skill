"""Category use cases."""
from database import db, commit
from models.category import Category
from models.task import Task

DEFAULT_COLOR = '#000000'


def list_categories():
    result = []
    for category in Category.query.all():
        data = category.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=category.id).count()
        result.append(data)
    return result, 200


def create_category(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400
    name = data.get('name')
    if not name:
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_COLOR)

    db.session.add(category)
    commit()
    return category.to_dict(), 201


def update_category(cat_id, data):
    category = Category.query.get(cat_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404

    data = data or {}
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    commit()
    return category.to_dict(), 200


def delete_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404
    db.session.delete(category)
    commit()
    return {'message': 'Categoria deletada'}, 200
