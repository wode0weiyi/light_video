#coding:utf8
from . import admin

from app.admin.forms import (LoginForm, TagForm, MovieForm, PreviewForm,
                             MemberForm,AdminForm)
from app.models import (Admin, Tag, Movie, Preview, User, Comment, Moviecol,
                        Adminlog, Oplog,Auth,Role)
from functools import wraps
from app import db, app
from flask import (render_template, redirect, url_for, flash, session, request,abort)
from werkzeug.utils import secure_filename
import os, uuid, datetime,json
from time import strftime
from wtforms.validators import ValidationError
from werkzeug.security import generate_password_hash


# 所有需要登录状态才能操作的接口装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 权限管理装饰器
def admin_auth(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        print('session',session['admin'])
        # 获取管理员信息
        admin = Admin.query.join(
            Role
        ).filter(
            # 匹配条件
            Role.id == Admin.role_id,
            Admin.name == session['admin']
        ).first_or_404()
        print('admin',admin)
        # 获取当前管理员的权限列表
        auths = admin.role.auths
        auths = list(map(lambda v: int(v), auths.split(',')))
        # 获取所有的权限auth实例数组
        auth_list = Auth.query.all()
        # 匹配当前管理员的权限
        urls = [v.url for v in auth_list for val in auths if v.id == val]

        # 获取当前连接接口
        # /admin/tag/delete/<int:id>
        rule = request.url_rule 
        # ['', 'admin', 'tag', 'delete', '<int:id>'] 
        rule = str(rule).split('/')
        # /tag 
        rule = '/' + str(rule[2])
        print('rule',rule,urls)
        # 如果请求的接口在管理员的权限列表里面
        if str(rule) not in urls:
            abort(404)
        return f(*args,**kwargs)
    return decorated_function

# 修改文件名称(时间+随机字符串)
def exchange_filename(filename, type='png'):
    fileinfo = os.path.splitext(filename)
    print(fileinfo)
    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(
        uuid.uuid4().hex) + fileinfo[-1]
    if type == 'mp4':
        filename = filename + '.mp4'
    return filename


@admin.route('/')
@admin_login_req
def index():
    username = session['admin']
    return render_template('/admin/index.html',username=username)


# 登录界面
@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        if not admin.check_pwd(data['pwd']):
            flash('密码错误')
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        # 登录操作，添加管理员登录日志
        ip = request.remote_addr
        adminlog = Adminlog(admin_id=admin.id, ip=ip)
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('/admin/login/login.html', form=form)


#登出界面
@admin.route('/logout')
@admin_login_req
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd')
@admin_login_req
def pwd():
    username = session['admin']
    return render_template('/admin/login/pwd.html',username=username)


# 标签添加
@admin.route('/tag/add', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def tag_add():
    username = session['admin']
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        # 查看标签库中是否存在标签
        tagCount = Tag.query.filter_by(name=data['tag_name']).count()
        if tagCount == 1:
            flash('标签已经存在！', 'error')
            return redirect(url_for('admin.tag_add'))
        # 如果库中不存在标签，则做入库操作
        tag = Tag(name=data['tag_name'])
        db.session.add(tag)
        db.session.commit()
        flash('添加成功', 'ok')
        # 添加标签操作添加日志
        dealOplog(data['tag_name'], 'addTag')
        return redirect(url_for('admin.tag_add'))
    return render_template('/admin/tag/tag_add.html', form=form,username=username)


# 标签编辑
@admin.route('/tag/edit/<int:id>', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def tag_edit(id=None):
    username = session['admin']
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        # 查看标签库中是否存在标签
        tagCount = Tag.query.filter_by(name=data['tag_name']).count()
        if tagCount == 1:
            flash('标签已经存在！', 'error')
            return redirect(url_for('admin.tag_edit', id=tag.id))
        # 如果库中不存在标签，则做入库操作
        tag.name = data['tag_name']
        db.session.commit()
        flash('修改成功', 'ok')
        dealOplog(data['tag_name'], 'upTag')
        return redirect(url_for('admin.tag_list', page=1))
    return render_template('/admin/tag/tag_edit.html', form=form, tag=tag,username=username)


# 标签删除
@admin.route('/tag/delete/<int:id>')
@admin_login_req
@admin_auth
def tag_delete(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('删除标签成功', 'ok')
    dealOplog(tag.name, 'rmTag')
    return redirect(url_for('admin.tag_list', page=1))


# 标签列表
@admin.route('/tag/list/<int:page>')
@admin_login_req
def tag_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Tag.query.order_by(Tag.addTime.desc()).paginate(page=page,
                                                                per_page=10)
    return render_template('/admin/tag/tag_list.html', page_data=page_data,username=username)


# 添加电影
@admin.route('/movie/add', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def movie_add():
    username = session['admin']
    form = MovieForm()
    if form.validate_on_submit():
        print(1111111111)
        data = form.data
        file_url = secure_filename(form.movie_file.data.filename)
        file_logo = secure_filename(form.movie_logo.data.filename)
        # 判断是否存在文件夹
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        url = exchange_filename(file_url, 'mp4')
        logo = exchange_filename(file_logo, 'png')
        form.movie_file.data.save(app.config['UP_DIR'] + url)
        form.movie_logo.data.save(app.config['UP_DIR'] + logo)
        movie = Movie(
            title=data['movie_title'],
            url=url,
            info=data['movie_info'],
            logo=logo,
            star=int(data['movie_star']),
            tag_id=int(data['movie_tag']),
            area=data['movie_area'],
            length=data['movie_length'],
            release_time=data['movie_releaseTime'],
            commenNum=0,
            playNum=0,
        )
        db.session.add(movie)
        db.session.commit()
        flash('电影添加成功！', 'ok')
        dealOplog(data['movie_title'], 'addMovie')
    return render_template('/admin/movie/movie_add.html', form=form,username=username)


# 电影列表
@admin.route('/movie/list/<int:page>', methods=['GET'])
@admin_login_req
def movie_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Movie.query.join(Tag).filter(Tag.id == Movie.tag_id).order_by(
        Movie.addTime.desc()).paginate(page=page, per_page=10)
    return render_template('/admin/movie/movie_list.html', page_data=page_data,username=username)


# 电影编辑
@admin.route('/movie/edit/<int:id>', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def movie_edit(id=None):
    username = session['admin']
    form = MovieForm()
    movie = Movie.query.get_or_404(id)
    # file和logo可以免验证
    form.movie_file.validators = []
    form.movie_logo.validators = []
    # 如果是get请求，表示获取数据，则对表单进行初始值赋值
    if request.method == 'GET':
        form.movie_star.data = movie.star
        form.movie_info.data = movie.info
        form.movie_tag.data = movie.tag_id
    # 表单提交验证
    if form.validate_on_submit():
        data = form.data
        movieCount = Movie.query.filter_by(title=data['movie_title']).count()
        if movieCount == 1 and movie.title != data['movie_title']:
            flash('电影名已经存在！', 'error')
            return redirect(url_for('admin.movie_edit', id=id))
        # 判断file和logo表单是否有值，有的话，则需要更换数据
        if form.movie_file.data.filename != '':
            file_url = secure_filename(form.movie_file.data.filename)
            movie.url = exchange_filename(file_url, 'mp4')
            form.movie_file.data.save(app.config['UP_DIR'] + movie.url)
        if form.movie_logo.data.filename != '':
            file_logo = secure_filename(form.movie_logo.data.filename)
            movie.logo = exchange_filename(file_logo, 'png')
            form.movie_logo.data.save(app.config['UP_DIR'] + movie.logo)
        # movie值改变
        movie.title = data['movie_title']
        movie.info = data['movie_info']
        movie.star = int(data['movie_star'])
        movie.tag_id = int(data['movie_tag'])
        movie.area = data['movie_area']
        movie.length = data['movie_length']
        movie.release_time = data['movie_releaseTime']
        print(movie.info)
        db.session.commit()
        flash('修改成功', 'ok')
        dealOplog(data['movie_title'], 'upMovie')
        return redirect(url_for('admin.movie_edit', id=id))
    return render_template('/admin/movie/movie_edit.html',
                           form=form,
                           movie=movie,
                           username=username)


# 电影删除
@admin.route('/movie/delete/<int:id>')
@admin_login_req
@admin_auth
def movie_delete(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    flash('删除电影成功！', 'ok')
    dealOplog(movie.title, 'rmMovie')
    return redirect(url_for('admin.movie_list', page=1))


# 电影预告添加
@admin.route('/preview/add', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def preview_add():
    username = session['admin']
    form = PreviewForm()
    if form.validate_on_submit():
        print('preview ------')
        data = form.data
        # logo文件名称安全处理
        preview_logo = secure_filename(form.preview_logo.data.filename)
        # 查询预告表中是否有相同标题的预告
        preview_count = Preview.query.filter_by(
            title=data['preview_title']).count()
        if preview_count == 1:
            flash('电影名称已经存在！', 'error')
            return redirect(url_for('admin.preview_add'))
        # 判断当前是否存在文件存储文件夹
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        logo = exchange_filename(preview_logo, 'png')
        form.preview_logo.data.save(app.config['UP_DIR'] + logo)
        # 写入数据库
        preview = Preview(
            title=data['preview_title'],
            logo=logo,
        )
        db.session.add(preview)
        db.session.commit()
        flash('添加预告电影成功', 'ok')
        dealOplog(data['preview_title'], 'addPreview')
    return render_template('/admin/movie/preview_add.html', form=form,username=username)


# 电影预告列表
@admin.route('/preview/list/<int:page>')
@admin_login_req
def preview_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Preview.query.order_by(Preview.addTime.desc()).paginate(
        page=page, per_page=5)
    return render_template('/admin/movie/preview_list.html',
                           page_data=page_data,
                           username=username)


# 电影预告编辑
@admin.route('/preview/edit/<int:id>')
@admin_login_req
@admin_auth
def preview_edit(id=None):
    username = session['admin']
    # 获取预告
    preview = Preview.query.filter_by(id=id).first_or_404()
    form = PreviewForm()
    # logo免验证
    form.preview_logo.validators = []
    if form.validate_on_submit():
        data = form.data
        # 判断当前的预告名是否在数据库中存在
        preview_count = Preview.query.filter_by(
            title=data['preview_title']).count()
        if preview_count == 1 and preview.title != data['preview_title']:
            flash('预告名已经存在!', 'error')
            return redirect(url_for('admin.preview_edit', id=id))
        # 判断当前的封面选择表单是否有值，有值表示修改过封面，需要做替换处理
        if form.preview_logo.data.filename != '':
            preview_logo = secure_filename(form.preview_logo.data.filename)
            preview.logo = exchange_filename(preview_logo, 'png')
            form.preview_logo.data.save(app.config['UP_DIR'] + preview.logo)
        preview.title = data['preview_title']
        db.session.commit()
        flash('修改预告成功!', 'ok')
        dealOplog(data['preview_title'], 'upPreview')
    return render_template('/admin/movie/preview_edit.html',
                           form=form,
                           preview=preview,
                           username=username)


# 电影预告删除
@admin.route('/preview/delete/<int:id>')
@admin_login_req
@admin_auth
def preview_delete(id=None):
    # 获取当前的preview
    preview = Preview.query.filter_by(id=id).first_or_404()
    # 删除掉当前的preview
    db.session.delete(preview)
    db.session.commit()
    flash('删除预告成功!', 'ok')
    dealOplog(preview.title, 'rmPreview')
    return redirect(url_for('admin.preview_list', page=1))


# 会员列表
@admin.route('/member/list/<int:page>')
@admin_login_req
def member_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = User.query.order_by(User.addTime.desc()).paginate(page=page,
                                                                  per_page=10)
    return render_template('/admin/user/member_list.html', page_data=page_data,username=username)


# 查看会员详情
@admin.route('/member/detail/<int:id>')
@admin_login_req
@admin_auth
def member_detail(id=None):
    username = session['admin']
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('/admin/user/member_detail.html', user=user,username=username)


# 会员编辑界面
@admin.route('/member/edit/<int:id>', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def member_edit(id=None):
    username = session['admin']
    form = MemberForm()
    data = form.data
    # logo跳过验证
    form.logo.validators = []
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == 'GET':
        form.info.data = user.info
    if form.validate_on_submit():
        # 判断是否需要验证当前昵称、邮箱、手机表单（如果这些参数和当前用户相同，则不需要验证是否存在，如果不同，则需要验证）
        if user.name != data['name']:
            user_count = User.query.filter_by(name=data['name']).count()
            if user_count == 1:
                flash('会员名已经存在！', 'error')
                return redirect(url_for('admin.member_edit', id=id))

        if user.email != data['email']:
            user_count = User.query.filter_by(email=data['email']).count()
            if user_count == 1:
                flash('邮箱已存在！', 'error')
                return redirect(url_for('admin.member_edit', id=id))

        if user.phone != data['phone']:
            user_count = User.query.filter_by(phone=data['phone']).count()
            if user_count == 1:
                flash('手机已存在！', 'error')
                return redirect(url_for('admin.member_edit', id=id))

        # 判断当前是否存在文件存储文件夹
        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        # 判断当前的头像是是否有值
        if form.logo.data.filename != '':
            member_face = secure_filename(form.logo.data.filename)
            user.face = exchange_filename(member_face)
            form.logo.data.save(app.config['UP_DIR'] + user.face)
        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.info = data['info']
        db.session.commit()
        flash('编辑会员成功', 'ok')
        dealOplog(data['name'], 'upUser')
    return render_template('/admin/user/member_edit.html',
                           form=form,
                           user=user,
                           username=username)


# 会员账号冻结/解冻(state:0表示冻结操作，1表示解冻操作)
@admin.route('/user/chengeState/<int:id>/<int:state>/<int:page>')
@admin_login_req
@admin_auth
def member_changeState(id=None, state=None, page=None):
    # 获取当前的user
    user = User.query.filter_by(id=id).first_or_404()
    if page == None:
        page = 1
    user.state = state
    db.session.commit()
    if state == 0:
        # 冻结操作
        dealOplog(user.name, 'freeze')
    else:
        # 解冻操作
        dealOplog(user.name, 'unfreeze')
    return redirect(url_for('admin.member_list', page=page))


# 会员账号删除
@admin.route('/user/delete/<int:id>')
@admin_login_req
@admin_auth
def member_delete(id=None):
    # 获取user
    user = User.query.filter_by(id=id).first_or_404()
    # 删除
    db.session.delete(user)
    db.session.commit()
    # 删除会员操作
    dealOplog(user.name, 'rmUser')
    return redirect(url_for('admin.member_list', page=1))


# 评论列表
@admin.route('/comment/list/<int:page>')
@admin_login_req
def comment_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Comment.query.join(Movie, User).filter(
        Movie.id == Comment.movie_id, User.id == Comment.user_id).order_by(
            Comment.addTime.desc()).paginate(page=page, per_page=10)
    return render_template('/admin/comment/comment_list.html',
                           page_data=page_data,
                           username=username)


# 删除评论
@admin.route('/comment/delete/<int:id>')
@admin_login_req
@admin_auth
def comment_delete(id=None):
    # 获取到评论
    comment = Comment.query.filter_by(id=id).first_or_404()
    # 数据库删除
    db.session.delete(comment)
    db.session.commit()
    flash('删除评论成功！', 'ok')
    # 删除评论操作日志
    dealOplog(comment.id, 'rmComment')
    return redirect(url_for('admin.comment_list', page=1))


# 收藏电影列表
@admin.route('/moviecol/list/<int:page>')
@admin_login_req
def moviecol_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Moviecol.query.join(Movie, User).filter(
        Movie.id == Moviecol.movie_id, Moviecol.user_id == User.id).order_by(
            Moviecol.addTime.desc()).paginate(page=page, per_page=10)
    return render_template('/admin/movie/moviecol_list.html',
                           page_data=page_data,username=username)


# 收藏电影删除
@admin.route('/moviecol/delete/<int:id>')
@admin_login_req
@admin_auth
def moviecol_delete(id=None):
    # 获取收藏电影数据
    moviecol = Moviecol.query.filter_by(id=id).first_or_404()
    # 数据库删除
    db.session.delete(moviecol)
    db.session.commit()
    flash('删除收藏电影成功！', 'ok')
    # 删除收藏电影操作
    dealOplog(moviecol.title, 'rmMoviecol')
    return redirect(url_for('admin.moviecol_list', page=1))


# 操作日志记录列表
@admin.route('/oplog/list/<int:page>')
@admin_login_req
def oplog_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Oplog.query.join(Admin).filter(
        Oplog.admin_id == Admin.id).order_by(Oplog.addTime.desc()).paginate(
            page=page, per_page=10)
    return render_template('/admin/log/oplog_list.html', page_data=page_data,username=username)


# 管理员登录日志列表
@admin.route('/adminlog/list/<int:page>')
@admin_login_req
def adminlog_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Adminlog.query.join(Admin).filter(
        Adminlog.admin_id == Admin.id).order_by(
            Adminlog.addTime.desc()).paginate(page=page, per_page=10)
    return render_template('/admin/log/adminlog_list.html',
                           page_data=page_data,username=username)


# 会员登录日志列表
@admin.route('/userlog/list')
@admin_login_req
def userlog_list():
    username = session['admin']
    return render_template('/admin/log/userlog_list.html',username=username)


# 添加权限
auths = [
        {'title':'标签管理','path':'/tag'},
        {'title':'电影管理','path':'/movie'},
        {'title':'预告管理','path':'/preview'},
        {'title':'会员管理','path':'/member'},
        {'title':'评论管理','path':'/comment'},
        {'title':'电影收藏','path':'/moviecol'},
        {'title':'日志管理','path':'/log'},
        {'title':'权限管理','path':'/auth'},
        {'title':'角色管理','path':'/role'},
        {'title':'管理员管理','path':'/admin'}
    ]
@admin.route('/auth/add', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def auth_add():
    username = session['admin']
    form = request.form
    authpath = request.values.get('authPath')
    authName = form.get('authName')
    if authName and authpath:
        auth = Auth(
            name=authName,
            url=authpath
        )
        db.session.add(auth)
        db.session.commit()
        flash('添加权限成功！', 'ok')
        return redirect(url_for( 'admin.auth_add' ))
    
    return render_template('/admin/user/auth_add.html', form=form, auths=auths,username=username)

# 权限列表
@admin.route('/auth/list/<int:page>')
@admin_login_req
def auth_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addTime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('/admin/user/auth_list.html', page_data=page_data,username=username)

# 权限编辑
@admin.route('/auth/edit/<int:id>')
@admin_login_req
@admin_auth
def auth_edit(id=None):
    username = session['admin']
    auth = Auth.query.filter_by(id=id).first_or_404()
    form = request.form
    # 获取权限名
    authName = form.get('authName')
    # 获取权限path
    authpath = request.values.get('authpath')
    if authName and authpath:
        auth.name = authName
        auth.url = authpath
        db.session.commit()
        flash('修改权限成功','ok')
        return redirect(url_for('admin.auth_list',page=1))
    return render_template('/admin/user/auth_edit.html',auth=auth,auths=auths,username=username)

    
# 权限删除
@admin.route('/auth/delete/<int:id>')
@admin_login_req
@admin_auth
def auth_delete(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash('删除成功','ok')
    return redirect(url_for('admin.auth_list', page=1))

# 添加角色
@admin.route('/role/add',methods=['GET','POST'])
@admin_login_req
@admin_auth
def role_add():
    username = session['admin']
    form = request.form
    rolename = form.get('rolename')
    role_auths = []
    print('form',form)
    if len(form) > 1:
        for item in form.items():
            print('item',item)
            if item[0] != 'rolename':
                auth_id = item[1]
                # 获取auth
                role_auths.append(auth_id)
        print('role_auths',role_auths)
        role = Role(
            name=rolename,
            auths=','.join(role_auths)
        )
        db.session.add(role)
        db.session.commit()
        flash('添加角色成功','ok')
        return redirect(url_for('admin.role_add'))
    # 获取所有的权限列表
    authList = Auth.query.order_by()
    return render_template('/admin/user/role_add.html',auths=authList,username=username)


# 角色列表
@admin.route('/role/list/<int:page>')
@admin_login_req
@admin_auth
def role_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Role.query.order_by(
        Role.addTime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('/admin/user/role_list.html',page_data=page_data,username=username)

# 编辑角色
@admin.route('/role/edit/<int:id>')
@admin_login_req
@admin_auth
def role_edit(id=None):
    username = session['admin']
    role = Role.query.filter_by(id=id).first_or_404()
    auths = Auth.query.all()
    selectedAuths = role.auths.split(',')
    role_auths=[]
    for item  in selectedAuths:
       role_auths.append(int(item))
    # print('role_auths',role_auths,auths[1].id)
    form = request.form
    reloName = form.get('rolename')
    role_auths = []
    print('form',form)
    if len(form) > 1:
        for item in form.items():
            print('item',item)
            if item[0] != 'rolename':
                auth_id = item[1]
                # 获取auth
                role_auths.append(auth_id)
        print('role_auths',role_auths)
        role.name = rolename
        role.auths = ','.join(role_auths)
        db.session.commit()
        flash('编辑角色成功','ok')
    return render_template('/admin/user/role_edit.html',
                            role=role, 
                            auths=auths,
                            selectedAuths=role_auths,
                            username=username)
    
# 删除角色
@admin.route('/role/delete/<int:id>')
@admin_login_req
@admin_auth
def role_delete(id=None):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    flash('删除角色成功','ok')
    return redirect(url_for('admin.role_list', page=1))

# 添加管理员
@admin.route('/admin/add',methods=['GET','POST'])
@admin_login_req
@admin_auth
def admin_add():
    username = session['admin']
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        # 判断当前的名字是否存在
        name = data['admin_name']
        pwd = data['admin_pwd']
        role_id = data['admin_role']
        # 密码加密
        pwd = generate_password_hash(pwd)
        # 存入数据库
        admin = Admin(
            name=name,
            pwd=pwd,
            role_id=role_id,
            is_super=0
        )
        db.session.add(admin)
        db.session.commit()
        flash('管理员添加成功！','ok')
        return redirect(url_for('admin.admin_add'))
    return render_template('/admin/user/admin_add.html',form=form,username=username)


# 管理员列表
@admin.route('/admin/list/<int:page>')
@admin_login_req
def admin_list(page=None):
    username = session['admin']
    if page == None:
        page = 1
    page_data = Admin.query.join(Role).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addTime.desc()
    ).paginate(page=page,per_page=10)
    return render_template('/admin/user/admin_list.html',page_data=page_data,username=username)


# 操作日志处理
def dealOplog(des, type):
    ip = request.remote_addr
    account = session['admin']
    admin = Admin.query.filter_by(name=account).first_or_404()
    admin_id = admin.id
    oplog = Oplog(
        ip=ip,
        admin_id=admin_id,
    )
    if type == 'addTag':
        # 添加标签
        oplog.reason = '添加一个标签：' + des
    elif type == 'rmTag':
        # 删除标签
        oplog.reason = '删除一个标签：' + des
    elif type == 'upTag':
        # 更新标签
        oplog.reason = '更新一个标签：' + des
    elif type == 'addMovie':
        # 添加电影
        oplog.reason = '添加电影：' + des
    elif type == 'rmMovie':
        # 删除电影
        oplog.reason = '删除电影：' + des
    elif type == 'upMovie':
        # 更新电影
        oplog.reason = '更新电影：' + des
    elif type == 'addPreview':
        # 添加预告
        oplog.reason = '添加预告：' + des
    elif type == 'rmPreview':
        # 删除预告
        oplog.reason = '删除预告：' + des
    elif type == 'upPreview':
        # 更新预告
        oplog.reason = '更新预告：' + des
    elif type == 'rmComment':
        # 删除评论
        oplog.reason = '删除评论：' + des
    elif type == 'rmUser':
        # 删除会员
        oplog.reason = '删除会员：' + des
    elif type == 'rmMoviecol':
        # 删除收藏电影
        oplog.reason = '删除收藏电影：' + des
    elif type == 'freeze':
        # 冻结会员账号
        oplog.reason = '冻结会员账号：' + des
    elif type == 'unfreeze':
        # 解冻会员账号
        oplog.reason = '解冻会员账号：' + des

    db.session.add(oplog)
    db.session.commit()
