from datetime import datetime

from flask import Blueprint, request, render_template, session, jsonify
from flask_login import login_required

from app.models import Order, House, User, Status

order = Blueprint('order', __name__)


@order.route('/order_detail/', methods=['GET'])
@login_required
def order_detail():
    return render_template('orders.html')


@order.route('/orders/', methods=['POST'])
@login_required
def orders():
    price = request.form.get('price')
    house_id = request.form.get('id')
    house = House.query.filter(House.id == house_id).first()
    if house.order_count:
        return jsonify({'code': 200, 'msg': '请求成功', 'failed': '该房间已被预订'})
    total_price = request.form.get('total')
    sd = request.form.get('sd')
    ed = request.form.get('ed')
    my_order = Order()
    d1 = datetime.strptime(sd, '%Y-%m-%d')
    d2 = datetime.strptime(ed, '%Y-%m-%d')
    delta = d2 - d1
    days = delta.days + 1
    my_order.house_id = int(house_id)
    my_order.user_id = int(session['user_id'])
    my_order.amount = int(total_price)
    my_order.house_price = int(price)
    my_order.begin_date = sd
    my_order.end_date = ed
    my_order.days = days
    house.order_count = 1
    house.add_update()
    my_order.add_update()
    return jsonify({'code': 200, 'msg': '请求成功', 'data': '创建订单成功'})


@order.route('/my_orders/', methods=['POST'])
@login_required
def my_orders():
    user_id = session['user_id']
    user = User.query.get(int(user_id))
    my_order = user.orders
    orders_list = []
    for i in my_order:
        orders_list.append(i.to_dict())
    return jsonify({'code': 200, 'msg': '请求成功', 'data': orders_list})


@order.route('/lorders/', methods=['GET'])
@login_required
def lorders():
    return render_template('lorders.html')


@order.route('/my_lorders/', methods=['POST'])
@login_required
def my_lorders():
    id = session['user_id']
    houses = House.query.filter(House.user_id == id).all()
    order_list = []
    for house in houses:
        orders = house.orders
        for o in orders:
            order_list.append(o.to_dict())
    return jsonify({'code': 200, 'msg': '请求成功', 'data': order_list})


@order.route('/receive/', methods=['POST'])
@login_required
def receive():
    order_id = request.form.get('order_id')
    order = Order.query.get(int(order_id))
    order.status = Status.WAIT_PAYMENT
    order.add_update()
    return jsonify({'code': 200, 'msg': '请求成功', 'data': order.to_dict()})


@order.route('/reject/', methods=['POST'])
@login_required
def reject():
    order_id = request.form.get('order_id')
    reason = request.form.get('reason')
    order = Order.query.get(int(order_id))
    order.status = Status.REJECTED
    order.reason = reason
    order.add_update()
    return jsonify({'code': 200, 'msg': '请求成功'})


@order.route('/comment/', methods=['POST'])
@login_required
def comment():
    order_id = request.form.get('order_id')
    comment = request.form.get('comment')
    order = Order.query.get(int(order_id))
    order.comment = comment
    order.add_update()
    return jsonify({'code': 200, 'msg': '请求成功'})


@order.route('/booking/<int:id>', methods=['GET'])
@login_required
def booking(id):
    session['house_id'] = id
    return render_template('booking.html')
