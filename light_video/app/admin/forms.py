#coding:utf8
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, Regexp, EqualTo
from app.models import Admin, Tag, User, Role
from wtforms import (StringField, PasswordField, SubmitField, FileField,
                     SelectField, TextAreaField, RadioField)

tags = Tag.query.all()
roles = Role.query.all()


class LoginForm(FlaskForm):
    # 管理员登录表单
    account = StringField(
        label='账号',  #标签
        validators=[DataRequired('请输入账号')],  #验证字段
        description='账号',  #描述
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入账号',
            'required': False  #不设置false，会默认required
        }  #属性值
    )
    pwd = PasswordField(label='密码',
                        validators=[DataRequired('请输入密码')],
                        description='密码',
                        render_kw={
                            'class': 'form-control',
                            'placeholder': '请输入密码',
                            'required': False
                        })
    submit = SubmitField(
        '登录', render_kw={'class': 'btn btn-primary btn-block btn-flat'})

    # 验证账号是否存在
    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError('账号不存在')


# 标签表单
class TagForm(FlaskForm):
    # 标签输入框
    tag_name = StringField(label='标签',
                           validators=[DataRequired('请输入标签')],
                           description='标签',
                           render_kw={
                               'class': "form-control",
                               'id': "input_name",
                               'placeholder': "请输入标签名称！",
                               'required': False
                           })
    # 提交按钮
    tag_submit = SubmitField(label='添加',
                             render_kw={'class': "btn btn-primary"})
    # 修改按钮
    tag_update = SubmitField(label='修改',
                             render_kw={'class': "btn btn-primary"})


# 添加电影表单
class MovieForm(FlaskForm):
    # 标题
    movie_title = StringField(label='片名',
                              validators=[DataRequired('请输入片名')],
                              description='片名',
                              render_kw={
                                  'class': "form-control",
                                  'id': "input_title",
                                  'placeholder': "请输入片名！",
                                  'required': False
                              })
    # file
    movie_file = FileField(label='文件',
                           validators=[
                               DataRequired('请选择文件'),
                           ],
                           description='文件',
                           render_kw={
                               'id': 'input_url',
                               'required': False
                           })
    # 简介info
    movie_info = TextAreaField(label='简介',
                               validators=[DataRequired('请输入电影介绍')],
                               description='电影简介',
                               render_kw={
                                   'class': "form-control",
                                   'rows': "10",
                                   'id': "input_info",
                                   'required': False
                               })
    # 封面logo
    movie_logo = FileField(label='封面',
                           validators=[DataRequired('请选择封面')],
                           description='封面',
                           render_kw={
                               'id': 'input_logo',
                               'required': False
                           })
    # 星级star
    movie_star = SelectField(label='星级',
                             validators=[DataRequired('请选择星级')],
                             description='星级',
                             coerce=int,
                             choices=[(1, '1星'), (2, '2星'), (3, '3星'),
                                      (4, '4星'), (5, '5星')],
                             render_kw={
                                 'class': "form-control",
                                 'id': "input_star"
                             })
    # 标签 tag_id
    movie_tag = SelectField(label='标签',
                            validators=[DataRequired('请选择标签')],
                            description='标签',
                            coerce=int,
                            choices=[(t.id, t.name) for t in tags],
                            render_kw={
                                'class': "form-control",
                                'id': "input_tag_id"
                            })
    # 地区area
    movie_area = StringField(label='地区',
                             validators=[DataRequired('请输入地区')],
                             description='地区',
                             render_kw={
                                 'class': "form-control",
                                 'id': "input_area",
                                 'placeholder': "请输入地区！",
                                 'required': False
                             })
    # 片长 length
    movie_length = StringField(label='片长',
                               validators=[DataRequired('请输入片长')],
                               description='片长',
                               render_kw={
                                   'class': "form-control",
                                   'id': "input_length",
                                   'placeholder': "请输入片长！",
                                   'required': False
                               })
    # 上映时间 release_time
    movie_releaseTime = StringField(label='上映时间',
                                    validators=[DataRequired('请选择上映时间')],
                                    description='上映时间',
                                    render_kw={
                                        'class': "form-control",
                                        'id': "input_release_time",
                                        'placeholder': "请选择上映时间！",
                                        'required': False
                                    })
    # 添加电影
    movie_submit = SubmitField(label='添加',
                               render_kw={'class': 'btn btn-primary'})
    # 修改电影
    movie_editBtn = SubmitField(label='修改',
                                render_kw={'class': 'btn btn-primary'})


