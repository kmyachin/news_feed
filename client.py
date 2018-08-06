# encoding: utf-8

from random import randint
import os
from flask import Flask
from flask import current_app, render_template, session

class News:
    def __init__(self, id, user_id, ts, title, text):
       self.id = id
       self.user_id = user_id
       self.ts = ts
       self.title = title
       self.text = text

    def __str__(self):
        return "title: " + self.title + "\ntext: " + self.text

class LightNewsClient:
    def __init__(self):
        #self.user_id = randint(1,10)
        self.news_count = 0

    def load_from_file(self):
        from db import db
        db = db.get_db()
        with open(current_app.config['FILENAME'], 'r') as newsfeed:
            for line in newsfeed:
                args = line.split(';')
                if len(args) == 5:
                    #self.news.append(News(args[0], args[1], args[2], args[3], args[4]))
                    db.execute(
                        'INSERT INTO news (title, text) VALUES (?, ?)', (unicode(args[3], "utf-8"), unicode(args[4], "utf-8"))
                    )
                    self.news_count += 1
        db.commit()

    def get_news(self):
        from db import db
        db = db.get_db()
        if len(session['already_view']) > 0:
            where_str = " WHERE id not in (" + ",".join(session['already_view']) + ")"
        else:
            where_str = ""

        return db.execute(
                    "SELECT id, title, text FROM news" +  where_str + " limit 1"
                ).fetchone()

    @property
    def count(self):
        return self.news_count

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
            SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            FILENAME='./data/news.csv'
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from db import db
    db.init_app(app)

    with app.app_context():
        client = LightNewsClient()
        client.load_from_file()

    from . import auth, comments
    app.register_blueprint(auth.bp)
    app.register_blueprint(comments.bp)


    @app.route("/")
    def random_news():
        return client.news[randint(0,client.count-1)].title

    @app.route("/news/")
    def news():
        if 'already_view' not in session \
                or len(session['already_view']) == client.count:
            session['already_view']=[]

        news = client.get_news()

        session['already_view'].append(str(news['id']))
        session.modified = True
        return render_template("main.html", title=news['title'], text=news['text'])

    return app
