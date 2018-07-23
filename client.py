from random import randint
import os
from flask import Flask
from flask import render_template, session

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
        self.user_id = randint(1,10)
        self.filename = './data/news.csv'
        self.news = []

    def load_feed(self):
        with open(self.filename, 'r') as newsfeed:
            for line in newsfeed:
                args = line.split(';')
                if len(args) == 5:
                    self.news.append(News(args[0], args[1], args[2], args[3], args[4]))

    @property
    def news_count(self):
        return len(self.news)

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
            SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    client = LightNewsClient()
    client.load_feed()

    from db import db
    db.init_app(app)

    @app.route("/")
    def random_news():
        return client.news[randint(0,client.news_count-1)].title

    @app.route("/news/")
    def render():
        if 'already_view' not in session:
            session['already_view']=[]
            session.modified=True
        id = randint(0,client.news_count-1)
        if len(session['already_view']) == client.news_count:
            return "No more news"
        while id in session['already_view']:
            id = randint(0,client.news_count-1)
        session['already_view'].append(id)
        session.modified=True
        return render_template("main.html", title=unicode(client.news[id].title, "utf8"), text=unicode(client.news[id].text, "utf8"))

    @app.route("/logout")
    def logout():
        session.pop('already_view', None)
        return 'logout done'

    return app
