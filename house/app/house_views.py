import os
import uuid
from datetime import datetime

from flask import Blueprint, request, render_template, session, jsonify
from flask_login import login_required

from app.models import User, House, Facility, Area, HouseImage

house = Blueprint('house', __name__)


@house.route('/myhouse/', methods=['GET'])
@login_required
def myhouse():
    return render_template('myhouse.html')


@house.route('/myhouse_auth/', methods=['POST'])
@login_required
def myhouse_auth():
    id = session['user_id']
    user = User.query.get(id)
    houses_list = []
    if user.id_card:
        houses = user.houses
        if houses:
            for h in houses:
                houses_list.append(h.to_dict())
        return jsonify({'code': 200, 'msg': '请求成功', 'data': {'success': '已实名认证！', 'houses': houses_list}})
    return jsonify({'code': 200, 'msg': '请求成功', 'data': {'failed': '未实名认证'}})


@house.route('/upload_pic/<int:id>/', methods=['GET'])
@login_required
def upload_pic(id):
    if session.get('house_id'):
        del session['house_id']
    session['house_id'] = id
    return render_template('upload-pic.html')


@house.route('/my_upload_pic/', methods=['POST'])
@login_required
def my_upload_pic():
    id = session.get('house_id')
    del session['house_id']
    img = request.files.get('house_image')
    # 获取项目的根路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 获取媒体文件的路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    MEDIA_DIR = os.path.join(STATIC_DIR, 'media')
    # 随机生成图片的名称
    filename = str(uuid.uuid4())
    a = img.mimetype.split('/')[-1:][0]
    filename += '.' + a
    # 拼接图片的地址
    path = os.path.join(MEDIA_DIR, filename)
    # 保存
    img.save(path)
    houseimage = HouseImage()
    houseimage.house_id = id
    houseimage.url = filename
    houseimage.add_update()
    return jsonify({'code': 200, 'msg': '请求成功', 'success': '上传成功, 可继续上传！'})


@house.route('/detail/<int:id>/', methods=['GET'])
@login_required
def detail(id):
    if session.get('house_id'):
        del session['house_id']
    session['house_id'] = id
    return render_template('detail.html')


@house.route('/house_detail/', methods=['GET'])
@login_required
def house_detail():
    house_id = session['house_id']
    del session['house_id']
    house = House.query.get(int(house_id))
    user_id = session['user_id']
    if int(user_id) == house.user_id:
        return jsonify({'code': 200, 'msg': '请求成功', 'data': house.to_full_dict(), 'my': True})
    return jsonify({'code': 200, 'msg': '请求成功', 'data': house.to_full_dict()})


@house.route('/newhouse/', methods=['GET'])
@login_required
def newhouse():
    return render_template('newhouse.html')


@house.route('/newhouse_info/', methods=['POST'])
@login_required
def newhouse_info():
    facilitys = Facility.query.all()
    facilitys_list = []
    for facility in facilitys:
        facilitys_list.append(facility.to_dict())
    areas = Area.query.all()
    areas_list = []
    for area in areas:
        areas_list.append(area.to_dict())
    return jsonify({'code': 200, 'msg': '请求成功',
                    'data': {'facilitys_list': facilitys_list, 'areas_list': areas_list}})


@house.route('/my_newhouse/', methods=['POST'])
@login_required
def my_newhouse():
    title = request.form.get('title')
    price = request.form.get('price')
    area_id = request.form.get('area_id')
    address = request.form.get('address')
    room_count = request.form.get('room_count')
    acreage = request.form.get('acreage')
    unit = request.form.get('unit')
    capacity = request.form.get('capacity')
    beds = request.form.get('beds')
    deposit = request.form.get('deposit')
    min_days = request.form.get('min_days')
    max_days = request.form.get('max_days')
    facility = request.form.getlist('facility')
    house_image = request.files.get('user_image')
    if not all([title, price, area_id, address, room_count, acreage, unit,
                capacity, beds, deposit, min_days, max_days, facility, house_image]):
        return jsonify({'code': 200, 'msg': '请求成功', 'failed': '请将全部信息填写完整后再提交！'})
    # 获取项目的根路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 获取媒体文件的路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    MEDIA_DIR = os.path.join(STATIC_DIR, 'media')
    # 随机生成图片的名称
    filename = str(uuid.uuid4())
    a = house_image.mimetype.split('/')[-1:][0]
    filename += '.' + a
    # 拼接图片的地址
    path = os.path.join(MEDIA_DIR, filename)
    # 保存
    house_image.save(path)
    house = House()
    id = session['user_id']
    house.user_id = id
    house.title = title
    house.price = int(price)
    house.area_id = int(area_id)
    house.address = address
    house.acreage = int(acreage)
    house.room_count = int(room_count)
    house.unit = unit
    house.capacity = int(capacity)
    house.beds = beds
    house.deposit = int(deposit)
    house.min_days = int(min_days)
    house.max_days = int(max_days)
    house.index_image_url = filename
    for fac in facility:
        fac = int(fac)
        fac = Facility.query.get(fac)
        house.facilities.append(fac)
    house.add_update()
    return jsonify({'code': 200, 'msg': '请求成功', 'success': '发布房源成功！'})


@house.route('/search', methods=['GET'])
def search():
    aid = request.args.get('aid')
    sd = request.args.get('sd')
    ed = request.args.get('ed')
    sort_key = request.args.get('sortKey')
    session['aid'] = aid
    session['sd'] = sd
    session['ed'] = ed
    session['sortKey'] = sort_key
    return render_template('search.html')


@house.route('/appoint_search/', methods=['POST'])
def appoint_search():
    aid = session.get('aid')
    sd = session.get('sd')
    ed = session.get('ed')
    sort_key = session.get('sortKey')
    if aid:
        area = Area.query.get(int(aid))
        if sort_key:
            if sort_key == 'new':
                houses = area.houses
            elif sort_key == 'price-inc':
                houses = House.query.filter(House.area_id == aid).order_by('price')
            elif sort_key == 'price-des':
                houses = House.query.filter(House.area_id == aid).order_by('-price')
        else:
            houses = area.houses
    else:
        if sort_key:
            if sort_key == 'new':
                houses = House.query.all()
            elif sort_key == 'price-inc':
                houses = House.query.order_by('price')
            elif sort_key == 'price-des':
                houses = House.query.order_by('-price')
        else:
            houses = House.query.all()
    houses_list = []
    for house in houses:
        if house.order_count == 0:
            if house.max_days:
                d1 = datetime.strptime(sd, '%Y-%m-%d')
                d2 = datetime.strptime(ed, '%Y-%m-%d')
                delta = d2 - d1
                if delta.days < house.max_days:
                    houses_list.append(house.to_full_dict())
            else:
                houses_list.append(house.to_full_dict())
    areas = Area.query.all()
    areas_list = []
    for area in areas:
        areas_list.append(area.to_dict())
    return jsonify({'code': 200, 'msg': '请求成功', 'data': {'houses_list': houses_list, 'areas_list': areas_list}})


