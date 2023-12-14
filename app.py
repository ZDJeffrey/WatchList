from flask import Flask
from flask import url_for
from markupsafe import escape

app = Flask(__name__)

# 主页
@app.route('/')
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

# 用户页面
@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}' # 转义处理

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name='Jeffrey'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'Test page'





