from flask import (
    Blueprint, g, url_for, redirect, request, render_template
)

from auth import login_required
from db.db import get_db

bp = Blueprint('comment', __name__)

@bp.route('/<int:news_id>/create', methods=('GET','POST'))
@login_required
def create(news_id):
    if request.method == 'POST':
        text = request.form['text']

        db = get_db()
        db.execute(
            'INSERT INTO comments (news_id, user_id, text) VALUES (?, ?, ?)', (news_id, g.user['id'], text)
        )
        db.commit()
        return redirect(url_for('news'))

    return render_template('comments/create.html')