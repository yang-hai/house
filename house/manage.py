import redis
from flask import Flask, render_template
from flask_script import Manager
from flask_session import Session

from app.house_views import house
from app.order_views import order
from app.user_views import user, login_manage
from app.models import db

app = Flask(__name__)
app.register_blueprint(blueprint=user, url_prefix='/user')
app.register_blueprint(blueprint=order, url_prefix='/order')
app.register_blueprint(blueprint=house, url_prefix='/house')

app.secret_key = 'adbfHEGR38RY9EUFAJFH9Q8Y9hlkHFEEIWUHFIkjsfdkj1654646846468.,,2?'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host='39.108.75.156', port=6379, password='123456')
se = Session()
se.init_app(app)

login_manage.init_app(app)
login_manage.login_view = 'user.login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/house'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db.init_app(app)


manage = Manager(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    manage.run()
