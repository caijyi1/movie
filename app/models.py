# -*- coding:utf8 -*-
from datetime import datetime
from app import db

# 会员
class User(db.Model):
	""" CREATE TABLE `user` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) DEFAULT NULL,
	`pwd` varchar(100) DEFAULT NULL,
	`email` varchar(100) DEFAULT NULL,
	`phone` varchar(11) DEFAULT NULL,
	`info` text,
	`face` varchar(255) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	`uuid` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `name` (`name`),
	UNIQUE KEY `email` (`email`),
	UNIQUE KEY `phone` (`phone`),
	UNIQUE KEY `face` (`face`),
	UNIQUE KEY `uuid` (`uuid`),
	KEY `ix_user_addtime` (`addtime`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8 """

	__tablename__ = "user" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	name = db.Column(db.String(100), unique=True) #昵称
	pwd = db.Column(db.String(100)) #密码
	email = db.Column(db.String(100), unique=True) #邮箱
	phone = db.Column(db.String(11), unique=True) #手机号码
	info = db.Column(db.Text, default='这个人太懒了，什么都没写!') #个性简介
	face = db.Column(db.String(255)) #头像
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #注册时间
	uuid = db.Column(db.String(255), unique=True) #唯一标识符

	def __repr__(self):
		return "<User %r" % self.name

	def check_pwd(self, pwd):
		from werkzeug.security import check_password_hash
		return check_password_hash(self.pwd, pwd)


# 会员登录日志
class Userlog(db.Model):
	"""CREATE TABLE `userlog` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`user_id` int(11) DEFAULT NULL,
	`ip` varchar(100) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `user_id` (`user_id`),
	KEY `ix_userlog_addtime` (`addtime`),
	CONSTRAINT `userlog_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8 """

	__tablename__ = "userlog" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #所属会员
	user = db.relationship(User, backref="userlogs") #外键关联User
	ip = db.Column(db.String(100)) #登录ip
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #登录时间

	def __repr__(self):
		return "<Userlog %r>" % self.id

# 标签
class Tag(db.Model):
	"""CREATE TABLE `tag` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `name` (`name`),
	KEY `ix_tag_addtime` (`addtime`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "tag" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	name = db.Column(db.String(100), unique=True) #标题
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Tag %r>" % self.name

# 电影
class Movie(db.Model):
	"""CREATE TABLE `movie` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`title` varchar(255) DEFAULT NULL,
	`url` varchar(255) DEFAULT NULL,
	`info` text,
	`logo` varchar(255) DEFAULT NULL,
	`star` smallint(6) DEFAULT NULL,
	`playnum` bigint(20) DEFAULT NULL,
	`commentnum` bigint(20) DEFAULT NULL,
	`tag_id` int(11) DEFAULT NULL,
	`area` varchar(255) DEFAULT NULL,
	`release_time` date DEFAULT NULL,
	`length` varchar(100) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `title` (`title`),
	UNIQUE KEY `url` (`url`),
	UNIQUE KEY `logo` (`logo`),
	KEY `tag_id` (`tag_id`),
	KEY `ix_movie_addtime` (`addtime`),
	CONSTRAINT `movie_ibfk_1` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "movie"
	id = db.Column(db.Integer, primary_key=True) #编号
	title = db.Column(db.String(255), unique=True) #标题
	url = db.Column(db.String(255), unique=True) #地址
	info = db.Column(db.Text) #简介
	logo = db.Column(db.String(255), unique=True) #封面
	star = db.Column(db.SmallInteger) #星级
	playnum = db.Column(db.BigInteger) #播放量
	commentnum = db.Column(db.BigInteger) #评论量
	tag_id = db.Column(db.Integer, db.ForeignKey('tag.id')) #所属标签
	tag = db.relationship(Tag, backref='Movies') #外键关联tag
	area = db.Column(db.String(255)) #上映地区
	release_time = db.Column(db.Date) # 上映时间
	length = db.Column(db.String(100)) #播放长度
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间	
	

	def __repr__(self):
		return "<Movie %r>" % self.title

# 上映预告
class Preview(db.Model):
	"""docstring for Preview"""
	__tablename__ = "preview"
	id = db.Column(db.Integer, primary_key=True) #编号
	title = db.Column(db.String(255), unique=True) #标题
	logo = db.Column(db.String(255), unique=True) #封面
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Preview %r>" % self.title

