# coding:utf8
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog, User, Auth, Role, Admin
from functools import wraps
from app import db, app
from app.validators import Unique
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid

#上下文应用处理器
@admin.context_processor
def tpl_extra():
	data = dict( online_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		)
	return data

# oplog日志记录
def oplog_handle(reason):
	oplog = Oplog(
		admin_id = session["admin_id"],
		ip = request.remote_addr,
		reason = reason
	)
	db.session.add(oplog)
	db.session.commit()

# 登录装饰器
def adminlogin_required(f):
	@wraps(f)
	def decorated_function(*args,**kw):
		if "admin" not in session:
			return  redirect(url_for("admin.login", next=request.url))
		return f(*args,**kw)
	return decorated_function

#权限控制装饰器
def admin_auth(f):
	@wraps(f)
	def decorated_function(*args,**kw):
		admin = Admin.query.join(
			Role).filter(
			Role.id == Admin.role_id,
			Admin.id == session["admin_id"]
			).first()
		auths = admin.role.auths
		auths = list(map(lambda v: int(v), auths.split(",")))
		auth_list = Auth.query.all()
		urls = [v.url for v in auth_list for val in auths if val == v.id]
		rule = str(request.url_rule)
		if rule not in urls and admin.is_super != 0:
			abort(404)
		return f(*args, **kw)
	return decorated_function

# 修改文件名称
def change_filename(filename):
	fileinfo = os.path.splitext(filename)
	filename = datetime.now().strftime("%Y%m%d%H%M%S")+str(uuid.uuid4().hex)+fileinfo[-1]
	return filename

@admin.route("/")
@adminlogin_required
def index():
	return render_template("admin/index.html")

