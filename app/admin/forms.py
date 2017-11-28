#-*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, length, EqualTo
from app.models import Admin, Auth, Role

class LoginForm(FlaskForm):
	"""管理员登录表单"""
	account = StringField(
		label = "账号",
		validators = [DataRequired("请输入账号！")],
		description = '账号',
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入账号！",
			"required": "required"
		}
		)
	pwd = PasswordField(
		label = "密码",
		validators = [DataRequired("请输入密码！")],
		description = '密码',
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入密码！",
			"required": "required"
		}
		)
	submit = SubmitField(
		"登录",
		render_kw = {
			"class": "btn btn-primary btn-block btn-flat"
		}
		)

	def validate_account(self,field):
		account = field.data
		admin = Admin.query.filter_by(name=account).count()
		if admin == 0:
			raise ValidationError("用户名或密码错误！")
		
class TagForm(FlaskForm):
	"""标签表单"""
	name = StringField(
		label = "名称",
		validators = [DataRequired("请输入标签！"),length(min=2,max=6)],
		description = "标签",
		render_kw = {
			"class": "form-control", 
			"id": "input_name",
			"placeholder": "请输入标签！",
			"required": "required"
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)
	
class MovieForm(FlaskForm):
	"""电影表单"""
	title = StringField(
		label = "片名",
		validators = [DataRequired("请输入片名！"),length(min=4,max=10)],
		description = "片名",
		render_kw = {
			"class": "form-control", 
			"id": "input_title",
			"placeholder": "请输入片名！",
			"required": "required"
		}
		)
	url = FileField(
		label = "视频",
		validators = [ DataRequired("请上传视频！"), 
			FileAllowed(['mp4','avi','rmvb','mpg','mpeg','wmv'],'只支持mp4,avi,rmvb,mpg,mpeg,wmv视频格式！')],
		description = "视频"
		)
	info = TextAreaField(
		label = "简介",
		validators = [DataRequired("请输入简介！"),length(min=8,max=255)],
		render_kw = {
			"class": "form-control", 
			"rows": "10"
		}
		)
	logo = FileField(
		label = "封面",
		validators = [FileRequired("请上传封面！"),
			FileAllowed(['jpg','jpeg','png','gif'],'只支持jpg,jpeg,png,gif图片格式')],
		description = "封面"
		)
	star = SelectField(
		label = "星级",
		validators = [DataRequired("请选择星级！")],
		coerce = int,
		choices = [(1,"1星"), (2,"2星"), (3,"3星"), (4,"4星"), (5,"5星")],
		description = "星级",
		render_kw = {
			"class": "form-control"
		}
		)

	area = StringField(
		label = "地区",
		validators = [DataRequired("请输入地区！")],
		description = "地区",
		render_kw = {
			"class": "form-control", 
			"placeholder": "请输入地区！"
		}
		)
	length = StringField(
		label = "片长",
		validators = [DataRequired("请输入片长！")],
		description = "片长",
		render_kw = {
			"class": "form-control", 
			"placeholder": "请输入片长！"
		}
		)
	release_time = StringField(
		label = "上映时间",
		validators = [DataRequired("请选择上映时间！")],
		description = "上映时间",
		render_kw = {
			"class": "form-control", 
			"placeholder": "请输入上映时间！",
			"id": "input_release_time"
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)

class PreviewForm(FlaskForm):
	"""预告表单"""
	title = StringField(
		label = "预告标题",
		validators = [DataRequired("请输入预告标题！"),length(min=4,max=10)],
		description = "预告标题",
		render_kw = {
			"class": "form-control", 
			"id": "input_title",
			"placeholder": "请输入预告标题！",
			"required": "required"
		}
		)
	logo = FileField(
		label = "封面",
		validators = [ DataRequired("请上传封面！"), 
			FileAllowed(['jpg','jpeg','png','gif'],'只支持jpg,jpeg,png,gif图片格式')],
		description = "封面"
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)

class PwdForm(FlaskForm):
	old_pwd = PasswordField(
		label = "旧密码",
		validators = [ DataRequired("请输入旧密码！"),length(min=6,max=30)],
		description = "旧密码",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入旧密码！",
			"required": "required"
		}
		)
	new_pwd = PasswordField(
		label = "新密码",
		validators = [ DataRequired("请输入新密码！")],
		description = "新密码",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入新密码！",
			"required": "required"
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)

	def validate_old_pwd(self,field):
		from flask import session
		pwd = field.data
		name = session["admin"]
		admin = Admin.query.filter_by(name = name).first()
		if not admin.check_pwd(pwd):
			raise ValidationError("旧密码错误！")

class AuthForm(FlaskForm):
	name = StringField(
		label = "权限名称",
		validators = [ DataRequired("请输入权限名称！")],
		description = "权限名称",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入权限名称！",
			"required": "required"
		}
		)
	url = StringField(
		label = "权限地址",
		validators = [ DataRequired("请输入权限地址！")],
		description = "权限地址",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入权限地址！",
			"required": "required"
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)

class RoleForm(FlaskForm):
	auth_list = Auth.query.all()
	name = StringField(
		label = "角色名称",
		validators = [ DataRequired("请输入角色名称！")],
		description = "角色名称",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入角色名称！",
			"required": "required"
		}
		)
	auths = SelectMultipleField(
		label = "权限列表",
		validators = [ DataRequired("请输入权限列表！")],
		coerce = int,
		choices = [(v.id,v.name) for v in auth_list],
		description = "权限列表",
		render_kw = {
			"class": "form-control"
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)

class AdminForm(FlaskForm):
	role_list = Role.query.all()
	name = StringField(
		label = "管理员名称",
		validators = [ DataRequired("请输入管理员名称！")],
		description = "管理员名称",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入管理员名称！",
			"required": "required"
		}
		)
	pwd = PasswordField(
		label = "管理员密码",
		validators = [ DataRequired("请输入管理员密码！")],
		description = "管理员密码",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入管理员密码！",
			"required": "required"
		}
		)
	repwd = PasswordField(
		label = "管理员重复怒密码",
		validators = [ DataRequired("请重复输入管理员密码！"),
			EqualTo('pwd', message = u'密码输入不一致！')],
		description = "管理员重复密码",
		render_kw = {
			"class": "form-control",
			"placeholder": "请重复输入管理员密码！"
		}
		)
	role_id = SelectField(
		label = "所属角色",
		coerce = int,
		choices = [(v.id,v.name) for v in role_list],
		render_kw = {
			"class": "form-control",
		}
		)
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-primary"
		}
		)