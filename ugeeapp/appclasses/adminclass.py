from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup,send_file
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,UserRoles,Department,MyQualification,Trainings,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
import time
import json
import os
import datetime
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib
import xlsxwriter
from ugeeapp.appclasses.elearning import MYSCHOOL



class AdminRoles():

	def __init__(self):
		pass

	def get_user_roles(self,userid=0):
		"""This function will fetch all roles assigned to all users on the platform, or the roles(s) assigned to a specified user """
		roles = []
		if userid == 0:			
			users = User.query.all()
			for user in users:				
				try:
					if user.user_roles is not None:						
						items = json.loads(user.user_roles)
						for item in items:
							xrole = self.get_admin_roles(item)
							#print(user.sname,':',xrole.rid)
							roles.append(xrole)
				except:
					roles = []			

		else:			
			user = User.query.filter_by(userid=userid).first()
			try:
				if user.user_roles is not None:
					items = json.loads(user.user_roles)
					for item in items:
						xrole = self.get_admin_roles(item)
						roles.append(xrole)
			except:
				roles = []			

		return roles

	def get_admin_roles(self,rid=0):
		"""This function will fetch all the roles available on the database or a specific role if the id is provided"""
		
		if rid == 0:
			roles = UserRoles.query.all()
		else:
			roles = db.session.query(UserRoles).filter(UserRoles.rid==rid).first()

		return roles

	def fetch_skillset(self,rid):
		"""This function will fetch skills required for a given rolid. """
		role = self.get_admin_roles(rid)
		new = MYSCHOOL()
		trainings = []

		if role.trainings:
			tr = json.loads(role.trainings)
			if len(tr) == 0:
				trainings = None
				return trainings

			for i in tr:
				mr = {}
				x = new.get_training_by_t_code(i)
				mr['tid'] = x.tid
				mr['title'] = x.title
				mr['t_code'] = x.t_code
				mr['priority'] = x.priority
				trainings.append(mr)
		else:
			trainings = None
		
		return trainings

	def add_skills_to_role(self,rid,tcodes):
		"""This function will add supplied training codes to the given training"""

		new = MYSCHOOL()

		wrong_codes = []
		mand_tr = []

		pro_codes = [x.strip() for x in tcodes.split(',')]

		#check if a wrong training code has been entered
		for code in pro_codes:
			if not new.get_training_by_t_code(code):
				wrong_codes.append(code)

		if wrong_codes != []:
			response = Markup("<div class='alert alert-danger'>The action was not successful because the following codes did not match with any trainings in our record: {}</div>".format(wrong_codes))
			return json.dumps({'status':2,'message':response})

		#check for mandatory trainings in the new trainings to be added
		for cod in pro_codes:
			tr = new.get_training_by_t_code(cod)
			if tr.priority == 'M':
				mand_tr.append(code)

		if mand_tr != []:
			response = Markup("<div class='alert alert-danger'>The action was not successful because the following codes matched with Mandatory trainings: {}</div>".format(mand_tr))
			return json.dumps({'status':2,'message':response})

		#add training codes to role
		role = self.get_admin_roles(rid)
		if role.trainings:
			tr_json = json.loads(role.trainings)
			tr_json.extend(pro_codes)
			tr_json = [x for x in set(tr_json)]
			new_codes = json.dumps(tr_json)
		else:
			pro_codes = [x for x in set(pro_codes)]
			new_codes = json.dumps(pro_codes)

		db.session.query(UserRoles).filter(UserRoles.rid==rid).update({'trainings':new_codes})
		db.session.commit()

		response = Markup("<div class='alert alert-success'>Skills added successfully.</div>")

		return json.dumps({'status':1,'message':response})

	def delete_skill_from_role(self,rid,tcode):
		role = self.get_admin_roles(rid)

		#tcode = "{}".format(tcode)
	
		tr_json = json.loads(role.trainings)
		if tcode not in tr_json:
			response = Markup("<div class='alert alert-danger'>Skill not in the list.</div>")
			return json.dumps({'status':2,'message':response})

		tr_json.pop(tr_json.index(tcode))		
		new_codes = json.dumps(tr_json)

		db.session.query(UserRoles).filter(UserRoles.rid==rid).update({'trainings':new_codes})
		db.session.commit()

		response = Markup("<div class='alert alert-success'>Skill removed successfully.</div>")

		return json.dumps({'status':1,'message':response})

	def add_user_role(self,form):

		new = UserRoles()
		new.rname = form.name.data
		new.description = form.description.data
		new.report_to = form.report_to.data
		if form.skills.data:
			new.trainings = json.dumps(form.skills.data)
		if form.rnr.data:
			new.rnr = json.dumps([x.strip() for x in form.rnr.data.split(';')])

		db.session.add(new)
		db.session.commit()
		
		resp = Markup("<div class='alert alert-success'>Role added successfully.</div>")

		return {'status':1,'message':resp}

	def update_admin_role(self, rid, form):

		if form.rnr.data:
			rnr = json.dumps([x.strip() for x in form.rnr.data.split(';')])
		else:
			rnr = ''

		db.session.query(UserRoles).filter_by(rid=rid).update({
			'rname':form.name.data,\
			'description':form.description.data,\
			'report_to':form.report_to.data,\
			'rnr':rnr})
		db.session.commit()

		return Markup("<div class='alert alert-success'>Role was updated successfully.</div>")

	def delete_admin_role(self,roleid):

		#check if a user has been assigned to this role
		oro = [x.rid for x in self.get_user_roles()]
		
		if int(roleid) in oro:
			resp = Markup("<div class='alert alert-danger'>This role cannot be deleted because one or more users have been assigned to it.</div>")
			return json.dumps({'status':2,'message':resp})

		else:
			return json.dumps({'status':1,'message':'success'})
			UserRoles.query.filter_by(rid=roleid).delete()
			db.session.commit()

			resp = Markup("<div class='alert alert-success'>Role deleted successfully.</div>")
			return json.dumps({'status':1,'message':resp})

	def add_department(self,frm):
		departments = [
		{'abbr':'PSG','id':1, 'description':'Packing operations department','hod':26},
		{'abbr':'MSG','id':2, 'description':'Making operations department','hod':74},
		{'abbr':'QA','id':3, 'description':'Quality Assurance department','hod':67},
		{'abbr':'WHSE','id':4, 'description':'Warehouse department','hod':28},
		{'abbr':'HS&E','id':5, 'description':'Healt, Safety & Enveironment department','hod':22},
		{'abbr':'HR','id':6, 'description':'Human Resources department','hod':31},
		{'abbr':'STR_ROOM','id':7, 'description':'Store Room department','hod':31},
		{'abbr':'IT','id':8, 'description':'Information Technology department','hod':31},
		{'abbr':'FINANCE','id':9, 'description':'Finance department','hod':31}
		]
		
		db.session.query(Department).delete()
		db.session.commit()

		for form in departments:
			log = Department()
			log.did = form['id']
			log.abbr = form['abbr']
			log.description = form['description']
			log.hod = form['hod']
			
			db.session.add(log)
			db.session.commit()	

		return

	def get_departments(self,id=0):
		if id == 0:
			dept = Department.query.order_by(Department.abbr.asc()).all()
		else:
			dept = Department.query.filter_by(did=id).first()

		return dept	

