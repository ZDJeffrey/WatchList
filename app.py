import os
import sys
import click
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape

app = Flask(__name__)

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

# MySQL数据库配置
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:182015@localhost:3306/movie_list?charset=utf8mb4'

# SQLite数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主键
    name = db.Column(db.String(20)) # 名字

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

# 主页
@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html',movies=movies)

# 用户页面
@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}' # 转义处理

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name='Jeffrey'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'Test page'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404 # 返回模板和状态码

@app.cli.command() # 注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.') # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    name = 'Jeffrey'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
        
    db.session.commit()
    click.echo('Done.')


