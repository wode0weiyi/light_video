#coding:utf8

from app import app

if __name__ == "__main__":
    config = dict(
        debug=True,
        host='localhost',
        port=8000
    )
    app.run(**config)
    
    
