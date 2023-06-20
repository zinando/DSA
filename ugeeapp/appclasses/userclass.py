from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User
import time
import json
import datetime
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib


class USERACCOUNT:

	def __init__(self):
		pass

	def loginservice(self,form):

		##query the user using the username from form#
		user=User.query.filter_by(username=form.username.data).first()

		if user and check_password_hash(user.password, form.password.data):
			
			##check if user is blocked#
			if user.block_stat>0:
				return {'status':2,'message':'Your account is blocked. You cannot login at this time.'}
			
			##check if user password is temporary password#
			if self.is_temp_password(user.userid,form.password.data):
				return {"status":3,'id':user.userid, "message":'This is temporary password and needs to be changed'}

			##log user in#
			login_user(user,remember=form.remember.data)

			##create session data#
			session['userid']=user.userid
			session['fullname']="{} {}".format(user.fname,user.sname)
			session['fname']=user.fname
			session['sname']=user.sname
			session['email']=user.email
			session['phone']=user.phone
			session['adminlevel']=user.adminlevel
			session['ip_address']=request.remote_addr
			session['username']=user.username
			session['activated']=user.activated
			session['user_department']=user.department

			if user.last_login == None or  user.last_login == '':
				session['last_login']=datetime.now()
			else:
				session['last_login']=user.last_login

			db.session.query(User).filter(User.userid==user.userid).update({'last_login':datetime.now()})
			db.session.commit()

			return {'status':1,'message':'Login was successful.'}

		else:
			
			return {'status':2,'message':'Invalid username and or password'}	
		
		

	def addnewuser(self,form):
		
		##check that username and password does not already exist#
		check = User.query.filter_by(username=form.username.data).count()
		if check >0:
			return {'status':2,'message':'User name already exists for another user.'}

		check = User.query.filter_by(email=form.email.data).count()
		if check >0:
			return {'status':2,'message':'Email name already exists for another user.'}

		##check phone number#
		phone=form.phone.data
		if  phone[:3] =='234':
			phone2='0{}'.format(phone[3:13])
			check_mobile=db.session.query(User).filter((User.phone==phone) | (User.phone ==phone2)).count()

		elif len(phone) ==11:
			## remove the zero and add 234 and recheck ##
			phone2='234{}'.format(phone[1:11])
			check_mobile=db.session.query(User).filter((User.phone==phone) | (User.phone ==phone2)).count()

		elif len(phone) <11:

			return {'status':2,'message':'Invalid phone number.'}

		if check_mobile > 0 :

			return {'status':2,'message':'The provided mobile number is currently linked to another account and cannot be used.'}

		##validate password#
		if len(myfunc.check_password_strength(form.password.data))>0:

			resp=myfunc.check_password_strength(form.password.data)[0]
			return {'status':2,'message':resp}

		loguser=User()
		loguser.acctype=form.acctype.data
		loguser.fname=form.fname.data.title()
		loguser.sname=form.sname.data.title()
		loguser.email=form.email.data
		loguser.password=generate_password_hash(form.password.data)
		loguser.temp_password=generate_password_hash(form.password.data)
		loguser.phone=form.phone.data
		loguser.role=1
		if form.role.data:
			roll = json.dumps(form.role.data)
			loguser.user_roles = roll
		loguser.department=form.department.data
		loguser.adminlevel=form.adminlevel.data
		loguser.createdby=session['userid']
		loguser.block_stat=form.block_stat.data
		loguser.username=form.username.data
		loguser.passresetcode='hncbdjkbjcdkd'
		loguser.activated=1
		loguser.team = form.team.data
		db.session.add(loguser)
		db.session.commit()

		return {'status':1,'message':'User has been added successfully.'}

	def reset_password(self,form):

		key = 'wewe4354wdwewewwsaedasa3e76r32wsdfasdasdasda' # Defined as a simple string.
		key_bytes= bytes(key , 'latin-1')
		data_bytes = bytes(str(time.time()), 'latin-1') # Assumes `data` is also a string.
		resetcode=hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()

		#set_resetcode=db.session.query(User).filter(User.username==form.username.data).update({'passresetcode': resetcode,'last_password_reset': time.time()})
		#db.session.commit()

		subject="Password Reset Link"
		resetlink = ""
		link = "<a href='{}{}?m={}'> Reset Password </a>".format('http://127.0.0.1:5000/','reset_password',resetcode)

		##this is used for the mean time till the app is hosted on the internet#

		##validate password#
		if len(myfunc.check_password_strength(form.password.data))>0:
			resp=myfunc.check_password_strength(form.password.data)[0]
			return {'status':2,'message':resp}

		User.query.filter_by(username=form.username.data).update({'password':generate_password_hash(form.password.data),"temp_password":generate_password_hash(form.password.data)})
		db.session.commit()

		return {'status':1,'message':'password was changed successfully.'}


	def is_temp_password(self,userid,password):
		user=User.query.filter_by(userid=userid).first()
		if user.temp_password is not None:
			if check_password_hash(user.temp_password, password):
				return True

		return False

	def change_temp_password(self,userid,password):

		if len(myfunc.check_password_strength(password))>0:

			resp=myfunc.check_password_strength(password)[0]
			return {'status':2,'message':resp}

		##change user's password to the new one#
		db.session.query(User).filter(User.userid==userid).update({'password':generate_password_hash(password)})
		db.session.commit()
		
		return {'status':1,'message':'All good.'}

	def changepassword(self,userid,old,new):
		user = User.query.filter_by(userid=userid).first()

		##check that the new password is not the temporary password#
		if self.is_temp_password(userid,new):
			return {'status':2,'message':'The new password is the same as the temporary password used to create your account. You must change it.'}

		##check that the new password ha not been used recently#
		if new == user.last_password_reset:
			return {'status':2,'message':'You have used this password previously. Please change it.'}


		##validate new password#
		if len(myfunc.check_password_strength(new))>0:

			resp=myfunc.check_password_strength(new)[0]
			return {'status':2,'message':resp}

		##change password#
		db.session.query(User).filter_by(userid=userid).update({
			'last_password_reset':old,
			'password':generate_password_hash(new)
			})
		db.session.commit()

		return {'status':1,'message':'Password changed successfully.'}

	def get_skills(self, userid):
		user = User.query.filter_by(userid=userid).first()
		met = user.skill_metrix

		html += '<table class="table table-bordered table-striped">'
		html += '<thead><tr>'
		html += '<th scope="col">S/N</th>'
		html += '<th scope="col">Skill Title</th>'		
		html += '</tr></thead>'
		html += '<tbody>'

		if met is not None:
			skill_met = json.loads(met)
			#html = 
		return