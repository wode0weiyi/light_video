#coding:utf8

from datetime import datetime
from app import db


# 会员
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  #编号
    name = db.Column(db.String(100), unique=True)  #名字
    pwd = db.Column(db.String(100))  #密码
    email = db.Column(db.String(100), unique=True)  #邮箱
    phone = db.Column(db.String(100), unique=True)  #电话
    info = db.Column(db.String(100))  #描述
    face = db.Column(db.String(255), unique=True)  #头像
    state = db.Column(db.Integer)# 状态（0冻结，1解冻）
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #注册时间
    uuid = db.Column(db.String(255), unique=True)  #唯一标识

    userlogs = db.relationship('Userlog', backref='user')  #userlog的外键关系
    comments = db.relationship('Comment', backref='user')  #评论外键关系
    moviecols = db.relationship('Moviecol', backref='user')  #收藏外键关系
    usernears = db.relationship('UserNear', backref='user') #最近登录用户外键关系

    def __repr__(self):
        return '<User %r>' % self.name

    # 验证密码是否正确
    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

# 会员登录日志
class Userlog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)  #编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  #日志用户id
    ip = db.Column(db.String(100))  #登录ip
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #登录时间

    def __repr__(self):
        return '<Userlog %r>' % self.id


# 标签（id，name，添加时间）
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)  #标签id
    name = db.Column(db.String(100), unique=True)  #标签名
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间
    movies = db.relationship('Movie', backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name


#电影的模型
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255), unique=True)
    star = db.Column(db.SmallInteger)
    playNum = db.Column(db.BigInteger)
    commenNum = db.Column(db.BigInteger)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    area = db.Column(db.String(100))
    release_time = db.Column(db.Date)
    length = db.Column(db.String(100))
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)

    comments = db.relationship('Comment', backref='movie')
    moviecols = db.relationship('Moviecol', backref='movie')

    def __repr__(self):
        return "<Movie %r>" % self.title


# 电影预告模型
class Preview(db.Model):
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)  #编号
    title = db.Column(db.String(100), unique=True)  #电影名
    # url = db.Column(db.String(255),unique=True)
    # info = db.Column(db.Text)
    logo = db.Column(db.String(255), unique=True)  #电影logo
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    def __repr__(self):
        return '<Preview %r>' % self.title


# 电影评论模型
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  #编号
    content = db.Column(db.Text)  #评论内容
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  #电影id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  #用户id
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间
    def __repr__(self):
        return '<Comment %r>' % self.id


# 收藏电影模型
class Moviecol(db.Model):
    __tablename__ = 'moviecol'
    id = db.Column(db.Integer, primary_key=True)  #编号
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  #电影id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  #用户ID
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    def __repr__(self):
        return '<Moviecol %r>' % self.id


#权限模型
class Auth(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)  #编号
    name = db.Column(db.String(100), unique=True)  #权限名
    url = db.Column(db.String(255), unique=True)  #权限url
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    def __repr__(self):
        return '<Auth %r>' % self.name


#角色模型
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)  #编号
    name = db.Column(db.String(100), unique=True)  #角色名
    auths = db.Column(db.String(600))  #权限列表
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    admins = db.relationship('Admin', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


#管理员模型
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)  #编号
    name = db.Column(db.String(100), unique=True)  #管理员账号
    pwd = db.Column(db.String(100))  #管理员密码
    is_super = db.Column(db.SmallInteger)  #是否为超级管理员， 0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  #所属角色
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    adminlogs = db.relationship('Adminlog', backref='admin')  #管理员登录日志外键关系
    oplogs = db.relationship('Oplog', backref='admin')  #管理员操作日志外键关系

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


#管理员登录日志
class Adminlog(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)  #编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  #所属管理员
    ip = db.Column(db.String(100))  #登录ip
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    def __repr__(self):
        return '<Adminlog %r>' % self.id


#管理员操作日志
class Oplog(db.Model):
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)  #编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  #所属管理员
    ip = db.Column(db.String(100))  #操作ip
    reason = db.Column(db.Text)  #操作原因
    addTime = db.Column(db.DateTime, index=True, default=datetime.now)  #添加时间

    def __repr__(self):
        return '<Oplog %r>' % self.id

# 最近登录用户表
class UserNear(db.Model):
    __tablename__ = 'user_near'
    id = db.Column(db.Integer,primary_key=True)
    userId = db.Column(db.Integer,db.ForeignKey('user.id'))
    

if __name__ == "__main__":
    pass
    # db.create_all()
    # 插入一个角色
    # role = Role(
    #     name="普通用户",
    #     auths="",
    # )
    # db.session.add(role)
    # db.session.commit()
    #添加管理员
    # from werkzeug.security import generate_password_hash  #密码hash加密
    # admin = Admin(name="huzhihui",
    #               pwd=generate_password_hash(b'123456'),
    #               is_super=0,
    #               role_id=1)
    # db.session.add(admin)
    # db.session.commit()
    # comment = Comment(
    #     content='第一条评论第一条评论第一条评论第一条评论第一条评论',
    #     movie_id=9,
    #     user_id=1
    # )
    # db.session.add(comment)
    # db.session.commit()