# 电影预告表单
class PreviewForm(FlaskForm):
    # 预告标题
    preview_title = StringField(label='预告标题',
                                validators=[DataRequired('请输入预告标题')],
                                description='预告标题',
                                render_kw={
                                    'class': "form-control",
                                    'id': "input_title",
                                    "placeholder": "请输入预告标题！",
                                    'required': False
                                })
    # 预告封面
    preview_logo = FileField(label='预告封面',
                             validators=[DataRequired('请选择预告封面')],
                             description='预告封面',
                             render_kw={
                                 'id': 'input_logo',
                                 'required': False
                             })
    # 提交按钮
    preview_submit = SubmitField(label='添加',
                                 render_kw={'class': 'btn btn-primary'})

    # 修改按钮
    preview_edit = SubmitField(label='修改',
                               render_kw={'class': 'btn btn-primary'})


# 会员编辑表单
class MemberForm(FlaskForm):
    # 昵称
    name = StringField(label='昵称',
                       validators=[DataRequired('请输入昵称')],
                       description='昵称',
                       render_kw={
                           'class': 'form-control',
                           'placeholder': '昵称',
                           'required': False
                       })
    # 邮箱
    email = StringField(label='邮箱',
                        validators=[DataRequired('请输入邮箱'),
                                    Email('邮箱格式不正确')],
                        description='邮箱',
                        render_kw={
                            'class': "form-control",
                            'placeholder': "邮箱",
                            'required': False
                        })
    # 手机
    phone = StringField(label='手机',
                        validators=[
                            DataRequired('请输入手机'),
                            Regexp('1[3458]\\d{9}', message='手机格式不正确')
                        ],
                        description='手机',
                        render_kw={
                            'class': "form-control",
                            'placeholder': "手机",
                            'required': False
                        })
    # 头像
    logo = FileField(label='头像',
                     validators=[DataRequired('请选择头像')],
                     description='头像',
                     render_kw={
                         'id': 'input_logo',
                         'required': False
                     })
    # 简介
    info = TextAreaField(label='简介',
                         validators=[DataRequired('请输入简介')],
                         description='简介',
                         render_kw={
                             'class': "form-control",
                             'rows': "10",
                             'id': "input_info",
                             'required': False
                         })
    # 提交按钮
    submit = SubmitField(label='编辑', render_kw={'class': 'btn btn-primary'})

    # # 验证昵称是否存在
    # def validate_name(self,field):
    #     print('self=',self)
    #     name = field.data
    #     user = User.query.filter_by(name=name).count()
    #     if user == 1:
    #         raise ValidationError('昵称已经存在')
    # # 验证邮箱是否存在
    # def validate_email(self,field):
    #     email = field.data
    #     user = User.query.filter_by(email=email).count()
    #     if user == 1:
    #         raise ValidationError('邮箱已经存在')
    # # 验证手机是否存在
    # def validate_phone(self,field):
    #     phone = field.data
    #     user = User.query.filter_by(phone=phone).count()
    #     if user == 1:
    #         raise ValidationError('手机号已经存在')


# 管理员表单
class AdminForm(FlaskForm):
    admin_name = StringField(label='管理员名称',
                             validators=[DataRequired('请输入管理员名称！')],
                             description='管理员名称',
                             render_kw={
                                 'class': "form-control",
                                 'id': "input_name",
                                 "placeholder": "请输入管理员名称！",
                                 'required': False
                             })
    admin_pwd = PasswordField(label='管理员密码',
                              validators=[DataRequired('请输入管理员密码！')],
                              description='管理员密码',
                              render_kw={
                                  'type': "password",
                                  'class': "form-control",
                                  'id': "input_pwd",
                                  "placeholder": "请输入管理员重复密码！",
                                  'required': False
                              })
    admin_repwd = PasswordField(label='确认管理员密码',
                                validators=[
                                    DataRequired('请确认管理员密码！'),
                                    EqualTo('admin_pwd', message='两次密码不一致')
                                ],
                                description='确认管理员密码',
                                render_kw={
                                    'type': "password",
                                    'class': "form-control",
                                    'id': "input_re_pwd",
                                    "placeholder": "请确认管理员重复密码！",
                                    'required': False
                                })
    admin_role = SelectField(label='所属角色',
                             validators=[DataRequired('请选择所属角色')],
                             description='所属角色',
                             choices=[(r.id, r.name) for r in roles],
                             coerce=int,
                             render_kw={
                                 'class': "form-control",
                                 'id': "input_role_id"
                             })
    admin_submit = SubmitField(label='添加',
                               render_kw={'class': 'btn btn-primary'})
                    
    def validate_admin_name(self,field):
        name = field.data
        count = Admin.query.filter_by(name=name).count()
        if count == 1:
            raise ValidationError('管理员名字已经存在')

