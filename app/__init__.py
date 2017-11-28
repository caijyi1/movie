# coding:utf8
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql, os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:docker_mysql@db:3306/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "f0d8de6a873e430a8c8ce195b6281507"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/video/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/video/users/")
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"
app.debug = True
app.testing = True
if not os.path.exists(app.config["FC_DIR"]):
	os.makedirs(app.config["FC_DIR"])
	os.chmod(app.config["FC_DIR"],"rw")


db = SQLAlchemy(app)

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")

@app.errorhandler(404)
def page_not_found(error):
	return render_template("common/404.html"), 404
