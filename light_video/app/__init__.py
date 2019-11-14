#coding:utf8
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template,url_for,redirect,Blueprint,request,flash)
import pymysql,os


app = Flask(__name__,static_url_path='/movieStatic')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:0shiwodeweiyi@106.12.180.188:3306/movie?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '12a5f98e9f314c4da8e05e2c4a656b98'
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/uploads/')
db = SQLAlchemy(app=app)

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint
from app.mobile import mobile as mobile_blueprint

import importlib,sys
importlib.reload(sys)

# 注册路由
app.register_blueprint(home_blueprint,url_prefix='/movie')
app.register_blueprint(admin_blueprint, url_prefix='/movie/admin')
app.register_blueprint(mobile_blueprint,url_prefix='/mobile')

@app.context_processor
def inject_url():
    data = {
        "url_for": dated_url_for,
    }
    return data

def dated_url_for(endpoint, **values):
    print(endpoint,values)
    if endpoint == 'movieStatic':
        filename = values.get('filename', None)
        if filename:
            endpoint = 'static'
            file_path = os.path.join(app.root_path, endpoint, filename)
            print(file_path)
            values['v'] = int(os.stat(file_path).st_mtime)  # 取文件最后修改时间的时间戳，文件不更新，则可用缓存
            return url_for(endpoint, **values)
    else:
        return url_for(endpoint,**values)

@app.errorhandler(404)
def page_not_fount(error):
    return render_template('404.html'), 404
