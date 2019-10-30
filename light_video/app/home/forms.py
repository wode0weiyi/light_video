#coding:utf8

from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError,Regexp,EqualTo
from app.models import User

class RegisterForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称')
        ],
        description='昵称',
        render_kw={
            'id':"input_name",
            'class':"form-control input-lg", 
            'placeholder':"昵称",
            'required':False
        }
    )
    # 邮箱
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱'),
            Email('邮箱格式不正确')
        ],
        description='邮箱',
        render_kw={
            'id':"input_email", 
            'class':"form-control input-lg", 
            'placeholder':"邮箱",
            'required':False
        }
    )
    # 手机
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机'),
            Regexp('1[3458]\\d{9}',message='手机号码格式不正确')
        ],
        description='手机号码',
        render_kw={
            'id':"input_phone", 
            'class':"form-control input-lg", 
            'placeholder':"手机",
            'required':False
        }
    )
    # 密码
    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码')
        ],
        description='密码',
        render_kw={
            'id':"input_password", 
            'class':"form-control input-lg",
            'placeholder':'密码',
            'required':False
        }
    )
    # 确认密码
    repwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('请确认密码'),
            EqualTo('pwd',message='两次密码不一致')
        ],
        description='确认密码',
        render_kw={
            'id':"input_repassword", 
            'class':"form-control input-lg",
            'placeholder':'确认密码',
            'required':False
        }
    )
    # 注册按钮
    register = SubmitField(
        label='注册',
        render_kw={
            'class':'btn btn-lg btn-success btn-block'
        }
    )

    # 验证昵称是否存在
    def validate_name(self,field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError('昵称已经存在')
    # 验证邮箱是否存在
    def validate_email(self,field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError('邮箱已经存在')
    # 验证手机是否存在
    def validate_phone(self,field):
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError('手机号已经存在')