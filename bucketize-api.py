from waitress import serve

from app import app, db
from app.models.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Tasks':Task}

serve(app, listen='*:5000')