# 评论
class Comment(db.Model):
	"""CREATE TABLE `comment` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`content` text,
	`movie_id` int(11) DEFAULT NULL,
	`user_id` int(11) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `movie_id` (`movie_id`),
	KEY `user_id` (`user_id`),
	KEY `ix_moviecol_addtime` (`addtime`),
	CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movie` (`id`),
	CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8"""
	__tablename__ = "comment"
	id = db.Column(db.Integer, primary_key=True) #编号
	content = db.Column(db.Text) #内容
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id')) #所属电影
	movie = db.relationship(Movie, backref='comments') # 评论外键关系关联Movie
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #所属用户
	user = db.relationship(User, backref='comments') #评论外键关系关联 User
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Comment %r>" % self.id

# 电影收藏
class Moviecol(db.Model):
	"""docstring for Moviecol"""
	__tablename__ = "moviecol"
	id = db.Column(db.Integer, primary_key=True) #编号
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id')) #所属电影
	movie = db.relationship(Movie, backref='moviecols') # 电影收藏外键关系关联
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #所属用户
	user = db.relationship(User, backref='moviecols') #电影收藏外键关系关联
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Moviecol %r>" % self.id

########
# 权限
class Auth(db.Model):
	"""CREATE TABLE `auth` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) DEFAULT NULL,
	`url` varchar(100) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `name` (`name`),
	UNIQUE KEY `url` (`url`),
	KEY `ix_auth_addtime` (`addtime`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "auth"
	id = db.Column(db.Integer, primary_key=True) # 编号
	name = db.Column(db.String(100), unique=True) # 名称
	url = db.Column(db.String(100), unique=True) # 地址
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Auth %r>" % self.name

# 角色
class Role(db.Model):
	"""CREATE TABLE `role` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) DEFAULT NULL,
	`auths` varchar(600) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `name` (`name`),
	KEY `ix_role_addtime` (`addtime`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "role"
	id = db.Column(db.Integer, primary_key=True) # 编号
	name = db.Column(db.String(100), unique=True) # 名称
	auths = db.Column(db.String(600)) #角色权限列表
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Role %r>" % self.name

# 管理员
class Admin(db.Model):
	"""CREATE TABLE `admin` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`name` varchar(100) DEFAULT NULL,
	`pwd` varchar(100) DEFAULT NULL,
	`is_super` smallint(6) DEFAULT NULL,
	`role_id` int(11) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE KEY `name` (`name`),
	KEY `role_id` (`role_id`),
	KEY `ix_admin_addtime` (`addtime`),
	CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "admin" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	name = db.Column(db.String(100), unique=True) #管理员
	pwd = db.Column(db.String(100)) #管理员密码
	is_super = db.Column(db.SmallInteger) # 是否为超级管理员， 0为超级管理员
	role_id = db.Column(db.Integer, db.ForeignKey('role.id')) #所属角色
	role = db.relationship(Role, backref='admins') # 管理员外键关系关联	
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #添加时间

	def __repr__(self):
		return "<Admin %r>" % self.name

	def check_pwd(self,pwd):
		from werkzeug.security import check_password_hash
		return check_password_hash(self.pwd, pwd)

# 管理员登录日志
class Adminlog(db.Model):
	"""CREATE TABLE `adminlog` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`admin_id` int(11) DEFAULT NULL,
	`ip` varchar(100) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `admin_id` (`admin_id`),
	KEY `ix_adminlog_addtime` (`addtime`),
	CONSTRAINT `adminlog_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "adminlog" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) #所属管理员
	admin = db.relationship(Admin, backref='adminlogs') #管理员登录日志外键关联
	ip = db.Column(db.String(100)) #登录ip
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #登录时间

	def __repr__(self):
		return "<Adminlog %r>" % self.id

# 操作日志
class Oplog(db.Model):
	"""CREATE TABLE `oplog` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`admin_id` int(11) DEFAULT NULL,
	`ip` varchar(100) DEFAULT NULL,
	`reason` varchar(600) DEFAULT NULL,
	`addtime` datetime DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `admin_id` (`admin_id`),
	KEY `ix_oplog_addtime` (`addtime`),
	CONSTRAINT `oplog_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"""

	__tablename__ = "oplog" #表名
	id = db.Column(db.Integer, primary_key=True) #编号
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) #所属管理员
	admin = db.relationship(Admin, backref='oplogs') #管理员操作日志外键关联
	ip = db.Column(db.String(100)) #登录ip
	reason = db.Column(db.String(600))
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) #登录时间

	def __repr__(self):
		return "<Oplog %r>" % self.id

"""
if __name__ == '__main__':
	db.create_all()
	role = Role(
		name = "超级管理员",
		auths = ""
		)
	db.session.add(role)
	db.session.commit()

	from werkzeug.security import generate_password_hash

	admin = Admin(
		name = "jony",
		pwd = generate_password_hash("jony"),
		is_super = 0,
		role_id = 1
		)
	db.session.add(admin)
	db.session.commit()
"""