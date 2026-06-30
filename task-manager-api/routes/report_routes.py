"""Report + category routes (View layer): map HTTP -> controller, no logic."""
from flask import Blueprint, request, jsonify

from controllers import report_controller, category_controller

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    body, status = report_controller.summary_report()
    return jsonify(body), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    body, status = report_controller.user_report(user_id)
    return jsonify(body), status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    body, status = category_controller.list_categories()
    return jsonify(body), status


@report_bp.route('/categories', methods=['POST'])
def create_category():
    body, status = category_controller.create_category(request.get_json(silent=True))
    return jsonify(body), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    body, status = category_controller.update_category(cat_id, request.get_json(silent=True))
    return jsonify(body), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    body, status = category_controller.delete_category(cat_id)
    return jsonify(body), status
