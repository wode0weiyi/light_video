from . import mobile
from sqlalchemy.orm import class_mapper
from flask import jsonify,redirect,render_template,request,session
from app import db
from app.models import User, Movie, Tag
from functools import wraps

# 数据模型转字典
def serialize(model):
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c,getattr(model,c)) for c in columns)

# 数据模型转json
def model_to_json(modelName):
    q = db.session.query(model).first()
    q_dict = serialize(q)
    dic = dict(
        code=200,
        msg='',
        data=q_dict
    )
    q_json = jsonify(dic)
    return q_json

# 登录验证装饰器
def mobile_login_req(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user' not in session:
            return redirect(url_for('mobile.login', next=request.url))
        return f(*args,**kwargs)
    return decorated_function

# 登录
@mobile.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args
    print(data)
    return render_template('/mobile/mobile.html')

# 退出登录
@mobile.route('/loginOut')
def loginOut():
    userName = session['user']
    if userName:
        session.pop('user')
    mobile.responseData('退出登录成功',200)

# 获取电影类型列表
@mobile.route('/tag/list')
def tag_list():
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args
    page = form.get('page')
    data = Tag.query.order_by(
        Tag.addTime.desc()
    ).paginate(page=page,per_page=10).items
    return mobile.responseData(data)