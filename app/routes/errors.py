from flask import render_template
from app import app

# Handles 404 Errors
@app.errorhandler(404)
def not_found_error(error):
    return "Not found!", 404

# Handles 500 errors  
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return "Internal Error!", 500