# 登录
@admin.route("/login/",methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		data = form.data
		admin = Admin.query.filter_by(name=data["account"]).first()
		if not admin.check_pwd(data["pwd"]):
			flash("用户名或密码错误！", "err")
			return redirect(url_for("admin.login"))
		session["admin"] = data["account"]
		session["admin_id"] = admin.id
		# 管理员登录日志
		adminlog = Adminlog(
			admin_id = admin.id,
			ip = request.remote_addr)
		db.session.add(adminlog)
		db.session.commit()
		return redirect(request.args.get("next") or url_for("admin.index"))

	return render_template("admin/login.html", form=form)

@admin.route("/logout/")
@adminlogin_required
def logout():
	session.pop("admin",None)
	session.pop("admin_id",None)
	return redirect(url_for("admin.login"))

# 修改密码
@admin.route("/pwd/", methods=["GET","POST"])
@adminlogin_required
def pwd():
	form = PwdForm()
	if form.validate_on_submit():
		data = form.data
		admin = Admin.query.filter_by(name=session["admin"]).first()
		from werkzeug.security import generate_password_hash
		admin.pwd = generate_password_hash(data["new_pwd"])
		db.session.add(admin)
		db.session.commit()
		flash("修改密码成功，请重新登录！", "ok")
		recod = "修改管理员%s-密码" %(admin.name)
		oplog_handle(recod)
		return redirect(url_for('admin.login'))
	return render_template("admin/pwd.html", form=form)

# 添加标签
@admin.route("/tag/add/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def tag_add():
	form = TagForm()
	if form.validate_on_submit():
		data = form.data
		tag_count = Tag.query.filter_by(name=data["name"]).count()
		if tag_count == 1:
			flash("此标签已经存在！","err")
			return redirect(url_for('admin.tag_add'))

		tag = Tag(name=data["name"])
		db.session.add(tag)
		db.session.commit()
		flash("添加标签成功！","ok")
		recod = "添加标签-%s" % (data["name"])
		oplog_handle(recod)
		redirect(url_for('admin.tag_add'))
	return render_template("admin/tag_add.html",form=form)

# 标签列表
@admin.route("/tag/list/<int:page>/",methods=["GET"])
@adminlogin_required
@admin_auth
def tag_list(page):
	page_data = Tag.query.order_by(
		Tag.addtime
		).paginate(page=page,per_page=20)
	return render_template("admin/tag_list.html", page_data=page_data)

# 标签删除
@admin.route("/tag/del/<int:id>/",methods=["GET"])
@adminlogin_required
@admin_auth
def tag_del(id=None):
	tag = Tag.query.filter_by(id=id).first_or_404()
	db.session.delete(tag)
	db.session.commit()
	flash("删除标签成功！", "ok")
	recod = "删除标签-%s" % (tag.name)
	oplog_handle(recod)
	return redirect(url_for('admin.tag_list',page=1))

# 标签编辑
@admin.route("/tag/edit/<int:id>/",methods=["GET","POST"])
@adminlogin_required
@admin_auth
def tag_edit(id=None):
	form = TagForm()
	tag = Tag.query.get_or_404(int(id))
	if form.validate_on_submit():
		data = form.data
		tag_count = Tag.query.filter_by(name=data["name"]).count()

		if tag.name != data["name"] and tag_count == 1:
			flash("此标签已经存在！","err")
			return redirect(url_for('admin.tag_edit',id=id))

		tag.name = data["name"]
		db.session.add(tag)
		db.session.commit()
		flash("修改标签成功！","ok")
		recod = "修改-%d的标签为-%s" % (id,data["name"])
		oplog_handle(recod)
		redirect(url_for('admin.tag_edit', id=id))

	return render_template("admin/tag_edit.html",form=form, tag=tag)

# 添加电影
@admin.route("/movie/add/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def movie_add():
	tags = Tag.query.all()
	form = MovieForm()
	if form.validate_on_submit():
		data = form.data
		# 判断提交title参数是否唯一
		title_count = Movie.query.filter_by(title=data["title"]).count()
		if title_count == 1:
			flash("电影标题已经存在！","err")
			return redirect(url_for('admin.movie_add'))

		# 保存视频文件
		url = change_filename(secure_filename(form.url.data.filename))
		form.url.data.save(app.config["UP_DIR"]+url)
		# 保存封面
		logo = change_filename(secure_filename(form.logo.data.filename))
		form.logo.data.save(app.config["UP_DIR"]+logo)

		movie = Movie(
			title = data["title"],
			url = url,
			info = data["info"],
			logo = logo,
			star = int(data["star"]),
			playnum = 0,
			commentnum = 0,
			tag_id = int(request.values.get("tag_id")),
			area = data["area"],
			release_time = data["release_time"],
			length = data["length"]
			)
		db.session.add(movie)
		db.session.commit()
		flash("添加电影成功！", "ok")
		recod = "添加电影-%s" % (data["title"])
		oplog_handle(recod)
		return redirect(url_for('admin.movie_add'))
	return render_template("admin/movie_add.html", form=form,tags=tags)

# 电影列表
@admin.route("/movie/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def movie_list(page):
	page_data = Movie.query.join(Tag).filter(
		Tag.id == Movie.tag_id
		).order_by(
		Movie.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/movie_list.html", page_data=page_data)

# 编辑电影
@admin.route("/movie/edit/<int:id>/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def movie_edit(id=None):
	tags = Tag.query.all()
	form = MovieForm()
	form.url.validators = []
	form.logo.validators = []
	movie = Movie.query.get_or_404(int(id))
	if request.method == "GET":
		form.info.data = movie.info
		form.star.data = movie.star
	if form.validate_on_submit():
		data = form.data
		movie_count = Movie.query.filter_by(title=data["title"]).count()
		if movie_count == 1 and movie.title != data["title"]:
			flash("片名已经存在！", "err")
			return redirect(url_for('admin.movie_edit', id=id))

		if not os.path.exists(app.config["UP_DIR"]):
			os.makedirs(app.config["UP_DIR"])
			os.chmod(app.config["UP_DIR"],"rw")

		# 视频文件保存
		if hasattr(form.url.data, 'filename'):
			movie.url = change_filename(secure_filename(form.url.data.filename))
			form.url.data.save(app.config["UP_DIR"]+movie.url)

		# 封面保持
		if hasattr(form.logo.data, 'filename'):
			movie.logo = change_filename(secure_filename(form.logo.data.filename))
			form.logo.data.save(app.config["UP_DIR"]+movie.logo)

		movie.star = int(data["star"])
		movie.info = data["info"]
		movie.tag_id = int(request.values.get("tag_id"))
		movie.title = data["title"]
		movie.area = data["area"]
		movie.length = data["length"]
		movie.release_time = data["release_time"]
		db.session.add(movie)
		db.session.commit()
		flash("修改电影成功！", "ok")

		recod = "修改电影ID-%d" % (id)
		oplog_handle(recod)
		return redirect(url_for('admin.movie_list', page=1))
	return render_template("admin/movie_edit.html", form=form,movie=movie,tags=tags)

# 删除电影
@admin.route('/movie/del/<int:id>/', methods=["GET"])
@adminlogin_required
@admin_auth
def movie_del(id=None):
	movie = Movie.query.get_or_404(int(id))
	db.session.delete(movie)
	db.session.commit()
	flash("删除电影成功！", "ok")
	recod = "删除电影-%s" % (movie.title)
	oplog_handle(recod)
	return redirect(url_for('admin.movie_list',page=1))

# 添加预告
@admin.route("/preview/add/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def preview_add():
	form = PreviewForm()
	if form.validate_on_submit():
		data = form.data
		preview_count = Preview.query.filter_by(title=data["title"]).count()
		if preview_count == 1:
			flash("此预告标题已经存在！", "err")
			return redirect(url_for('admin.preview_add'))

		if not os.path.exists(app.config["UP_DIR"]):
			os.makedirs(app.config["UP_DIR"])
			os.chmod(app.config["UP_DIR"],"rw")

		logo = change_filename(secure_filename(form.logo.data.filename))
		form.logo.data.save(app.config["UP_DIR"]+logo)
		preview = Preview(
			title = data["title"],
			logo = logo
		)
		db.session.add(preview)
		db.session.commit()
		flash("预告添加成功！", "ok")
		
		recod = "添加预告-%s" % (data["title"])
		oplog_handle(recod)
		return redirect(url_for('admin.preview_add'))
	return render_template("admin/preview_add.html",form=form)

# 预告列表
@admin.route("/preview/list/<int:page>/")
@adminlogin_required
@admin_auth
def preview_list(page):
	page_data = Preview.query.order_by(
		Preview.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/preview_list.html", page_data=page_data)

# 删除预告
@admin.route('/preview/del/<int:id>/', methods=["GET"])
@adminlogin_required
@admin_auth
def preview_del(id=None):
	preview = Preview.query.get_or_404(id)
	db.session.delete(preview)
	db.session.commit()
	flash("删除电影成功！", "ok")
	recod = "删除预告-%s" % (preview.title)
	oplog_handle(recod)
	return redirect(url_for('admin.preview_list',page=1))

# 编辑预告
@admin.route("/preview/edit/<int:id>/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def preview_edit(id=None):
	form = PreviewForm()
	form.logo.validators = []
	preview = Preview.query.get_or_404(int(id))

	if form.validate_on_submit():
		data = form.data
		preview_count = Movie.query.filter_by(title=data["title"]).count()
		if preview_count == 1 and preview.title != data["title"]:
			flash("预告标题已经存在！", "err")
			return redirect(url_for('admin.preview_edit', id=id))

		# 封面保持
		if hasattr(form.logo.data, 'filename'):
			preview.logo = change_filename(secure_filename(form.logo.data.filename))
			form.logo.data.save(app.config["UP_DIR"]+preview.logo)

		preview.title = data["title"]
		db.session.add(preview)
		db.session.commit()
		flash("修改预告成功！", "ok")
		recod = "修改预告ID-%s" % (id)
		oplog_handle(recod)
		return redirect(url_for('admin.preview_list', page=1))

	return render_template("admin/preview_edit.html", form=form, preview=preview)

# 用户列表
@admin.route("/user/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def user_list(page):
	page_data = User.query.order_by(
		User.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/user_list.html", page_data=page_data)

# 用户查看
@admin.route("/user/view/<int:id>/", methods=["GET"])
@adminlogin_required
def user_view(id=None):
	user = User.query.get_or_404(int(id))
	return render_template("admin/user_view.html",user=user)

# 用户删除
@admin.route("/user/del/<int:id>/", methods=["GET"])
@adminlogin_required
@admin_auth
def user_del(id=None):
	user = User.query.get_or_404(int(id))
	db.session.delete(user)
	db.session.commit()
	flash("删除用户成功！", "ok")
	recod = "删除用户-%s" % (user.name)
	oplog_handle(recod)
	return redirect(url_for('admin.user_list',page=1))

# 评论列表
@admin.route("/comment/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def comment_list(page):
	page_data = Comment.query.join(
		Movie).join(User).filter(
		Movie.id == Comment.movie_id,
		User.id == Comment.user_id
		).order_by(
		Comment.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/comment_list.html",page_data=page_data)

# 删除评论
@admin.route("/comment/del/<int:id>/", methods=["GET"])
@adminlogin_required
@admin_auth
def comment_del(id=None):
	comment = Comment.query.get_or_404(int(id))
	db.session.delete(comment)
	db.session.commit()
	flash("删除评论成功！", "ok")
	recod = "删除评论ID-%d" % (id)
	oplog_handle(recod)
	return redirect(url_for('admin.comment_list',page=1))

# 电影收藏列表
@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def moviecol_list(page=None):
	page_data = Moviecol.query.join(
		Movie).join(User).filter(
		Movie.id == Moviecol.movie_id,
		User.id == Moviecol.user_id
		).order_by(
		Moviecol.id.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/moviecol_list.html", page_data=page_data)

# 删除电影收藏
@admin.route("/moviecol/del/<int:id>/", methods=["GET"])
@adminlogin_required
@admin_auth
def moviecol_del(id=None):
	moviecol = Moviecol.query.get_or_404(int(id))
	db.session.delete(moviecol)
	db.session.commit()
	flash("删除电影收藏成功！", "ok")
	recod = "删除电影收藏-%d" % (id)
	oplog_handle(recod)
	return redirect(url_for('admin.moviecol_list', page=1))

# 操作日志列表
@admin.route("/oplog/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def oplog_list(page):
	page_data = Oplog.query.join(
		Admin).filter(
		Admin.id == Oplog.admin_id
		).order_by(
		Oplog.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/oplog_list.html",page_data=page_data)

# 管理员登录日志列表
@admin.route("/adminloginlog/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def adminloginlog_list(page):
	page_data = Adminlog.query.join(
		Admin).filter(
		Admin.id == Adminlog.admin_id
		).order_by(
		Adminlog.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/adminloginlog_list.html",page_data=page_data)

# 会员登录日志列表
@admin.route("/userloginlog/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def userloginlog_list(page):
	page_data = Userlog.query.join(
		User).filter(
		User.id == Userlog.user_id
		).order_by(
		Userlog.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("admin/userloginlog_list.html", page_data=page_data)

#权限添加
@admin.route("/auth/add/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def auth_add():
	form = AuthForm()
	if form.validate_on_submit():
		
		name_count = Auth.query.filter_by(name=form.data["name"]).count()
		url_count = Auth.query.filter_by(url=form.data["url"]).count()

		if name_count == 1 and auth.name != data["name"]:
			flash("权限名称已经存在！", "err")
			return redirect(url_for('admin.auth_edit', id=id))

		if url_count == 1 and auth.url != data["url"]:
			flash("权限地址已经存在！", "err")
			return redirect(url_for('admin.auth_edit', id=id))

		auth = Auth(
			name = form.data["name"],
			url = form.data["url"]
			)
		db.session.add(auth)
		db.session.commit()
		flash("添加权限成功！", "ok")

		recod = "添加权限-%s" % (form.data["name"])
		oplog_handle(recod)
	return render_template("admin/auth_add.html",form=form)

# 权限列表
@admin.route("/auth/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def auth_list(page):
	page_data = Auth.query.order_by(
		Auth.addtime.desc()
		).paginate(page=page,per_page=20)
	return render_template("admin/auth_list.html", page_data=page_data)

#权限删除
@admin.route("/auth/del/<int:id>/", methods=["GET"])
@adminlogin_required
def auth_del(id):
	auth = Auth.query.get_or_404(int(id))
	db.session.delete(auth)
	db.session.commit()
	flash("删除权限成功", "ok")
	recod = "删除权限-%s" % (auth.name)
	oplog_handle(recod)	
	return redirect(url_for('admin.auth_list',page=1))

#权限修改
@admin.route("/auth/edit/<int:id>/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def auth_edit(id=None):
	form = AuthForm()
	auth = Auth.query.get_or_404(int(id))
	if form.validate_on_submit():
		data = form.data
		name_count = Auth.query.filter_by(name=data["name"]).count()
		url_count = Auth.query.filter_by(url=data["url"]).count()
		if name_count == 1 and auth.name != data["name"]:
			flash("权限名称已经存在！", "err")
			return redirect(url_for('admin.auth_edit', id=id))

		if url_count == 1 and auth.url != data["url"]:
			flash("权限地址已经存在！", "err")
			return redirect(url_for('admin.auth_edit', id=id))

		auth.name = data["name"]
		auth.url = data["url"]
		db.session.commit()
		flash("修改权限成功！", "ok")
		recod = "修改权限ID-%d" % (int(id))
		oplog_handle(recod)
	return render_template("admin/auth_edit.html",form=form, auth=auth)

# 角色添加
@admin.route("/role/add/", methods=["GET","POST"])
@adminlogin_required
def role_add():
	form = RoleForm()
	if form.validate_on_submit():
		data = form.data
		if Role.query.filter_by(name=form.data["name"]).count():
			flash("角色名称已经存在！", "err")
			return redirect(url_for("admin.role_add"))

		# 插入role新记录
		role = Role(
			name = data["name"],
			auths = ",".join(map(lambda v: str(v), data["auths"]))
			)
		db.session.add(role)
		db.session.commit()
		flash("添加角色成功！", "ok")
		recod = "添加角色-%s" % (data["name"])
		oplog_handle(recod)
	return render_template("admin/role_add.html", form=form)

# 角色列表
@admin.route("/role/list/<int:page>", methods=["GET"])
@adminlogin_required
@admin_auth
def role_list(page):
	page_data = Role.query.order_by(
		Role.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("admin/role_list.html", page_data=page_data)

# 编辑角色
@admin.route("/role/edit/<int:id>/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def role_edit(id=None):
	form = RoleForm()
	role = Role.query.get_or_404(int(id))
	if request.method == "GET":
		form.auths.data = list(map(lambda v:int(v) ,role.auths.split(",")))
	if form.validate_on_submit():
		data = form.data
		name_count = Role.query.filter_by(name=data["name"]).count()
		if name_count == 1 and role.name != data["name"]:
			flash("角色名称已经存在！", "err")
			return redirect(url_for('admin.role_edit', id=id))

		# update role 表
		role.name = data["name"]
		role.auths = ",".join(map(lambda v: str(v), data["auths"]))
		db.session.commit()

		flash("修改权限成功！", "ok")
		recod = "修改权限ID-%d" % (id)
		oplog_handle(recod)
	return render_template("admin/role_edit.html",form=form, role=role)

# 删除角色
@admin.route("/role/del/<int:id>/", methods=["GET"])
@adminlogin_required
@admin_auth
def role_del(id=None):
	role = Role.query.get_or_404(int(id))
	db.session.delete(role)
	db.session.commit()
	flash("删除角色成功", "ok")
	recod = "删除角色ID-%d" % (id)
	oplog_handle(recod)
	return redirect(url_for('admin.role_list',page=1))

@admin.route("/admin/add/", methods=["GET","POST"])
@adminlogin_required
@admin_auth
def admin_add():
	form = AdminForm()
	from werkzeug.security import generate_password_hash
	if form.validate_on_submit():
		data = form.data
		if Admin.query.filter_by(name=data["name"]).count():
			flash("该管理员已经存在！", "err")
			return redirect(url_for('admin.admin_add'))

		admin = Admin(
			name = data["name"],
			pwd = generate_password_hash(data["pwd"]),
			role_id = data["role_id"],
			is_super = 1	
			)
		db.session.add(admin)
		db.session.commit()
		flash("添加管理员成功", "ok")
	return render_template("admin/admin_add.html", form=form)

@admin.route("/admin/list/<int:page>/", methods=["GET"])
@adminlogin_required
@admin_auth
def admin_list(page):
	page_data = Admin.query.join(
		Role).filter(
		Role.id == Admin.role_id
		).order_by(
		Admin.addtime.desc()
		).paginate(page=page, per_page=20)
	return render_template("admin/admin_list.html", page_data=page_data)