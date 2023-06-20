from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,StopCode,ReasonOne,User,SKU,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
import time
import json
import datetime
#from ugeeapp.appclasses.production import PRODUCTION
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib



class GLOBALCLASS():

	def __init__(self):
		pass


	def modify_data(self):

		

		return

	def get_sku(self,productcode):

		code=SKU.query.filter_by(productcode=productcode).first()

		return code.description

	def get_userinfo(self,userid):

		user=User.query.filter_by(userid=userid).first()

		return "{} {}".format(user.sname,user.fname)