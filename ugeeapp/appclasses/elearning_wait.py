from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup,send_file
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,MyQualification,Trainings,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
import time
import json
import os
import datetime
#from ugeeapp.appclasses.production import PRODUCTION
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib
import xlsxwriter
from io import BytesIO
import numpy as np
import pandas as pd
#from ugeeapp.appclasses.adminclass import AdminRoles



class MYSCHOOL():

	def __init__(self):
		pass

	def get_user(self,userid=0):
		if userid == 0:
			user = User.query.order_by(User.sname.asc()).all()
		else:
			user = User.query.filter_by(userid=userid).first()
		return user

	def get_training(self,tid=0):
		if tid == 0:
			tr = Trainings.query.order_by(Trainings.tid.desc()).all()
		else:
			tr = Trainings.query.filter_by(tid=tid).first()
		return tr

	def get_training_by_t_code(self,tcode):
		tr = Trainings.query.filter_by(t_code=tcode).first()
		return tr

	def get_departments(self,department_id=0):

		department = [{'name':'PSG','value':1},{'name':'MSG','value':2},{'name':'QA','value':3},{'name':'WHSE','value':4},{'name':'SAFETY','value':5},{'name':'HR','value':6},{'name':'STORE ROOM','value':7}]
		if department_id == 0:
			dept = department
		else:
			dept = [i for i in department if i['value'] == department_id]
		return dept				

	def get_training_report(self,form):
		"""This function returns trainng report for all trainings on the platform. 			
		"""

		users = User.query.all()
		
	
		html = '<table class="table table-bordered table-striped" id="general_repo">'

		#row for general plant completion
		gen_repo = self.get_general_report()
		html += '<div class="col-md-2 tabb1">'
		html += '<button title="export to excell" type="button" onclick="exportTableToExcel()">'
		html += '<i class="fas fa-file-excel" style="font-size:24px;color:green;"></i>'
		html += '</button></div>'		

		html += '<div class="col-md-12 tabb1"><hr style="border: solid 2px #179cd7;"></div>'
		html += '</div>'

		html += '<thead><tr>'

		#html += '<div class="row">'
		#html += '<div class="col-md-12 tabb1"><hr style="border: solid 2px #179cd7;"></div>'

		#html += '<div class="col-md-4"><span style="background:#179cd7; color:white; padding: 7px 7px">'
		html += '<th>Plant Overall:</th>' 
		html += '<th>' + str(gen_repo["total"] if gen_repo["total"] >= 0 else "Nil")+'%</th>'
		#html += '%</span></div>'
		#html += '<div class="col-md-2"><span style="background:#179cd7; color:white; padding: 7px 7px">'
		html += '<th>Mandatory: </th><th>'+ str(gen_repo["m"] if gen_repo["m"] >= 0 else "Nil")+'%</th>'
		#html += '%</span></div>'
		#html += '<div class="col-md-2"><span style="background:#179cd7; color:white; padding: 7px 7px">'
		html += '<th >Priority A: </th><th>' + str(gen_repo["a"] if gen_repo["a"] >= 0 else "Nil") + '%</th>'
		#html += '%</span></div>'
		#html += '<div class="col-md-2"><span style="background:#179cd7; color:white; padding: 7px 7px">B: '
		#html += str(gen_repo["b"] if gen_repo["b"] >= 0 else "Nil")
		#html += '%</span></div>'		 
		html += '</tr>' #end_row 

		if form['scope'] == 'DEPARTMENT':
			html += '<tr>'
			html += '<th scope="col">S/N</th>'
			html += '<th scope="col">Department Name</th>'
			html += '<th scope="col">Overall (%)</th>'
			html += '<th scope="col">Mandatory (%)</th>'
			html += '<th scope="col">Priority A (%)</th>'
			html += '<th scope="col">Priority B (%)</th>'					
			html += '</tr></thead>'
			html += '<tbody>'

			departments = self.get_departments()
			count = 0

			for dept in departments:
				get_report = self.get_department_report(dept['value']) #complete traininings report for department
				count += 1
				html += '<tr>'
				html += '<td>' + str(count) + '</td>'
				html += '<td>' + dept['name'] + '</td>'
				html += '<td>'
				html += str(get_report["total"] if get_report['total'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["m"] if get_report['m'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["a"] if get_report['a'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				html += '</td>'				
				html += '</tr>'
		else:	
			#table for individual total completion
			html += '<tr>'
			html += '<th scope="col">S/N</th>'
			html += '<th scope="col">Employee Name</th>'
			html += '<th scope="col">Overall (%)</th>'
			html += '<th scope="col">Mandatory (%)</th>'
			html += '<th scope="col">Priority A (%)</th>'
			html += '<th scope="col">Priority B (%)</th>'					
			html += '</tr></thead>'
			html += '<tbody>'
		
			if form['scope'] == 'GENERAL':
				users = self.get_user()
				count = 0

				for user in users:
					get_report = self.get_user_report(user.userid) #complete traininings report for user
					count += 1
					html += '<tr>'
					html += '<td>' + str(count) + '</td>'
					html += '<td>' + "{} {}".format(user.sname, user.fname) + '</td>'
					html += '<td>' 
					html += str(get_report["total"] if get_report["total"] >=0 else 'Nil') 
					html += '</td>'
					html += '<td>' 
					html += str(get_report['m'] if get_report["m"] >=0 else 'Nil') 
					html += '</td>'
					html += '<td>' 
					html += str(get_report['a'] if get_report["a"] >=0 else 'Nil') 
					html += '</td>'
					html += '<td>' 
					html += str(get_report['b'] if get_report["b"] >=0 else 'Nil') 
					html += '</td>'				
					html += '</tr>'

			elif form['scope'].isnumeric():
				user = self.get_user(form['scope'])
				count = 1					
				get_report = self.get_user_report(user.userid) #complete traininings report for user
				
				html += '<tr>'
				html += '<td>' + str(count) + '</td>'
				html += '<td>' + "{} {}".format(user.sname, user.fname) + '</td>'
				html += '<td>'
				html += str(get_report["total"] if get_report['total'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["m"] if get_report['m'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["a"] if get_report['a'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				html += '</td>'				
				html += '</tr>'						
			
		html += '</tbody>'
		html += '</table>'

		
		return html

	def get_general_report(self,tid=0):
		"""	This will generate general completion report for a given training whose id is provided
			else it will generate competion report for all trainings for all users in the plantform 
			that are memebers of the org.
		"""
		tid = int(tid)
		users = self.get_user()

		mandatory = 0
		prio_a = 0
		prio_b = 0
		total_passed = 0

		total_mand = 0
		total_prio_a = 0
		total_prio_b = 0
		total_tr = 0

		if tid > 0:
			for user in users:				
				if tid in [int(x.tid) for x in self.get_user_trainings(user.userid)]:
					total_tr += 1
					if 	self.get_user_report(user.userid,tid) == 100:
						total_passed += 1

			if total_tr >0:
				xyz = "{:0.2f}".format((total_passed/total_tr)*100)
				completion = float(xyz)
			else:
				completion = -1.0	

			return 	completion

		for user in users:			
			trainings = self.get_user_trainings(user.userid)
			if trainings is not None:
				for training in trainings:
					if self.get_user_report(user.userid,training.tid) == 100:
						total_passed += 1
						if training.priority ==  "M":
							mandatory += 1
						elif training.priority ==  "A":
							prio_a += 1
						elif training.priority ==  "B":
							prio_b += 1	
			total_mand += len(self.get_user_mandatories(user.userid))
			total_prio_a += len(self.get_user_priority_a(user.userid))
			total_prio_b += len(self.get_user_priority_b(user.userid))	
			total_tr += len(trainings)

		t_completion = float("{:0.2f}".format((total_passed/total_tr)*100))
		if total_mand >0:
			m_completion = 	float("{:0.2f}".format((mandatory/total_mand)*100))
		else:
			m_completion = -1.0
		if total_prio_a >0:
			a_completion = 	float("{:0.2f}".format((prio_a/total_prio_a)*100))
		else:
			a_completion = -1.0
		if total_prio_b >0:
			b_completion = 	float("{:0.2f}".format((prio_b/total_prio_b)*100))
		else:
			b_completion = -1.0			

		return {"total":t_completion,"m":m_completion,"a":a_completion,"b":b_completion}

	def get_user_report(self,userid,tid=0):
		"""	This function will get user completion report for a training when training id is provided
			else it will generate total completion report for the user for all trainings based on the
			skill priority classifications.
		"""
		if tid > 0:
			##get report for a single training## 
			complete = db.session.query(MyQualification).filter(MyQualification.training_id==tid,MyQualification.userid==userid,MyQualification.status=="PASSED").first()
			if complete:
				return 100
			else:
				return 0.0
		else:
			##get report for all trainings#
			mandatory_passed = []
			prio_a_passed = []
			prio_b_passed = []
			total_passed = []

			trainings = self.get_training()
			mandatory = [x for x in Trainings.query.filter_by(priority="M").all()]
			prio_a = [x for x in Trainings.query.filter_by(priority="A").all()]
			prio_b = [x for x in Trainings.query.filter_by(priority="B").all()]

			for training in trainings:
				complete = db.session.query(MyQualification).filter(MyQualification.training_id==training.tid,MyQualification.userid==userid,MyQualification.status=="PASSED").first()
				if complete:
					total_passed.append(training) 

					if training.priority == "A":
						prio_a_passed.append(training)
					elif training.priority == "M":
						mandatory_passed.append(training)
					elif training.priority == "B":
						prio_b_passed.append(training)

			if trainings is not None:
				total_completion = float("{:0.2f}".format((len(total_passed)/len(trainings))*100))
			else:
				total_completion = -1.0	
			if 	len(mandatory) >0:
				mandatory_completion = float("{:0.2f}".format((len(mandatory_passed)/len(mandatory))*100))
			else:
				mandatory_completion = -1.0
			if len(prio_a) > 0:
				prio_a_completion = float("{:0.2f}".format((len(prio_a_passed)/len(prio_a))*100))
			else:
				prio_a_completion = -1.0
			if len(prio_b) > 0:
				prio_b_completion = float("{:0.2f}".format((len(prio_b_passed)/len(prio_b))*100))
			else:
				prio_b_completion = -1.0

			
			return {"total":total_completion,"m":mandatory_completion,"a":prio_a_completion,"b":prio_b_completion}

	def get_user_mandatories(self,userid):
		tr = Trainings.query.filter_by(priority="M").all()
		return  tr

	def get_user_priority_a(self,userid):
		""""This function will retrieve all priority A trainings  associated with the user's user_role """
		from ugeeapp.appclasses.adminclass import AdminRoles
		new = AdminRoles()
		t_codes = []
		prio_a_trs = []

		for role in new.get_user_roles(userid):
			if role.trainings:
				trs = json.loads(role.trainings)
				t_codes.extend(trs)

		#now remove duplicates from tcodes
		t_codes = [x for x in set(t_codes)]

		#get trainings by tcodes
		for x in t_codes:
			tr = self.get_training_by_t_code(x)
			if tr.priority != 'M':
				prio_a_trs.append(tr)

		if prio_a_trs == [] :
			prio_a_trs = None

		return  prio_a_trs

	def get_user_priority_b(self,userid):
		tr = Trainings.query.filter_by(priority="B").all()
		return  tr

	def get_user_trainings(self,userid):
		#tr = Trainings.query.order_by(Trainings.tid.desc()).all()
		tr = []
		for i in self.get_user_mandatories(userid):
			tr.append(i)
		if self.get_user_priority_a(userid):
			tr.extend(self.get_user_priority_a(userid))

		return  tr			

	def get_department_report(self,department_id,tid=0):
		tid = int(tid)
		users = User.query.filter_by(department=department_id).all()

		mandatory = 0
		prio_a = 0
		prio_b = 0
		total_passed = 0

		total_mand = 0
		total_prio_a = 0
		total_prio_b = 0
		total_tr = 0

		if tid > 0:
			for user in users:				
				if tid in [int(x.tid) for x in self.get_user_trainings(user.userid)]:
					total_tr += 1
					if 	self.get_user_report(user.userid,tid) == 100:
						total_passed += 1

			if total_tr >0:
				completion = float("{:0.2f}".format((total_passed/total_tr)*100))
			else:
				completion = -1.0	

			return 	completion

		for user in users:			
			trainings = self.get_user_trainings(user.userid)
			if trainings is not None:
				for training in trainings:
					if self.get_user_report(user.userid,training.tid) == 100:
						total_passed += 1
						if training.priority ==  "M":
							mandatory += 1
						elif training.priority ==  "A":
							prio_a += 1
						elif training.priority ==  "B":
							prio_b += 1	
			total_mand += len(self.get_user_mandatories(user.userid))
			total_prio_a += len(self.get_user_priority_a(user.userid))
			total_prio_b += len(self.get_user_priority_b(user.userid))	
			total_tr += len(trainings)

		t_completion = float("{:0.2f}".format((total_passed/total_tr)*100))
		if total_mand >0:
			m_completion = 	float("{:0.2f}".format((mandatory/total_mand)*100))
		else:
			m_completion = -1.0
		if total_prio_a >0:
			a_completion = 	float("{:0.2f}".format((prio_a/total_prio_a)*100))
		else:
			a_completion = -1.0
		if total_prio_b >0:
			b_completion = 	float("{:0.2f}".format((prio_b/total_prio_b)*100))
		else:
			b_completion = -1.0			

		return {"total":t_completion,"m":m_completion,"a":a_completion,"b":b_completion}
 

	def add_training(self,form,edit=0):

		main = "main"
		#suck = "suc"
		#extra = "extra"		

		title = form['title']
		department = form['depart']
		owner = form['owner']
		exp = form['exp']
		#q_link = form['quiz']
		pass_mark = form['pasmk']
		priority = form['prio']

		titles = title.split()
		for x in titles:
			main += "_{}".format(x.lower())	
		

		if edit > 0:

			#check if title already exists for another course
			check = db.session.query(Trainings).filter(Trainings.title==title.title(),Trainings.tid != edit).count()
			if check > 0:
				return {'status':2, 'message':'This course title already exists for another course.'}

			#edit course now
			db.session.query(Trainings).filter(Trainings.tid == edit).update({
				'title': title.title(),
				'department' : department,
				'owner' : owner,
				'expiry' : exp,
				'last_review' : datetime.now(),
				'doc_link' : form['doc_link'],
				'pass_mark' : pass_mark,
				'priority' : priority
				})
			db.session.commit()

			return {'status':1, 'message': 'Course was updated successfully.'}

		#generate training code here with a function
		def generate_tcode():
			"""
			This function generates a UNIQUE CODE for each training
			It does this by repeating itself if a particular code being generated 
			is found to exist in the database
			"""
			tcode = myfunc.randomNumbs(6)
			check = db.session.query(Trainings).filter(Trainings.t_code==tcode).count()
			if check > 0:
				generate_tcode()
			return tcode

		log = Trainings()
		log.title = title.title()
		log.department = department
		log.owner = owner
		log.expiry = exp
		log.last_review = datetime.now()
		#log.quiz_link = q_link		
		log.doc_link = "{}{}".format('/static/documents/e_learning/',main)
		log.pass_mark = pass_mark
		log.priority = priority
		log.t_code = generate_tcode()

		db.session.add(log)
		db.session.commit()


		return {'status':1, 'message': 'Training was added successfully.'}

	def add_trainingxxx(self,form,files):

		main = "main"
		suck = "suc"
		extra = "extra"

		suc_link = []
		extra_resource = []

		title = form['title']
		department = form['depart']
		owner = form['owner']
		exp = form['exp']
		q_link = form['quiz']

		titles = title.split()
		for x in titles:
			main += "_{}".format(x.lower())
			suck += "_{}".format(x.lower())
			extra += "_{}".format(x.lower())

		main_file = files['material']

		if main_file.filename != '':
			file_ext = os.path.splitext(main_file.filename)[1]

			if file_ext not in app.config['UPLOAD_EXTENSIONS']:
				return {'status':2, 'message': 'Unsupported file type: Main Training Material.'}
			else:
				main_file.save(os.path.join("http://192.168.130.196:5000/",'static/documents/e_learning/', "{}{}".format(main,file_ext)))
		else:
			return {'status':2, 'message': 'Main Training Material is not found.'}

		suc_files = files.getlist('suc')

		if len(suc_files) > 0 :
			for suc in suc_files:
				if suc.filename != '':
					file_ext2 = os.path.splitext(suc.filename)[1]

					if file_ext2 not in app.config['UPLOAD_EXTENSIONS']:
						return {'status':2, 'message': 'Unsupported file type: SUCs.'}
					else:
						suc.save(os.path.join('static/documents/e_learning', "{}{}".format(suck,file_ext2)))
						suc_link.append("{}{}{}".format('static/documents/e_learning/',suck,file_ext2))
		
		other_files = files.getlist('other_file')

		if len(other_files) > 0 :
			for other in other_files:
				if other.filename != '':
					file_ext3 = os.path.splitext(other.filename)[1]

					if file_ext3 not in app.config['UPLOAD_EXTENSIONS']:
						return {'status':2, 'message': 'Unsupported file type: SUCs.'}
					else:
						other.save(os.path.join('static/documents/e_learning', "{}{}".format(extra,file_ext3)))
						extra_resource.append("{}{}{}".format('static/documents/e_learning/',extra,file_ext3))


		log = Trainings()
		log.title = title
		log.department = department
		log.owner = owner
		log.expiry = exp
		log.last_review = datetime.now()
		log.quiz_link = q_link
		log.suc_link = json.dumps(suc_link)
		log.doc_link = "{}{}{}".format('static/documents/e_learning/',main,file_ext)
		log.extra_resource = json.dumps(extra_resource)
	    #db.session.add(log)
	    #db.session.commit()


		return {'status':1, 'message': 'Training was added successfully.'}

	def delete_course(self, data):

		##check if there is atleast one training record for this course
		check = MyQualification.query.filter_by(training_id=data['tid']).count()

		if check > 0:

			return {'status':2, 'message': 'This course cannot be deleted, there is an existing training record for it.'}

		##delete training
		db.session.query(Trainings).filter(Trainings.tid==data['tid']).delete()
		db.session.commit()

		return {'status':1, 'message': 'Course deleted successfully.'}

	def record_training_score(self,data):


		get_tr = Trainings.query.filter(Trainings.tid==data['tid']).first()

		if int(data['score']) >= int(get_tr.pass_mark):
			status = 'PASSED'
		else:
			status = 'REPEAT'

		##check if qualification record already exist for this user on this course#
		qualz = db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).first()

		if qualz is not None:
			##update data otherwise add
			db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).update({
				'score':int(data['score']),
				'q_date': datetime.now(),
				'status': status
				})
			db.session.commit()

		else:

			log = MyQualification()
			log.userid = session['userid']
			log.q_date = datetime.now()
			log.training_id = get_tr.tid
			log.title = get_tr.title
			log.department = get_tr.department
			log.score = int(data['score'])
			log.status = status

			db.session.add(log)
			db.session.commit()

		return {'status':1, 'message': 'Weldone'}

	def fetch_trainings(self, data):

		get_courses = None
		#prioritty = ['A','M','B']
		#departmentt = ['SAFETY','QUALITY','HR','PSG','MSG','WHSE']

		html = '<div class="table-responsive">'						

		if data['filter'] == 'all' or data['value'] == 'all':		
			get_courses = self.get_user_trainings(session['userid']) #db.session.query(Trainings).order_by(Trainings.title.asc()).all()
		elif data['filter'] == 'priority':
			#get_courses = db.session.query(Trainings).filter(Trainings.priority==data['value']).order_by(Trainings.title.asc()).all()
			get_courses = []
			for i in self.get_user_trainings(session['userid']):
				if i.priority == data['value']:
					get_courses.append(i)
		elif data['filter'] == 'department':
			#get_courses = db.session.query(Trainings).filter(Trainings.department==data['value']).order_by(Trainings.title.asc()).all()
			get_courses = []
			for i in self.get_user_trainings(session['userid']):
				if i.department == data['value']:
					get_courses.append(i)
		else:		
			#get_courses = db.session.query(Trainings).order_by(Trainings.title.asc()).all()
			get_courses = self.get_user_trainings(session['userid'])
				
		if get_courses is not None:
			html += '<table class="table table-bordered table-striped">'
			html += '<thead><tr>'
			html += '<th scope="col">Code</th>'
			html += '<th scope="col">Skill Title</th>'
			html += '<th scope="col">Dept</th>'
			html += '<th scope="col">Priority</th>'
			html += '<th scope="col">Owner</th>'
			html += '<th scope="col">Outline</th>'
			html += '<th scope="col">Quiz</th>'
			html += '<th scope="col">Score (%)</th>'
			#html += '<th scope="col">Expiry</th>'
			html += '</tr></thead>'
			html += '<tbody>'

			count = 1

			if data['value'] != "complete" and data['value'] != "not-complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					main = 'tr'
					titles = course.title.split()
					for x in titles:
						main += "_{}".format(x.lower())

					html += '<tr>'
					html += '<td><span style="color:#179cd7">'+course.t_code+'</span></td>'
					html += '<td>'+course.title+'</td>'
					html += '<td>'+course.department+'</td>'
					html += '<td>'+course.priority+'</td>'
					html += '<td>'+self.get_course_owner(course.owner)+'</td>'

					if self.check_file(course.doc_link):
						html += '<td><a href="'+course.doc_link+'" target="_blank">course outline</a></td>'
					else:
						html += '<td></td>'
					
					if get_data :
						html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						if get_data.score >= course.pass_mark:
							html += '<td><span style="color:green">'+str(get_data.score)+'</span></td>'
						else:
							html += '<td><span style="color:red">'+str(get_data.score)+'</span></td>'
					else:
						html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						html += '<td><span style="color:#000">Not Done</span></td>'
					count += 1
					html += '</tr>'

			elif data['value'] == "complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					if get_data and get_data.score >= course.pass_mark:	
						main = 'tr'
						titles = course.title.split()
						for x in titles:
							main += "_{}".format(x.lower())

						html += '<tr>'
						html += '<td>'+str(count)+'</td>'
						html += '<td>'+course.title+'</td>'
						html += '<td>'+course.department+'</td>'
						html += '<td>'+course.priority+'</td>'
						html += '<td>'+self.get_course_owner(course.owner)+'</td>'

						if self.check_file(course.doc_link):
							html += '<td><a href="'+course.doc_link+'" target="_blank">course outline</a></td>'
						else:
							html += '<td></td>'
						
						if get_data :
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							if get_data.score >= course.pass_mark:
								html += '<td><span style="color:green">'+str(get_data.score)+'</span></td>'
							else:
								html += '<td><span style="color:red">'+str(get_data.score)+'</span></td>'
						else:
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							html += '<td><span style="color:#000">Not Done</span></td>'
						count += 1
						html += '</tr>'

			elif data['value'] == "not-complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					if get_data is None or get_data.score < course.pass_mark:	
						main = 'tr'
						titles = course.title.split()
						for x in titles:
							main += "_{}".format(x.lower())

						html += '<tr>'
						html += '<td>'+str(count)+'</td>'
						html += '<td>'+course.title+'</td>'
						html += '<td>'+course.department+'</td>'
						html += '<td>'+course.priority+'</td>'
						html += '<td>'+self.get_course_owner(course.owner)+'</td>'

						if self.check_file(course.doc_link):
							html += '<td><a href="'+course.doc_link+'" target="_blank">course outline</a></td>'
						else:
							html += '<td></td>'
						
						if get_data:
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							if get_data.score >= course.pass_mark:
								html += '<td><span style="color:green">'+str(get_data.score)+'</span></td>'
							else:
								html += '<td><span style="color:red">'+str(get_data.score)+'</span></td>'
						else:
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							html += '<td><span style="color:#000">Not Done</span></td>'
						count += 1
						html += '</tr>'


			html += '</tbody>'
			html += '</table>'

		
		else:
			html += "<div class='alert alert-danger'>No results found for your selection.</div>"
		html += '</div>'

		##fetch percentage completion data#
		total = self.fetch_total_training_percent(get_courses)
		mandatory = self.fetch_mandatory_training_percent(get_courses)
		prio_a = self.fetch_priority_a_training_percent(get_courses)
		prio_b = self.fetch_priority_b_training_percent(get_courses)

		return {'status':1, 'data': html,'all':total, 'man':mandatory, 'pa':prio_a, 'pb':prio_b}

	def get_course_owner(self,userid):

		user = User.query.filter(User.userid==userid).first()

		return "{} {}".format(user.sname, user.fname)

	def fetch_qualification_records(self, form):
		data = []
		count = 1

		##fetch users
		if form["scope"].isnumeric():
			#training report for a particular user
			users = self.get_user(form["scope"])

			info = db.session.query(MyQualification).filter(MyQualification.userid==users.userid,MyQualification.training_id==form['id']).first()

			mr = {}
			mr['name'] = "{} {}".format(users.sname,users.fname)
			mr['department'] = users.department
			mr['count'] = count

			if info is not None:
				
				if info.status == 'PASSED':
					mr['status'] = Markup('<span style="color:green">'+info.status+'</span>')
					mr['score'] =  Markup('<span style="color:green">'+str(info.score)+'</span>')
				else:
					mr['status'] =  Markup('<span style="color:yellow">Not Yet Qualified</span>')
					mr['score'] =  Markup('<span style="color:yellow">'+str(info.score)+'</span>')
			else:
				mr['status'] =  Markup('<span style="color:red">Not Qualified</span>')
				mr['score'] =  Markup('<span style="color:red">None</span>')		

			data.append(mr)
		
		elif form["scope"].isalpha() and form["scope"] == "GENERAL": 
			#specific training report for all users
			users = self.get_user()		

			##get individual records for the course#		
		
			for user in users:
				info = db.session.query(MyQualification).filter(MyQualification.userid==user.userid,MyQualification.training_id==form['id']).first()

				mr = {}
				mr['name'] = "{} {}".format(user.sname,user.fname)
				mr['department'] = user.department
				mr['count'] = count

				if info is not None:
					
					if info.status == 'PASSED':
						mr['status'] = Markup('<span style="color:green">'+info.status+'</span>')
						mr['score'] =  Markup('<span style="color:green">'+str(info.score)+'</span>')
					else:
						mr['status'] =  Markup('<span style="color:yellow">Not Yet Qualified</span>')
						mr['score'] =  Markup('<span style="color:yellow">'+str(info.score)+'</span>')
				else:
					mr['status'] =  Markup('<span style="color:red">Not Qualified</span>')
					mr['score'] =  Markup('<span style="color:red">None</span>')


				count += 1

				data.append(mr)

		elif form["scope"].isalpha() and form["scope"] == "DEPARTMENT": 
			#training report for all users
			departments = self.get_departments()		

			##get individual records for the course#		
		
			for dept in departments:
				info = self.get_department_report(dept["value"],form["id"])

				mr = {}
				mr['name'] = "N/A"
				mr['department'] = dept["value"]
				mr['count'] = count

				mr['status'] = 'N/A'
				mr['score'] =  info
				
				count += 1

				data.append(mr)		

		course = Trainings.query.filter(Trainings.tid==form['id']).first()

		title = course.title

		p = self.get_general_report(form['id'])
		if p >=0:
			overall = "{}%".format(p)
		else:
			overall = "Nil"	

		return {'status':1, 'data':data, 'title':title,"overall":overall}

	def check_file(self,link):


		from os.path import exists
		mylink = '/e_learning?action=GET-QUIZ&template=e_learning/tr_basic_fire_fighting.html&id=1&pass=100&tid=1' #'http://192.168.130.196:5000'+link

		if exists(mylink) :

			return True

		return True

	def fetch_total_training_percent(self, query):

		passed = []

		if query and len(query) >0:
			for course in query:
				get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

				if get_data:
					if get_data.score >= course.pass_mark:
						passed.append(1)

			passed = len(passed)
			total = len(query)
			percent = (passed/total) * 100
			percent = "{:0.2f}%".format(percent)

		else:
			percent = "{}".format('N/A')



		return percent

	def fetch_mandatory_training_percent(self, query):

		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'M':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					if get_data:
						if get_data.score >= course.pass_mark:
							passed.append(1)

			if len(man) > 0:
				passed = len(passed)
				total = len(man)
				percent = (passed/total) * 100
				percent = "{:0.2f}%".format(percent)

		else:
			percent = "{}".format('N/A')



		return percent

	def fetch_priority_a_training_percent(self, query):

		percent = "{}".format('N/A')
		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'A':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					if get_data:
						if get_data.score >= course.pass_mark:
							passed.append(1)

			if len(man) > 0:
				passed = len(passed)
				total = len(man)
				percent = (passed/total) * 100
				percent = "{:0.2f}%".format(percent)


		return percent

	def fetch_priority_b_training_percent(self, query):

		percent = "{}".format('N/A')
		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'B':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					if get_data:
						if get_data.score >= course.pass_mark:
							passed.append(1)

			if len(man) > 0:
				passed = len(passed)
				total = len(man)
				percent = (passed/total) * 100
				percent = "{:0.2f}%".format(percent)

		return percent

	def export_data_to_excell(self,item):

		
		return 		



