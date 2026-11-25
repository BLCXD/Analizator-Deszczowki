from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__)


@legal_bp.get('/privacy')
def privacy():
    return render_template('legal/privacy.html')


@legal_bp.get('/cookies')
def cookies():
    return render_template('legal/cookies.html')


@legal_bp.get('/terms')
def terms():
    return render_template('legal/terms.html')


@legal_bp.get('/eula')
def eula():
    return render_template('legal/eula.html')
