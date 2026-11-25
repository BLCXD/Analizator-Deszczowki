"""
Simple test controller for testing JavaScript.
"""
from flask import render_template
from app.controllers.base import create_blueprint

simple_test_bp = create_blueprint('simple_test', __name__)


@simple_test_bp.route('/simple_test')
def simple_test():
                           
    return render_template('simple_test.html')