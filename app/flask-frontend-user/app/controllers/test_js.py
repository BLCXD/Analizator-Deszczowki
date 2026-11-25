"""
JavaScript test controller - no authentication required.
"""
from flask import render_template
from app.controllers.base import create_blueprint

test_bp = create_blueprint('test_js', __name__)


@test_bp.route('/js-test')
def js_test():
                                                         
    return render_template('devices.html')


@test_bp.route('/js-test-simple')
def js_test_simple():
                                       
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>JS Test</title>
</head>
<body>
    <h1>JavaScript Test</h1>
    <div id="result">Waiting...</div>
    <script>
        alert('JavaScript is working!');
        document.getElementById('result').innerHTML = 'Success!';
    </script>
</body>
</html>
'''