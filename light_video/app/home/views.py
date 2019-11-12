#coding:utf8

from . import home
from flask import (render_template, redirect, flash)
from app import app, db
from app.home.forms import RegisterForm
from app.models import User, Movie, Tag,UserNear
from werkzeug.security import generate_password_hash
import uuid
import sqlalchemy


#首页路由
# tagid 标签id
# starid 星级id
# playNum 播放数量，1为从高到低 2为从低到高
# commentNum 评论数量 1为从高到低 2为从低到高
@home.route('/')
@home.route('/<int:tagid>/<int:star>/<int:playNum>/<int:commentNum>/<int:page>'
            )
def index(tagid=0, star=0, playNum=0, commentNum=0, page=None):
    # 获取标签
    tags = Tag.query.all()
    if playNum == 0 and commentNum == 0:
        filters = sqlalchemy.text('')
    elif playNum == 0 and commentNum != 0:
        filters = Movie.commenNum.desc() if (
            commentNum == 1) else Movie.commenNum
    elif playNum != 0 and commentNum == 0:
        filters = Movie.playNum.desc() if (playNum == 1) else Movie.playNum

    if page == None:
        page = 1
    page_data = Movie.query.filter(
        (Movie.tag_id == tagid) if (tagid != 0) else sqlalchemy.text(''),
        (Movie.star == star) if
        (star != 0) else sqlalchemy.text('')).order_by(filters).paginate(
            page=page, per_page=16)
    print('page_data', page_data.items)
    return render_template('/home/index.html', page_data=page_data, tags=tags)


# 登录路由
@home.route('/login')
def login():
    # 登录成功，保存当前的用户信息在本地
    return render_template('/home/login.html')


#登出路由
@home.route('/logout')
def logout():
    return redirect('/login')


#注册路由
@home.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        pwd = data['pwd']
        user = User(name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    pwd=generate_password_hash(pwd),
                    uuid=uuid.uuid4().hex)
        db.session.add(user)
        db.session.commit()
        flash('注册成功', 'ok')
    return render_template('/home/register.html', form=form)


# 会员中心


@home.route('/user/<int:userId>')
def user(userId=0):
    user = None
    
    if (userId != 0 and id != None):
        # 获取会员
        user = User.query.filter_by(id=userId).first_or_404()
    else:
        # 获取最近登录的用户id
        userid = UserNear.query.order_by().first_or_404()
        user = User.query.filter_by(id=userid).first_or_404()

    return render_template('/home/userCenter/user.html', user=user)


# 修改密码
@home.route('/pwd')
def pwd():
    return render_template('/home/userCenter/pwd.html')


# 评论
@home.route('/comment')
def comment():
    return render_template('/home/userCenter/comment.html')


# 登录日志
@home.route('/loginlog')
def loginlog():
    return render_template('/home/userCenter/loginlog.html')


# 收藏电影
@home.route('/moviecol')
def moviecol():
    return render_template('/home/userCenter/moviecol.html')


# 电影页头部轮播路由
@home.route('/animation')
def animation():
    return render_template('/home/movie/animation.html')


# 搜索页
@home.route('/search')
def search():
    return render_template('/home/movie/search.html')


#电影播放页
@home.route('/play')
def play():
    return render_template('/home/movie/play.html')
