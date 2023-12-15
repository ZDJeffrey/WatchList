import os
import sys
import click
from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'

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
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # 主键
    name = db.Column(db.String(20)) # 名字
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份


# 主页
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        if not current_user.is_authenticated: # 如果当前用户未认证
            return redirect(url_for('index'))
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year)!=4 or len(title)>60:
            flash('Invalid input.') # 错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html',movies=movies)

# 用户页面
@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}' # 转义处理

# 电影编辑页面
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required # 用于视图保护，会验证用户是否登录
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method=='POST':
        # 获取表单数据
        title = request.form['title']
        year = request.form['year']
        # 验证数据
        if not title or not year or len(year)!=4 or len(title)>60:
            flash('Invalid input.') # 错误提示
            return redirect(url_for('edit',movie_id=movie_id)) # 重定向回当前编辑界面

        # 保存表单数据到数据库
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index')) # 重定向回主页
    return render_template('edit.html',movie=movie)

# 删除操作，只接收POST请求
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required # 用于视图保护，会验证用户是否登录
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

# 登录界面
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
         # 获取表单数据
        username = request.form['username']
        password = request.form['password']
        # 验证数据
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login')) # 重定向回登录界面
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 登录用户
            flash('Login success.')
            return redirect(url_for('index'))
    
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

# 退出账号
@app.route('/logout')
@login_required # 用于视图保护，会验证用户是否登录
def logout():
    logout_user() # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))

# 修改用户名
@app.route('/settings',methods=['GET','POST'])
@login_required # 用于视图保护，会验证用户是否登录
def settings():
    if request.method == 'POST':
        name = request.form['name']
        
        if not name or len(name)>20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        
        current_user.name = name # current_user 会返回当前登录用户的数据库记录对象
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')



# 上下文处理器
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

# 生成管理员
@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
def admin(username,password):
    """Create user."""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username,name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login' # 设置登录页面的端点

# 创建用户加载回调函数，接收用户ID作为参数
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user
