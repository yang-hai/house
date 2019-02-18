import os
import random
import re
import shutil
import uuid

from flask import Blueprint, request, render_template, jsonify, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, LoginManager
from werkzeug.security import check_password_hash

from app.models import User, Area

login_manage = LoginManager()
user = Blueprint('user', __name__)


# 生成随机验证码
def code():
    temp = ""
    for i in range(4):
        num = random.randrange(0, 3)
        if num == 0:
            rad = random.randrange(0, 10)
            temp = temp + str(rad)
        elif num == 1:
            rad = random.randrange(65, 91)
            c = chr(rad)
            temp = temp + c
        else:
            rad = random.randrange(97, 122)
            c = chr(rad)
            temp = temp + c
    return temp


# 手机号验证
def check_phone(phone):
    phone_pat = re.compile("^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$")
    while True:
        res = re.search(phone_pat, phone)
        if res:
            return True
        else:
            return False


@user.route('/index/', methods=['GET'])
def index():
    return render_template('index.html')


@user.route('/my_index/', methods=['GET', 'POST'])
def my_index():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return jsonify({'code': 200, 'msg': '请求成功', 'data': user.name})
        return jsonify({'code': 1001, 'msg': '请求成功'})
    if request.method == 'POST':
        areas = Area.query.all()
        areas_list = []
        for area in areas:
            areas_list.append(area.to_dict())
        return jsonify({'code': 1001, 'msg': '请求成功', 'data': areas_list})


@user.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        tel = request.form.get('mobile')
        pwd = request.form.get('password')
        pwd2 = request.form.get('password2')
        phone_error = ''
        password_error = ''
        user = User.query.filter(User.phone == tel).first()
        if not check_phone(tel):
            phone_error = '请输入正确的手机号！'
        if user:
            phone_error = '手机号已注册！'
        if len(pwd) < 6 and len(pwd2) < 6 or pwd != pwd2:
            password_error = '密码少于6位或密码不一致！'
        if phone_error or password_error:
            return jsonify({'code': 200, 'msg': '请求成功',
                            'data': {'phone_error': phone_error, 'password_error': password_error}})
        u = User()
        u.phone = tel
        u.password = pwd
        u.name = tel
        u.save()
        return jsonify({'code': 200, 'msg': '请求成功', 'data': {'success': '注册成功！'}})


@user.route('/auth_code/', methods=['POST'])
def auth_code():
    if request.method == 'POST':
        four_code = code()
        return jsonify({'code': 200, 'msg': '请求成功', 'data': four_code})


@user.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        tel = request.form.get('mobile')
        pwd = request.form.get('password')
        phone_error = ''
        password_error = ''
        user = User.query.filter(User.phone == tel).first()
        if not user:
            if not check_phone(tel):
                phone_error = '请输入正确的手机号！'
            else:
                phone_error = '手机号未注册！'
            if len(pwd) < 6:
                password_error = '密码少于6位！'
        else:
            if len(pwd) < 6:
                password_error = '密码少于6位！'
            else:
                if not check_password_hash(user.pwd_hash, pwd):
                    password_error = '密码错误！'
        if phone_error or password_error:
            return jsonify({'code': 200, 'msg': '请求成功',
                            'data': {'phone_error': phone_error, 'password_error': password_error}})
        login_user(user)
        return jsonify({'code': 200, 'msg': '请求成功', 'data': {'success': '登录成功！'}})


@user.route('/my/', methods=['GET'])
@login_required
def my():
    return render_template('my.html')


@user.route('/my_info/', methods=['GET'])
@login_required
def my_info():
    id = session.get('user_id')
    user = User.query.filter(User.id == id).first()
    user_dict = user.to_basic_dict()
    return jsonify({'code': 200, 'msg': '请求成功', 'data': user_dict})


@user.route('/logout/', methods=['GET'])
@login_required
def logout():
    if request.method == 'GET':
        logout_user()
        return redirect(url_for('user.login'))


@login_manage.user_loader
def load_user(user_id):
    # 定义被login_manage装饰的回调函数
    # 返回的是当前登陆系统的用户对象
    return User.query.filter(User.id == user_id).first()


@user.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        return render_template('profile.html')
    if request.method == 'POST':
        avatar = request.files.get('avatar')
        username = request.form.get('username')
        id = session.get('user_id')
        user = User.query.get(id)
        if avatar:
            # 获取项目的根路径
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # 获取媒体文件的路径
            STATIC_DIR = os.path.join(BASE_DIR, 'static')
            MEDIA_DIR = os.path.join(STATIC_DIR, 'media')
            # 随机生成图片的名称
            filename = str(uuid.uuid4())
            a = avatar.mimetype.split('/')[-1:][0]
            filename += '.' + a
            # 拼接图片的地址
            path = os.path.join(MEDIA_DIR, filename)
            # 保存
            avatar.save(path)
            user.avatar = filename
            user.save()
            return jsonify({'code': 200, 'msg': '请求成功', 'data': filename})
        if len(username) < 30:
            u = User.query.filter(User.name == username).first()
            if not u:
                user.name = username
                user.save()
                return jsonify({'code': 200, 'msg': '请求成功', 'data': {'success': '更改成功！'}})
        return jsonify({'code': 200, 'msg': '请求成功', 'data': {'failed': '名字已存在或超过30字符！'}})


@user.route('/auth/', methods=['GET', 'POST'])
@login_required
def auth():
    if request.method == 'GET':
        return render_template('auth.html')
    if request.method == 'POST':
        real_name = request.form.get('real_name')
        card = request.form.get('id_card')
        if real_name and card:
            if len(card) <= 18 and len(real_name) <= 30:
                user = User.query.filter(User.id_card == card).first()
                if not user:
                    id = session['user_id']
                    u = User.query.get(id)
                    u.id_name = real_name
                    u.id_card = card
                    u.save()
                    return jsonify({'code': 200, 'msg': '请求成功', 'data': {'success': '认证成功！'}})
                else:
                    return jsonify({'code': 200, 'msg': '请求成功', 'data': {'failed': '认证失败，该号码已绑定！'}})
            else:
                return jsonify({'code': 200, 'msg': '请求成功', 'data': {'failed': '认证失败，名字或身份证号码长度太长！'}})
        else:
            return jsonify({'code': 200, 'msg': '请求成功', 'data': {'failed': '认证失败，请完善信息！'}})


@user.route('/my_auth/', methods=['GET'])
@login_required
def my_auth():
    id = session.get('user_id')
    user = User.query.get(id)
    user_dict = user.to_auth_dict()
    return jsonify({'code': 200, 'msg': '请求成功', 'data': user_dict})
