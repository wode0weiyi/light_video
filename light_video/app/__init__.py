#coding:utf8
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template)
import pymysql,os


app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:0shiwodeweiyi@106.12.180.188:3306/movie?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '12a5f98e9f314c4da8e05e2c4a656b98'
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/uploads/')
db = SQLAlchemy(app=app)

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint
from app.mobile import mobile as mobile_blueprint

# 注册路由
app.register_blueprint(home_blueprint,url_prefix='/movie')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(mobile_blueprint,url_prefix='/mobile')

@app.errorhandler(404)
def page_not_fount(error):
    return render_template('404.html'), 404
