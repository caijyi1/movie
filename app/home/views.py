# coding:utf8
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegistForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from app import db, app
from app.models import User, Userlog, Comment, Moviecol, Movie, Preview, Tag
from datetime import datetime
import uuid,os


# 登录装饰器
def login_required(f):
	@wraps(f)
	def decorated_function(*args,**kw):
		if "user" not in session:
			return  redirect(url_for("home.login", next=request.url))
		return f(*args,**kw)
	return decorated_function

# 修改文件名称
def change_filename(filename):
	fileinfo = os.path.splitext(filename)
	filename = datetime.now().strftime("%Y%m%d%H%M%S")+str(uuid.uuid4().hex)+fileinfo[-1]
	return filename

# 前台登录
@home.route("/login/", methods=["GET","POST"])
def login():
	if "user" in session:
		flash("你已经登录!","ok")
		return redirect(url_for("home.user"))
	form = LoginForm()
	if form.validate_on_submit():
		data = form.data
		user = User.query.filter_by(name=data["name"]).first()
		if not user.check_pwd(data["pwd"]):
			flash("用户名或密码错误！", "err")
			return redirect(url_for("home.login"))
		session["user"] = user.name
		session["user_id"] = user.id
		userlog = Userlog(
			user_id = user.id,
			ip = request.remote_addr
			)
		db.session.add(userlog)
		db.session.commit()
		return redirect(url_for("home.user"))
	return render_template("home/login.html", form=form)

# 前台登出
@home.route("/logout/")
@login_required
def logout():
	session.pop("user", None)
	session.pop("user_id", None)
	return redirect(url_for("home.login"))

# 前台注册
@home.route("/regist/", methods=["GET","POST"])
def regist():
	form = RegistForm()
	if form.validate_on_submit():
		data = form.data
		user = User(
			name = data['name'],
			email = data["email"],
			phone = data["phone"],
			pwd = generate_password_hash(data["pwd"]),
			uuid = uuid.uuid4().hex	
			)
		db.session.add(user)
		db.session.commit()
		flash("注册成功！", "ok")
		return redirect(url_for('home.login'))
	return render_template("home/regist.html", form=form)

# 用户详情修改页面
@home.route("/user/", methods=["GET","POST"])
@login_required
def user():
	form = UserdetailForm()
	user = User.query.get(int(session["user_id"]))
	form.face.validators = []
	if request.method == "GET":
		form.info.data = user.info
	if form.validate_on_submit():
		data = form.data

		# 判断是否修改成已经存在过的值，确保唯一
		if data["email"] != user.email and User.query.filter_by(email=data["email"]).count() == 1:
			flash("邮箱已经存在！", "err")
			return redirect(url_for('home.user'))

		if data["phone"] != user.phone and User.query.filter_by(phone=data["phone"]).count() == 1:
			flash("手机已经存在！", "err")
			return redirect(url_for('home.user'))

		user.name = session["user"]
		user.email = data["email"]
		user.phone = data["phone"]
		user.info = data["info"]

		if form.face.data.filename:
			user.face = change_filename(secure_filename(form.face.data.filename))
			form.face.data.save(app.config["FC_DIR"]+user.face)

		db.session.add(user)
		db.session.commit()
		flash("保存修改成功！", "ok")
		return redirect(url_for("home.user"))

	return render_template("home/user.html", form=form, user=user)

# 更改密码
@home.route("/pwd/", methods=["GET","POST"])
@login_required
def pwd():
	form = PwdForm()
	if form.validate_on_submit():
		data = form.data
		user = User.query.filter_by(name=session["user"]).first()
		from werkzeug.security import generate_password_hash
		user.pwd = generate_password_hash(data["new_pwd"])
		db.session.add(user)
		db.session.commit()
		flash("修改密码成功，请重新登录！", "ok")
		return redirect(url_for('home.login'))
	return render_template("home/pwd.html", form=form)

