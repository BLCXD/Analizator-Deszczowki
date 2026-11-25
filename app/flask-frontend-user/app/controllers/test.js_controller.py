"""
Test controller for JavaScript testing.
"""
from flask import render_template
from app.controllers.base import create_blueprint

test_bp = create_blueprint('test', __name__)


@test_bp.route('/js-test')
def js_test():
                                      
    return render_template('test_js.html')