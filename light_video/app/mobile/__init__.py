from flask import Blueprint, make_response

mobile = Blueprint('mobile',__name__)

import app.mobile.views

# 转化数据类型为可返回类型
def dataChange(data):
    if isinstance(data,int):
        return data    
    elif isinstance(data,float):
        return data   
    elif isinstance(data,str):
        return data
    elif isinstance(data,list):
        l = []
        for item in data:
            l.append(dataChange(item))
        return l
    elif isinstance(data,tuple):
        l = []
        for item in data:
            l.append(dataChange(item))
        return l
    elif isinstance(data,set):
        l = []
        for item in data:
            l.append(dataChange(item))
        return l
    elif isinstance(data,dict):
        d = {}
        for key,value in data.items():
            d[key] = dataChange(value)
        return d
    elif isinstance(data, object):
        return data.__dict__
    else:
        return data

def responseData(data,code=200):
    if code == 200:
        body = {
            'code':200,
            'data':dataChange(data)
        }
    else:
        body={
            'code':code,
            'data':dataChange(data)
        }
    # 构造response
    response = make_response(body)
    return response