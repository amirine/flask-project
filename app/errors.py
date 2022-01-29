from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """Custom page for 404 error"""

    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom page for 500 error"""

    db.session.rollback()
    return render_template('500.html'), 500
