from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from markupsafe import escape

from watchlist import app, db
from watchlist.models import User, Movie

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
