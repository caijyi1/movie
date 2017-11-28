# -*- coding:utf8 -*-
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired,ValidationError, EqualTo, Email, Regexp, InputRequired, length 
from app.validators import Unique
from app.models import User



class RegistForm(FlaskForm):
	"""注册表单"""
	name = StringField(
		label = "昵称",
		validators = [DataRequired("请输入昵称！"),
			Unique(User,User.name, message="昵称已经存在！")],
		description = '昵称',
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入昵称！",
			"required": "required"
		}
		)
	email = StringField(
		label = "邮箱",
		validators = [DataRequired("请输入邮箱！"),
		Email("邮箱格式不正确！"),
		Unique(User,User.email, message="昵称已经存在！")],
		description = '邮箱',
		render_kw = {
			"class": "form-control input-lg",
			"placeholder": "请输入邮箱！",
			"required": "required"
		}
		)
	phone = StringField(
		label = "手机",
		validators = [ DataRequired("请输入手机号！"),
			Regexp("1[3458]\\d{9}", message="手机号码格式不正确！"),
			Unique(User,User.phone, message="昵称已经存在！")],
		description="手机",
		render_kw = {
			"class": "form-control input-lg",
			"placeholder": "请输入手机号！"
		}
		)
	pwd = PasswordField(
		label = "密码",
		validators = [DataRequired("请输入密码！")],
		description = '密码',
		render_kw = {
			"class": "form-control input-lg",
			"placeholder": "请输入密码！",
			"required": "required"
		}
		)
	repwd = PasswordField(
		label = "确认密码",
		validators = [DataRequired("请再次输入密码！"),
			EqualTo('pwd',message=u'密码不一致！')],
		description = '确认密码',
		render_kw = {
			"class": "form-control input-lg",
			"placeholder": "请再次输入密码！",
			"required": "required"
		}
		)
	submit = SubmitField(
		"注册",
		render_kw = {
			"class": "btn btn-lg btn-success btn-block"
		}
		)

class LoginForm(FlaskForm):
	"""登录表单"""
	name = StringField(
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
			"class": "form-control input-lg",
			"placeholder": "请输入密码！",
			"required": "required"
		}
		)

	recaptcha = RecaptchaField()

	submit = SubmitField(
		"登录",
		render_kw = {
			"class": "btn btn-lg btn-primary btn-block"
		}
		)

class UserdetailForm(FlaskForm):
	"""注册表单"""
	name = StringField(
		label = "昵称",
		description = "昵称",
		render_kw = {
			"class": "form-control",
			"disabled": "disabled"
		}
		)
	email = StringField(
		label = "邮箱",
		validators = [DataRequired("请输入邮箱！"),
		Email("邮箱格式不正确！")],
		description = '邮箱',
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入邮箱！",
			"required": "required"
		}
		)
	face = FileField(
		label = "头像",
		validators = [ DataRequired("请上传头像！"), 
			FileAllowed(['jpg','jpeg','png','gif'],'只支持jpg,jpeg,png,gif图片格式')],
		description = "头像"
		)
	phone = StringField(
		label = "手机",
		validators = [ DataRequired("请输入手机号！"),
			Regexp("1[3458]\\d{9}", message="手机号码格式不正确！")],
		description="手机",
		render_kw = {
			"class": "form-control",
			"placeholder": "请输入手机号！",
		}
		)
	info = TextAreaField(
		label = "简介",
		validators = [InputRequired("请输入简介")],
		description = "简介",
		render_kw = {
			"class": "form-control",
			"rows": 10
		})
	submit = SubmitField(
		"提交",
		render_kw = {
			"class": "btn btn-lg btn-primary btn-block"
		}
		)

class PwdForm(FlaskForm):
	old_pwd = PasswordField(
		label = "旧密码",
		validators = [ DataRequired("请输入旧密码！")],
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
			"class": "btn btn-success"
		}
		)

	def validate_old_pwd(self,field):
		from flask import session
		pwd = field.data
		name = session["user"]
		user = User.query.filter_by(name = name).first()
		if not user.check_pwd(pwd):
			raise ValidationError("旧密码错误！")

class CommentForm(FlaskForm):
	content = TextAreaField(
		label = "内容",
		validators = [DataRequired("请输入内容！"),length(min=10,max=1000)],
		description = "内容",
		render_kw = {
			"id": "input_content"
		}
		)

	submit = SubmitField(
		'提交评论',
		render_kw = {
			"class": "btn btn-success",
			"id": "btn-sub"
		}
		)