# 评论列表
@home.route("/comments/<int:page>", methods=["GET"])
@login_required
def comments(page):
	page_data = Comment.query.join(
		User).filter(
		Comment.user_id == int(session["user_id"])
		).order_by(
		Comment.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("home/comments.html", page_data=page_data)

@home.route("/loginlog/<int:page>", methods=["GET"])
@login_required
def loginlog(page):
	page_data = Userlog.query.filter_by(
		user_id = int(session["user_id"])
		).order_by(
		Userlog.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("home/loginlog.html", page_data=page_data)

# 添加电影收藏
@home.route("/moviecol/add/", methods=["GET"])
@login_required
def moviecol_add():
	import json
	# javascript 通过点击获取两个参数
	uid = request.args.get("uid","")
	mid = request.args.get("mid", "")
	moviecol = Moviecol.query.filter_by(
		user_id = int(uid),
		movie_id = int(mid)
		).count()
	# 判断是否已经有记录
	if moviecol == 1:
		data = dict(ok=0)

	if moviecol == 0:
		moviecol = Moviecol(
			user_id = int(uid),
			movie_id = int(mid)
			)
		db.session.add(moviecol)
		db.session.commit()
		data = dict(ok=1)	
	return json.dumps(data)

# 电影收藏列表
@home.route("/moviecol/<int:page>", methods=["GET"])
@login_required
def moviecol(page):
	page_data = Moviecol.query.filter(
		Moviecol.user_id == int(session["user_id"])
		).join(
		Movie).filter(
		Movie.id == Moviecol.movie_id
		).order_by(
		Moviecol.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("home/moviecol.html", page_data=page_data)

# 首页
@home.route("/<int:page>/", methods=["GET"])
def index(page):
	tags = Tag.query.all()
	page_data = Movie.query
	# 标签
	tid = request.args.get("tid",0)
	if int(tid) !=0:
		page_data = page_data.filter_by(tag_id=int(tid))
	# 星级
	star = request.args.get("star",0)
	if int(star) !=0:
		page_data = page_data.filter_by(star=int(star))
	# 时间
	time = request.args.get("time",0)
	if int(time) == 2:
		page_data = page_data.order_by(
			Movie.addtime())
	elif int(time) == 1:
		page_data = page_data.order_by(
			Movie.addtime.desc())
	# 评论量
	cm = request.args.get("cm",0)
	if int(cm) == 2:
		page_data = page_data.order_by(
			Movie.commentnum.asc())
	elif int(cm) == 1:
		page_data = page_data.order_by(
			Movie.commentnum.desc())
	# 播放量
	pm = request.args.get("pm",0)
	if int(pm) == 2:
		page_data = page_data.order_by(
			Movie.playnum.asc())
	elif int(pm) == 1:
		page_data = page_data.order_by(
			Movie.playnum.desc())

	# page = request.args.get("page", 1)
	page_data = page_data.paginate(page=page, per_page=20)

	p = dict(
		tid = tid,
		star = star,
		time = time,
		pm = pm,
		cm = cm )
	return render_template("home/index.html", tags=tags, p=p, page_data=page_data)

#轮播图
@home.route("/animation/")
def animation():
	data = Preview.query.all()
	return render_template("home/animation.html", data=data)

# 搜索
@home.route("/search/<int:page>/")
def search(page):
	key = request.args.get("key", "")
	movie_count = Movie.query.filter(
		Movie.title.ilike('%'+key+'%')
		).count()
	page_data = Movie.query.filter(
		Movie.title.ilike('%'+key+'%')
		).order_by(
		Movie.addtime.desc()
		).paginate(page=page, per_page=20)
	page_data.key = key
	return render_template("home/search.html", movie_count=movie_count, page_data=page_data)

# 播放
@home.route("/play/<int:id>/<int:page>/", methods=["GET","POST"])
def play(id,page):
	form = CommentForm()
	
	movie = Movie.query.filter(
		Movie.id == int(id)
		).join(Tag
		).filter(
		Tag.id == Movie.tag_id
		).first_or_404()

	movie.playnum += 1

	page_data = Comment.query.join(
		Movie).join(
		User).filter(
		Movie.id == movie.id
		).order_by(
		Comment.addtime.desc()
		).paginate(page=page, per_page=20)
	
	if "user" in session and form.validate_on_submit():
		data = form.data
		comment = Comment(
			content = data["content"],
			movie_id = movie.id,
			user_id = session["user_id"]
			)
		db.session.add(comment)				
		movie.commentnum += 1
		db.session.commit()
		flash("添加评论成功", "ok")
		return redirect(url_for('home.play', id=movie.id,page=1))
	db.session.commit()
	return render_template("home/play.html", movie=movie,form=form,page_data=page_data)
