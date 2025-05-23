from flask import session,Markup
from ugeeapp.models import MyQualification,StepupCards,Trainings,User
import json
import os
import datetime
from datetime import datetime,timedelta
from werkzeug.utils import secure_filename
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
from ugeeapp import APP_ROOT
import calendar
from dateutil.relativedelta import relativedelta



class MYSCHOOL():

	def __init__(self):
		pass
	
	def get_user(self,userid=0):
		if userid == 0:
			user = User.query.filter_by(block_stat=0).order_by(User.sname.asc()).all()
		else:
			user = User.query.filter_by(userid=userid).first()
		return user

	def get_department_users(self,department):
		result = []

		users = self.get_user()
		for user in users:
			if user.department == int(department):
				result.append(user)

		return result

	def get_team_members(self,team,department):
		result = []
		users = self.get_department_users(department)
		if len(users) >0:
			for user in users:
				if user.team == team:
					result.append(user)

		return result

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
		from ugeeapp.appclasses.adminclass import AdminRoles
		new = AdminRoles()
		department = []

		for i in new.get_departments():
			mr = {}
			mr['name'] = i.abbr
			mr['value'] = i.did
			department.append(mr)
		
		if department_id == 0:
			dept = department
		else:
			dept = [i for i in department if i['value'] == department_id]
		return dept				

	def get_training_report(self,form):
		"""This function returns training report for all trainings on the platform. 			
		"""

		users = self.get_user()
		
	
		html = '<table class="table table-responsive table-bordered table-striped" id="general_repo">'

		#row for general plant completion
		gen_repo = self.get_general_report()
		html += '<div class="col-md-2 tabb1">'
		html += '<button title="export to excell" type="button" onclick="get_exportable_report()">'
		html += '<i class="fas fa-file-excel" style="font-size:24px;color:green;"></i>'
		html += '</button></div>'		

		html += '<div class="col-md-12 tabb1"><hr style="border: solid 2px #179cd7;"></div>'
		html += '</div>'

		html += '<thead><tr>'

		html += '<th>Plant Overall:</th>' 
		html += '<th>' + str(gen_repo["total"] if gen_repo["total"] >= 0 else "Nil")+'%</th>'
		html += '<th>Mandatory: </th><th>'+ str(gen_repo["m"] if gen_repo["m"] >= 0 else "Nil")+'%</th>'
		html += '<th >Priority A: </th><th>' + str(gen_repo["a"] if gen_repo["a"] >= 0 else "Nil") + '%</th>'
		html += '</tr>' #end_row 

		if form['scope'] == 'DEPARTMENT':
			html += '<tr>'
			html += '<th scope="col">S/N</th>'
			html += '<th scope="col">Department Name</th>'
			html += '<th scope="col">Overall (%)</th>'
			html += '<th scope="col">Mandatory (%)</th>'
			html += '<th scope="col">Priority A (%)</th>'
			#html += '<th scope="col">Priority B (%)</th>'					
			html += '</tr></thead>'
			html += '<tbody>'

			departments = self.get_departments()
			count = 0

			for dept in departments:
				get_report = self.get_department_report(dept['value']) #complete traininings report for department
				count += 1
				html += '<tr>'
				html += '<td>' + str(count) + '</td>'
				html += '<td><a target="_blank" href="/skills_matrix?action=DEPARTMENT&id='+str(dept['value'])+'" style="text-decoration:none">' + dept['name'] + '</a></td>'
				html += '<td>'
				html += str(get_report["total"] if get_report['total'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["m"] if get_report['m'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["a"] if get_report['a'] >= 0 else 'Nil')
				html += '</td>'
				#html += '<td>'
				#html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				#html += '</td>'				
				html += '</tr>'
		else:	
			#table for individual total completion
			html += '<tr>'
			html += '<th scope="col">S/N</th>'
			html += '<th scope="col">Employee Name</th>'
			html += '<th scope="col">Overall (%)</th>'
			html += '<th scope="col">Mandatory (%)</th>'
			html += '<th scope="col">Priority A (%)</th>'
			#html += '<th scope="col">Priority B (%)</th>'					
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
					html += '<td><a href="/skills_matrix?action=INDIVIDUAL&userid='+str(user.userid)+'&filter=all&value=" target="_blank" style="text-decoration:none">' + "{} {}".format(user.sname, user.fname) + '</a></td>'
					html += '<td>' 
					html += str(get_report["total"] if get_report["total"] >=0 else 'Nil') 
					html += '</td>'
					html += '<td>' 
					html += str(get_report['m'] if get_report["m"] >=0 else 'Nil') 
					html += '</td>'
					html += '<td>' 
					html += str(get_report['a'] if get_report["a"] >=0 else 'Nil') 
					html += '</td>'
					#html += '<td>' 
					#html += str(get_report['b'] if get_report["b"] >=0 else 'Nil') 
					#html += '</td>'				
					html += '</tr>'

			elif form['scope'].isnumeric():
				user = self.get_user(form['scope'])
				count = 1					
				get_report = self.get_user_report(user.userid) #complete traininings report for user
				
				html += '<tr>'
				html += '<td>' + str(count) + '</td>'
				html += '<td><a href="#" style="text-decoration:none">' + "{} {}".format(user.sname, user.fname) + '</a></td>'
				html += '<td>'
				html += str(get_report["total"] if get_report['total'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["m"] if get_report['m'] >= 0 else 'Nil')
				html += '</td>'
				html += '<td>'
				html += str(get_report["a"] if get_report['a'] >= 0 else 'Nil')
				html += '</td>'
				#html += '<td>'
				#html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				#html += '</td>'				
				html += '</tr>'						
			
		html += '</tbody>'
		html += '</table>'

		
		return html

	def get_exportable_training_report(self,form):
		"""This function returns trainng report for all trainings on the platform. 			
		"""

		users = self.get_user()
		
	
		html = '<table class="table table-responsive table-bordered table-striped" id="general_repo">'

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
			#html += '<th scope="col">Priority B (%)</th>'					
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
				#html += '<td>'
				#html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				#html += '</td>'				
				html += '</tr>'
		else:	
			#table for individual total completion
			html += '<tr>'
			html += '<th scope="col">S/N</th>'
			html += '<th scope="col">Employee Name</th>'
			html += '<th scope="col">Overall (%)</th>'
			html += '<th scope="col">Mandatory (%)</th>'
			html += '<th scope="col">Priority A (%)</th>'
			#html += '<th scope="col">Priority B (%)</th>'					
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
					#html += '<td>' 
					#html += str(get_report['b'] if get_report["b"] >=0 else 'Nil') 
					#html += '</td>'				
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
				#html += '<td>'
				#html += str(get_report["b"] if get_report['b'] >= 0 else 'Nil')
				#html += '</td>'				
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
					total_passed += self.get_user_report(user.userid,tid)
				
			if total_tr >0:
				xyz = "{:0.2f}".format((total_passed/total_tr))
				completion = float(xyz)
			else:
				completion = -1.0	

			return 	completion

		for user in users:			
			trainings = self.get_user_trainings(user.userid)
			if trainings is not None:
				for training in trainings:
					reap = self.get_user_report(user.userid,training.tid)
					total_passed += reap			
					if training.priority ==  "M":
						mandatory += reap
					elif training.priority ==  "A":
						prio_a += reap
					elif training.priority ==  "B":
						prio_b += reap

			total_mand += len(self.get_user_mandatories(user.userid))
			total_prio_a += len(self.get_user_priority_a(user.userid))
			total_prio_b += len(self.get_user_priority_b(user.userid))	
			total_tr += len(trainings)

		t_completion = float("{:0.2f}".format((total_passed/total_tr)))
		if total_mand >0:
			m_completion = 	float("{:0.2f}".format((mandatory/total_mand)))
		else:
			m_completion = -1.0
		if total_prio_a >0:
			a_completion = 	float("{:0.2f}".format((prio_a/total_prio_a)))
		else:
			a_completion = -1.0
		if total_prio_b >0:
			b_completion = 	float("{:0.2f}".format((prio_b/total_prio_b)))
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
			complete = db.session.query(MyQualification).filter(MyQualification.training_id==tid,MyQualification.userid==userid).first()
			if complete:
				return complete.percent
			else:
				return 0.0
		else:
			##get report for all trainings#
			mandatory_passed = []
			prio_a_passed = []
			prio_b_passed = []
			total_passed = []

			trainings = self.get_user_trainings(userid)
			mandatory = self.get_user_mandatories(userid)
			prio_a = self.get_user_priority_a(userid)
			prio_b = self.get_user_priority_b(userid)

			for training in trainings:
				complete = db.session.query(MyQualification).filter(MyQualification.training_id==training.tid,MyQualification.userid==userid).first()
				if complete:
					total_passed.append(complete.percent) 

					if training.priority == "A":
						prio_a_passed.append(complete.percent)
					elif training.priority == "M":
						mandatory_passed.append(complete.percent)
					elif training.priority == "B":
						prio_b_passed.append(complete.percent)

			if trainings is not None:
				total_completion = float("{:0.2f}".format((sum(total_passed)/len(trainings))))
			else:
				total_completion = -1.0	
			if 	len(mandatory) >0:
				mandatory_completion = float("{:0.2f}".format((sum(mandatory_passed)/len(mandatory))))
			else:
				mandatory_completion = -1.0
			if len(prio_a) > 0:
				prio_a_completion = float("{:0.2f}".format((sum(prio_a_passed)/len(prio_a))))
			else:
				prio_a_completion = -1.0
			if len(prio_b) > 0:
				prio_b_completion = float("{:0.2f}".format((sum(prio_b_passed)/len(prio_b))))
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

		if len(new.get_user_roles(userid)) >0 :
			for role in new.get_user_roles(userid):
				#print(role.rname)
				#print(role.trainings)
				if role.trainings:
					trs = json.loads(role.trainings)
					t_codes.extend(trs)

			#now remove duplicates from tcodes
			t_codes = [x for x in set(t_codes)]

			#get trainings by tcodes
			for x in t_codes:
				tr = self.get_training_by_t_code(x)
				if tr:
					if tr.priority != 'M':
						prio_a_trs.append(tr)

		return  prio_a_trs

	def get_user_priority_b(self,userid):
		tr = Trainings.query.filter_by(priority="B").all()
		return  tr

	def get_user_trainings(self,userid):
		
		tr = []
		for i in self.get_user_mandatories(userid):
			tr.append(i)
		if self.get_user_priority_a(userid):
			tr.extend(self.get_user_priority_a(userid))

		return  tr			

	def get_department_report(self,department_id,tid=0):
		tid = int(tid)
		users = [x for x in self.get_user() if x.department==department_id]

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
					total_passed +=	self.get_user_report(user.userid,tid)
					
			if total_tr >0:
				completion = float("{:0.2f}".format((total_passed/total_tr)))
			else:
				completion = 0.0	

			return 	completion

		for user in users:			
			trainings = self.get_user_trainings(user.userid)
			if trainings is not None:
				for training in trainings:
					reap = self.get_user_report(user.userid,training.tid)
					total_passed += reap
				
					if training.priority ==  "M":
						mandatory += reap
					elif training.priority ==  "A":
						prio_a += reap
					elif training.priority ==  "B":
						prio_b += reap	

			total_mand += len(self.get_user_mandatories(user.userid))
			total_prio_a += len(self.get_user_priority_a(user.userid))
			total_prio_b += len(self.get_user_priority_b(user.userid))	
			total_tr += len(trainings)

		t_completion = float("{:0.2f}".format((total_passed/total_tr)))
		
		if total_mand >0:
			m_completion = 	float("{:0.2f}".format((mandatory/total_mand)))
		else:
			m_completion = -1.0
		if total_prio_a >0:
			a_completion = 	float("{:0.2f}".format((prio_a/total_prio_a)))
		else:
			a_completion = -1.0
		if total_prio_b >0:
			b_completion = 	float("{:0.2f}".format((prio_b/total_prio_b)))
		else:
			b_completion = -1.0			

		return {"total":t_completion,"m":m_completion,"a":a_completion,"b":b_completion}

	def get_teams_report(self,department,team):
		result = []
		users = self.get_team_members(team,department)
		
		mandatory = 0
		prio_a = 0
		prio_b = 0
		total_passed = 0

		total_mand = 0
		total_prio_a = 0
		total_prio_b = 0
		total_tr = 0

		for user in users:			
			trainings = self.get_user_trainings(user.userid)
			if trainings is not None:
				for training in trainings:
					reap = self.get_user_report(user.userid,training.tid)
					total_passed += reap
				
					if training.priority ==  "M":
						mandatory += reap
					elif training.priority ==  "A":
						prio_a += reap
					elif training.priority ==  "B":
						prio_b += reap	

			total_mand += len(self.get_user_mandatories(user.userid))
			total_prio_a += len(self.get_user_priority_a(user.userid))
			total_prio_b += len(self.get_user_priority_b(user.userid))	
			total_tr += len(trainings)

		t_completion = float("{:0.2f}".format((total_passed/total_tr)))
		
		if total_mand >0:
			m_completion = 	float("{:0.2f}".format((mandatory/total_mand)))
		else:
			m_completion = -1.0
		if total_prio_a >0:
			a_completion = 	float("{:0.2f}".format((prio_a/total_prio_a)))
		else:
			a_completion = -1.0
		if total_prio_b >0:
			b_completion = 	float("{:0.2f}".format((prio_b/total_prio_b)))
		else:
			b_completion = -1.0			

		return {"total":t_completion,"m":m_completion,"a":a_completion,"b":b_completion}

	def expire_training(self, tid):
		"""assigns 0 score to non-suc trainings and pending to suc trainings"""
		qualz = db.session.query(MyQualification).filter(MyQualification.training_id==tid).all()
		if qualz is not None:			
			for item in qualz:				
				if item.suc_status == "na":
					db.session.query(MyQualification).filter(MyQualification.qid==item.qid).update({
						"score": 0, 'status': 'REPEAT'})
					db.session.commit()

					# log qualification percent
					self.log_qualification_percent(item.qid)
				
				else:
					db.session.query(MyQualification).filter(MyQualification.qid==item.qid)\
						.update({"suc_status": "pending", 'status': 'REPEAT'})
					
					if item.score is not None:
						db.session.query(MyQualification).filter(MyQualification.qid==item.qid)\
							.update({"score": 0})
					db.session.commit()

					# log qualification percent
					self.log_qualification_percent(item.qid)
						
		return

	def add_training(self,form,edit=0,files=None):

		#check if title already exists for another training
		
		check = db.session.query(Trainings).filter(Trainings.title==form['title'].title(),Trainings.tid != edit).count()
		if check > 0:
			return {'status':2, 'message':'This course title already exists for another course.'}

		main = "main"
		
		#document paths
		main_path = app.config["MAIN_UPLOAD_FOLDER"]
		suc_path = app.config["SUC_UPLOAD_FOLDER"]
		other_path = app.config["OTHER_UPLOAD_FOLDER"]
		main_link = None
		suc_link = None	
		other_link = []


		title = form['title']
		department = form['depart']
		owner = form['owner']
		exp = form['exp']
		#q_link = form['quiz']
		pass_mark = form['pasmk']
		priority = form['prio']
		
		#return {'status':1, 'message': 'Training was added successfully.'}

		suc = 0 
		if form['suc']:			
			suc = form['suc']

		titles = title.split()
		for x in titles:
			main += "_{}".format(x.lower())

		if files is not None:
			if 'main_obj' in files.keys() and files['main_obj'].filename:
				main_link = self.save_file(main_path,files['main_obj'],main)

			if 'other_file' in files.keys() and files['other_file'].filename:
				other_docs = files.getlist('other_file')
				for doc in other_docs:
					link = self.save_file(other_path,doc)
					other_link.append(link)

		if edit > 0:			
			#edit course now
			expire_option = form['expire_option']
			training = db.session.query(Trainings).filter(Trainings.tid == edit).first()
			if main_link is not None and main_link != training.doc_link:
				self.delete_file(training.doc_link)
			else:	
				main_link = training.doc_link

			if len(other_link) == 0:
				other_link = training.extra_resource
			else:
				if training.extra_resource and len(training.extra_resource) > 0:					
					resource = json.loads(training.extra_resource)					
					for path in resource:
						if path not in other_link:
							 other_link.append(path)
					other_link = json.dumps(other_link)
				else:
					other_link = json.dumps(other_link)	

			if files is not None and 'suc_obj' in files.keys() and files['suc_obj'].filename:
				suc_rec = StepupCards.query.filter_by(training_id=edit).first()
				if suc_rec:
					self.delete_file(suc_rec.suc_link)
					StepupCards.query.filter_by(training_id=edit).delete()
					db.session.commit()
				suc_link = self.save_file(suc_path,files['suc_obj'])
				if suc_link:
					self.log_suc_file(suc_link,edit)	

			db.session.query(Trainings).filter(Trainings.tid == edit).update({
				'title': title.title(),
				'department' : department,
				'owner' : owner,
				'expiry' : exp,
				'last_review' : datetime.now(),
				'extra_resource': other_link,
				'doc_link' : main_link,
				'pass_mark' : pass_mark,
				'priority' : priority,
				'suc': suc
				})
			db.session.commit()

			message = 'Training was updated successfully.'

			# expire qualifications here			
			if expire_option == 'yes':
				self.expire_training(edit)
				message += " Past qualifications have also been expired for all users."

			return {'status':1, 'message': message}

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
		log.doc_link = main_link #"{}{}".format(main_path,main)
		log.pass_mark = pass_mark
		log.priority = priority
		if other_link is not None:
			log.extra_resource = json.dumps(other_link)
		log.t_code = generate_tcode()
		log.suc = suc
		db.session.add(log)
		db.session.commit()

		if files is not None and 'suc_obj' in files.keys():
			suc_link = self.save_file(suc_path,files['suc_obj'])
			if suc_link is not None:
				self.log_suc_file(suc_link,log.tid)
			
		return {'status':1, 'message': 'Training was added successfully.'}

	def save_file(self,path,fileobj,fname=None):
		"""Saves a file to the given path"""
		if os.path.exists("{}{}".format(APP_ROOT,path)) and fileobj.filename:
			if fname:
				filename = "{}.{}".format(fname,secure_filename(fileobj.filename).split('.')[-1])
			else:	
				filename = secure_filename(fileobj.filename)
			fileobj.save("{}{}{}".format(APP_ROOT,path,filename))
			return os.path.join(path,filename)
		return None
	
	def update_quiz_questions(self,form,what):
		"""Updates the quiz_link attr of Trainings table"""

		training = Trainings.query.filter_by(tid = form["tid"]).first()

		data = {}
		data["attempt"] = None
		data["banner_image"] = None
		data["qualification_type"] = None
		data["questions"] = None
		
		if what == "settings":			
			if form["banner"].filename:				
				filename = ""
				title = training.title.lower().split()
				for x in title:
					filename += "{}_".format(x)
				file_path = "/static/img/images/quiz_templates/"
				data["banner_image"] = self.save_file(file_path,form["banner"],filename)
			if form["attempt"]:
				data["attempt"] = form["attempt"]
			if form["qualification_type"]:
				data["qualification_type"] = form["qualification_type"]
			if training.quiz_link is not None:
				_data = json.loads(training.quiz_link)
				data["questions"] = _data["questions"]	

		elif what == "question":
			mr = {}
			mr["question"] = form["question"] #string
			mr["question_type"] = form["question_type"] #string
			mr["options"] = form["options"] #list of strings
			mr["answer"] = form["answer"] #list of strings
			data["questions"] = []
			data["questions"].append(mr) 					

		if training.quiz_link is not None:
			quiz_data = json.loads(training.quiz_link)
			if what == "question":				
				if quiz_data["questions"] is not None and len(quiz_data["questions"]) > 0:
					quiz_data["questions"].append(mr)
				else:
					quiz_data["questions"] = []
					quiz_data["questions"].append(mr)	

			elif what == "settings":	
				quiz_data["attempt"] = data["attempt"]
				quiz_data["banner_image"] = data["banner_image"]
				quiz_data["questions"] = data["questions"]
				quiz_data["qualification_type"] = data["qualification_type"]

			Trainings.query.filter_by(tid = form["tid"]).update({"quiz_link":json.dumps(quiz_data)})
			db.session.commit()

			#temp = Trainings.query.filter_by(tid = form["tid"]).first()
			#if temp.quiz_link is not None:
				#link = json.loads(temp.quiz_link)
				#print(link["questions"])
			#else:
				#print("nothing here")	
			
		else:						 
			Trainings.query.filter_by(tid = form["tid"]).update({"quiz_link":json.dumps(data)})
			db.session.commit()
			
		return {"status":1, "message":"Updated Successsfully."}

	def delete_quiz_question(self,form):
		"""Deletes the specified question record from the question list"""

		training = Trainings.query.filter_by(tid = form["tid"]).first()

		if training.quiz_link is not None:
			quiz_data = json.loads(training.quiz_link)
			question_list = [x for x in quiz_data["questions"] if x["question"] != form["question"]] 
			quiz_data["questions"] = question_list

			Trainings.query.filter_by(tid = form["tid"]).update({"quiz_link":json.dumps(quiz_data)})
			db.session.commit()
		else:
			return {"status":2, "message":"No records found."}	

		return {"status":1, "message":"Question deleted successsfully."}

	def delete_file(self,filepath):
		"""Deletes the file specified in the filepath"""
		if os.path.exists("{}{}".format(APP_ROOT,filepath)):
			os.remove("{}{}".format(APP_ROOT,filepath))
			return True
		return False	

	def log_suc_file(self,filepath,training_id):
		"""creates a record of the uploaded suc file in the database"""
		new_entry = StepupCards()
		new_entry.training_id = training_id
		new_entry.suc_link = filepath
		db.session.add(new_entry)
		db.session.commit()
		return new_entry.sucid

	def delete_course(self, data):
		##check if there is atleast one training record for this course
		check = MyQualification.query.filter_by(training_id=data['tid']).count()

		if check > 0:

			return {'status':2, 'message': 'This course cannot be deleted, there is an existing training record for it.'}

		#check if suc is associated with course
		check = StepupCards.query.filter_by(training_id=data['tid']).count()
		if check > 0:
			for x in StepupCards.query.filter_by(training_id=data['tid']).all():
				#delete stepupcard file if exists
				if os.path.exists("{}{}".format(APP_ROOT,x.suc_link)):
					os.remove("{}{}".format(APP_ROOT,x.suc_link))
				#delete stepupcard record	
				StepupCards.query.filter_by(sucid=x.sucid).delete()
				db.session.commit()

		##delete training material if exists
		training =  db.session.query(Trainings).filter(Trainings.tid==data['tid']).first()
		if os.path.exists("{}{}".format(APP_ROOT,training.doc_link)):
			os.remove("{}{}".format(APP_ROOT,training.doc_link))
		##delete training	
		db.session.query(Trainings).filter(Trainings.tid==data['tid']).delete()
		db.session.commit()

		return {'status':1, 'message': 'Course deleted successfully.'}

	def check_for_suc(self,tid):
		get_tr = Trainings.query.filter(Trainings.tid==tid).first()
		if get_tr.suc == 2:
			stat = 'required'
		elif get_tr.suc == 1:
			stat = 'suc only'
		else:
			stat = 'not required'

		return stat

	def check_training_expiry(self,training_expiry,training_date, end_date=datetime.now()):
		result = 'expired'

		if int(training_expiry) == 0:
			return 'valid'

		if training_date is not None:
			start_date = training_date

			diffyears = end_date.year - start_date.year

			difference  = end_date - start_date.replace(end_date.year)

			days_in_year = calendar.isleap(end_date.year) and 366 or 365

			difference_in_years = diffyears + (difference.days + difference.seconds/86400.0)/days_in_year
			
			if difference_in_years <= training_expiry:
				result = 'valid'
		else:
			result = 'valid'

		return result
	
	def get_training_expiry_date(self, training_expiry, training_date):
		"""
		Returns the expiry date of a training as a string (YYYY-MM-DD).
		If the training has expired, returns 'expired'.
		"""
		end_date = datetime.now()

		# If expiry is not set or training_date is missing, treat it as non-expiring
		if int(training_expiry) == 0 or not training_date:
			return 'N/A'

		# Calculate expiry date
		expiry_date = training_date + relativedelta(years=int(training_expiry))

		# Check if it's expired
		if end_date > expiry_date:
			return 'expired'

		return expiry_date.strftime('%Y-%m-%d')
	
	def log_qualification_percent(self, qid):
		qualz = db.session.query(MyQualification).filter(MyQualification.qid==qid).first()

		if qualz is not None:
			suc_stat = self.check_for_suc(qualz.training_id)
			# get training expiry
			training = self.get_training(qualz.training_id)
			if suc_stat == "not required" :
				if qualz.status == 'PASSED' and self.check_training_expiry(training.expiry,qualz.q_date) !='expired':
					perc = 100
				else:
					perc = 0

				db.session.query(MyQualification).filter(MyQualification.qid==qid).update({'percent':perc})
				db.session.commit()
			
			elif suc_stat == 'suc only':
				if  qualz.suc_status == 'completed' and self.check_training_expiry(training.expiry,qualz.suc_q_date) !='expired':
					perc = 100
				else:
					perc = 0

				db.session.query(MyQualification).filter(MyQualification.qid==qid).update({'percent':perc})
				db.session.commit()

			else:
				#if both passed/completed, check training expiry  
				if qualz.status == 'PASSED' and qualz.suc_status == 'completed':
					perc = 0
					if  self.check_training_expiry(training.expiry,qualz.q_date) !='expired':
						perc += 50
					if  self.check_training_expiry(training.expiry,qualz.suc_q_date) !='expired':
						#print(f'{qualz.title}: {self.check_training_expiry(training.expiry,qualz.suc_q_date)}')
						perc += 50
				#if both failed/pending  
				elif qualz.status == 'REPEAT' and qualz.suc_status == 'pending':
					perc = 0
				#if one is passed while the other is not  
				else:
					perc = 0
					if qualz.status == 'PASSED' and self.check_training_expiry(training.expiry,qualz.q_date) !='expired':
						perc += 50
					elif qualz.suc_status == 'completed' and self.check_training_expiry(training.expiry,qualz.suc_q_date) !='expired':
						perc += 50

				db.session.query(MyQualification).filter(MyQualification.qid==qid).update({'percent':perc})
				db.session.commit()
		return

	def record_training_score(self,data,manual:int=0):
		"""Creates/Updates users training record automatically/manually
		   Automatically means when the user qualifies through online quiz
		   Manually means when admin updates users record manually
		"""
		f_path = None		

		get_tr = Trainings.query.filter(Trainings.tid==data['tid']).first()

		# check for score if training is not SUC ONLY
		if get_tr.suc != 1:
			if 'score' in data.keys() and data['score']:
				if int(data['score']) >= int(get_tr.pass_mark):
					status = 'PASSED'			
				else:
					status = 'REPEAT'

		##check if qualification record already exist for this user on this course#
		qualz = db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).first()

		##update data otherwise add 
		if qualz is not None:
			if manual == 1 and data['certificate'].filename:
				certificate_title = '{}_certificate'.format(get_tr.t_code)
				f_path = self.save_file(data['certificate_path'],data['certificate'],certificate_title)
				
			if 'score' in data.keys() and data['score']:
				if manual == 1:					
					db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).update({
						'score':int(data['score']),
						'q_date': datetime.now(),					
						'qualifier': data['qualifier'], 
						'logged_by': session['userid'],
						'status': status,
						'certificate_link': f_path	
						})
				else:
					db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).update({
						'score':int(data['score']),
						'q_date': datetime.now(),						
						'status': status
						})	
				db.session.commit()
			if 'suc' in data.keys() and data['suc']:
				if manual == 1:
					db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).update({
						'suc_status':data['suc'],					
						'qualifier': data['qualifier'], 
						'logged_by': session['userid'],
						'suc_q_date': datetime.now(),
						'certificate_link': f_path
						})
				else:
					db.session.query(MyQualification).filter(MyQualification.qid==data['quizid']).update({
						'suc_status':data['suc'],
						'suc_q_date': datetime.now()
					})
				db.session.commit()	
			#log qualification percent
			self.log_qualification_percent(qualz.qid)

		else:							 
			log = MyQualification()
			if manual == 1 and data['certificate'].filename:
				certificate_title = '{}_certificate'.format(get_tr.t_code)
				f_path = self.save_file(data['certificate_path'],data['certificate'],certificate_title)
				log.certificate_link = f_path
			log.training_id = get_tr.tid
			log.title = get_tr.title
			log.department = get_tr.department
				
			if 'suc' in data.keys() and data['suc']:				 
				log.suc_status = data['suc']
				log.suc_q_date = datetime.now()
			if 'score' in data.keys() and data['score']:	
				log.q_date = datetime.now()			
				log.score = int(data['score'])
				log.status = status
			if manual == 1:
				log.userid = data['userid']
				log.logged_by = session['userid']
				log.qualifier = data['qualifier']
			else:
				log.userid = session['userid']	

			db.session.add(log)
			db.session.commit()

			#log qualification percent
			self.log_qualification_percent(log.qid)

		return {'status':1, 'message': 'Weldone'}

	def fetch_trainings(self, data):
		""" This function returns the skill matrix view for user """

		get_courses = None
		fullnamme = session['fullname']
		if data['filter'] == 'report':
			usernow = data['userid']
		else:
			usernow = session['userid']

		html = '<div class="table table-responsive">'						

		if data['filter'] == 'all' or data['value'] == 'all':		
			get_courses = self.get_user_trainings(usernow)
		elif data['filter'] == 'priority':
			get_courses = []
			for i in self.get_user_trainings(usernow):
				if i.priority == data['value']:
					get_courses.append(i)
		elif data['filter'] == 'department':
			get_courses = []
			for i in self.get_user_trainings(usernow):
				if i.department == data['value']:
					get_courses.append(i)		
		elif data['filter'] == 'user':
			usernow = data['value']
			get_courses = self.get_user_trainings(usernow)
			xy = self.get_user(data['value'])
			fullnamme = "{} {}".format(xy.sname,xy.fname)

		else:		
			get_courses = self.get_user_trainings(usernow)
		#print(f'filter: {data["filter"]}, value: {data["value"]}')
				
		if get_courses:
			html += '<div class="row">'
			html += '<div class="col-md-12" style="text-align:center">Skill Matrix For: '+fullnamme+'</div>'
			html += '<di]v class="col-md-12"><hr style="border: solid 2px #179cd7;"></div>'
			html += '</div>'
			html += '<table class="table table-bordered table-striped">'
			html += '<thead><tr>'
			html += '<th scope="col">Code</th>'
			html += '<th scope="col">Date</th>'
			html += '<th scope="col">Skill Title</th>'
			html += '<th scope="col">Dept</th>'
			html += '<th scope="col">Priority</th>'
			html += '<th scope="col">Owner</th>'
			html += '<th scope="col">Outline</th>'
			html += '<th scope="col">Quiz</th>'
			html += '<th scope="col">Completion (%)</th>'
			#html += '<th scope="col">Certificate</th>'
			html += '</tr></thead>'
			html += '<tbody>'

			count = 1

			if data['value'] != "complete" and data['value'] != "not-complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==usernow,MyQualification.training_id==course.tid).first()

					main = 'tr'
					titles = course.title.split()
					for x in titles:
						main += "_{}".format(x.lower())

					html += '<tr>'
					html += '<td><span style="color:#179cd7">'+course.t_code+'</span></td>'
					if get_data:
						html += '<td>'
						if get_data.q_date:
							html += '<span style="color:#179cd7; font-size:9px">'+get_data.q_date.strftime("%Y-%m-%d")+'</span>'
						# check if suc is required for the course and that it has been done
						if self.check_for_suc(course.tid) !='not required' and get_data.suc_q_date:
							html += '<br><span style="color:#179cd7; font-size:9px">suc- '+get_data.suc_q_date.strftime("%Y-%m-%d")+'</span>'
						html += '</td>'
					else:
						html += '<td></td>'
					html += '<td>'+course.title+'</td>'
					html += '<td>'+course.department+'</td>'
					html += '<td>'+course.priority+'</td>'
					html += '<td>'+self.get_course_owner(course.owner)+'</td>'
					html += '<td>'

					if self.check_file(course.doc_link):
						html += '<span><a style="font-size:12px" href="'+course.doc_link+'" target="_blank">course outline</a></span><br>'
					if course.suc and StepupCards.query.filter_by(training_id=course.tid).first():
						suc_rec = StepupCards.query.filter_by(training_id=course.tid).first()
						html += '<span><a style="font-size:12px" href="'+suc_rec.suc_link+'" target="_blank">Stepup card</a></span><br>'	
					if course.extra_resource and len(course.extra_resource) > 0:
						resource = json.loads(course.extra_resource)
						for link in resource:							
							if self.check_file(link):
								filename = link.split('/')[-1]
								filename = filename[:-10] if len(filename)<=10 else "{}...".format(filename[:-10])
								html += '<span><a style="font-size:11px" href="'+link+'" target="_blank">'+filename+'</a></span><br>'						
					html += '</td>'
					if get_data :						
						quizlink = "/templates/e_learning/{}.html".format(main)													
						if self.check_file(quizlink):
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						elif course.suc !=1:							
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						else:
							html +='<td></td>'
						html += '<td>'		
						if get_data.percent == 100:
							html += '<span style="color:green">'+str(get_data.percent)+'</span><br>'
						else:
							html += '<span style="color:red">'+str(get_data.percent)+'</span><br>'						
						if self.check_file(get_data.certificate_link) and self.check_for_suc(course.tid) !='not required':
							html += '<span><a style="font-size:12px" href="'+get_data.certificate_link+'" target="_blank">certificate</a></span>'
						html +='</td>'

					else:
						quizlink = "/templates/e_learning/{}.html".format(main)
						if self.check_file(quizlink):
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						elif course.suc !=1:
							#html +='<td></td>'
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						else:
							html +='<td></td>'
						html += '<td><span style="color:#000">0</span></td>'						
					count += 1
					html += '</tr>'

			elif data['value'] == "complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					#if get_data and get_data.score >= course.pass_mark:
					if get_data and get_data.percent == 100:	
						main = 'tr'
						titles = course.title.split()
						for x in titles:
							main += "_{}".format(x.lower())

						html += '<tr>'
						#html += '<td>'+str(count)+'</td>'						
						html += '<td><span style="color:#179cd7">'+course.t_code+'</span></td>'
						if get_data:
							html += '<td>'
							if get_data.q_date:
								html += '<span style="color:#179cd7; font-size:9px">'+get_data.q_date.strftime("%Y-%m-%d")+'</span>'
							if self.check_for_suc(course.tid) !='not required' and get_data.suc_q_date:
								html += '<br><span style="color:#179cd7; font-size:9px">suc- '+get_data.suc_q_date.strftime("%Y-%m-%d")+'</span>'
							html += '</td>'
						else:
							html += '<td></td>'
						html += '<td>'+course.title+'</td>'
						html += '<td>'+course.department+'</td>'
						html += '<td>'+course.priority+'</td>'
						html += '<td>'+self.get_course_owner(course.owner)+'</td>'
						html += '<td>'

						if self.check_file(course.doc_link):
							html += '<span><a style="font-size:12px" href="'+course.doc_link+'" target="_blank">course outline</a></span><br>'
						if course.suc and StepupCards.query.filter_by(training_id=course.tid).first():
							suc_rec = StepupCards.query.filter_by(training_id=course.tid).first()
							html += '<span><a style="font-size:12px" href="'+suc_rec.suc_link+'" target="_blank">Stepup card</a></span><br>'	
						if course.extra_resource and len(course.extra_resource) > 0:
							resource = json.loads(course.extra_resource)
							for link in resource:							
								if self.check_file(link):
									filename = link.split('/')[-1]
									filename = filename[:-10] if len(filename)<=10 else "{}...".format(filename[:-10])
									html += '<span><a style="font-size:11px" href="'+link+'" target="_blank">'+filename+'</a></span><br>'						
						html += '</td>'
						if get_data :
							quizlink = "/templates/e_learning/{}.html".format(main)
							if self.check_file(quizlink):
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							elif course.suc !=1:								
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							else:
								html +='<td></td>'
							html += '<td>'		
							if get_data.percent == 100:
								html += '<span style="color:green">'+str(get_data.percent)+'</span><br>'
							else:
								html += '<span style="color:red">'+str(get_data.percent)+'</span><br>'
							if self.check_file(get_data.certificate_link) and self.check_for_suc(course.tid) !='not required':
								html += '<span><a style="font-size:12px" href="'+get_data.certificate_link+'" target="_blank">certificate</a></span>'
							html +='</td>'	
						else:
							quizlink = "/templates/e_learning/{}.html".format(main)
							if self.check_file(quizlink):
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							elif course.suc !=1:								
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							else:
								html +='<td></td>'	
							html += '<td><span style="color:#000">0</span></td>'
							
						count += 1
						html += '</tr>'

			elif data['value'] == "not-complete":
				for course in get_courses:
					bash = db.session.query(MyQualification).all()
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==session['userid'],MyQualification.training_id==course.tid).first()

					#if get_data is None or get_data.score < course.pass_mark:
					if get_data is None or get_data.percent < 100:	
						main = 'tr'
						titles = course.title.split()
						for x in titles:
							main += "_{}".format(x.lower())

						html += '<tr>'
						# html += '<td>'+str(count)+'</td>'						
						html += '<td><span style="color:#179cd7">'+course.t_code+'</span></td>'
						if get_data:
							html += '<td>'
							if get_data.q_date:
								html += '<span style="color:#179cd7; font-size:9px">'+get_data.q_date.strftime("%Y-%m-%d")+'</span>'
							if self.check_for_suc(course.tid) !='not required' and get_data.suc_q_date:
								html += '<br><span style="color:#179cd7; font-size:9px">suc- '+get_data.suc_q_date.strftime("%Y-%m-%d")+'</span>'
							html += '</td>'
						else:
							html += '<td></td>'
						html += '<td>'+course.title+'</td>'
						html += '<td>'+course.department+'</td>'
						html += '<td>'+course.priority+'</td>'
						html += '<td>'+self.get_course_owner(course.owner)+'</td>'
						html += '<td>'

						if self.check_file(course.doc_link):
							html += '<span><a style="font-size:12px" href="'+course.doc_link+'" target="_blank">course outline</a></span><br>'
						if course.suc and StepupCards.query.filter_by(training_id=course.tid).first():
							suc_rec = StepupCards.query.filter_by(training_id=course.tid).first()
							html += '<span><a style="font-size:12px" href="'+suc_rec.suc_link+'" target="_blank">Stepup card</a></span><br>'
						if course.extra_resource and len(course.extra_resource) > 0:
							resource = json.loads(course.extra_resource)
							for link in resource:							
								if self.check_file(link):
									filename = link.split('/')[-1]
									filename = filename[:-10] if len(filename)<=10 else "{}...".format(filename[:-10])
									html += '<span><a style="font-size:11px" href="'+link+'" target="_blank">'+filename+'</a></span><br>'						
						html += '</td>'
						if get_data :
							quizlink = "/templates/e_learning/{}.html".format(main)
							if self.check_file(quizlink):
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							elif course.suc !=1:								
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							else: 
								html +='<td></td>'
							html += '<td>'		
							if get_data.percent == 100:
								html += '<span style="color:green">'+str(get_data.percent)+'</span><br>'
							else:
								html += '<span style="color:red">'+str(get_data.percent)+'</span><br>'
							if self.check_file(get_data.certificate_link) and self.check_for_suc(course.tid) !='not required':
								html += '<span><a style="font-size:12px" href="'+get_data.certificate_link+'" target="_blank">certificate</a></span>'
							html +='</td>'	
						else:
							quizlink = "/templates/e_learning/{}.html".format(main)
							if self.check_file(quizlink):
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							elif course.suc !=1:								
								html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
							else:
								html +='<td></td>'	
							html += '<td><span style="color:#000">0</span></td>'
							
						count += 1
						html += '</tr>'


			html += '</tbody>'
			html += '</table>'

		
		else:
			html += "<div class='alert alert-danger'>No results found for your selection.</div>"
		html += '</div>'

		##fetch percentage completion data#
		total = self.fetch_total_training_percent(get_courses, usernow)
		mandatory = self.fetch_mandatory_training_percent(get_courses,usernow)
		prio_a = self.fetch_priority_a_training_percent(get_courses,usernow)
		prio_b = self.fetch_priority_b_training_percent(get_courses,usernow)

		return {'status':1, 'data': html,'all':total, 'man':mandatory, 'pa':prio_a, 'pb':prio_b}
	
	def fetch_expiring_trainings(self, data):
		""" This function returns trainings that are expiring/expired based on filters """
		
		# Get filter parameters
		time_period = data.get('time_period', '30')
		department = data.get('department', 'all')
		priority = data.get('priority', 'all')
		filter_type = data.get('filter')
		
		# Determine target date
		target_date = datetime.now()
		if time_period != 'expired':
			target_date += timedelta(days=int(time_period))

		# Determine user
		usernow = data.get('userid') if filter_type == 'report' else session.get('userid')

		# Filter trainings
		get_courses = [
			training for training in self.get_user_trainings(usernow)
			if (priority == 'all' or training.priority == priority) and
			(department == 'all' or training.department == department)
		]
		
		html = '<div class="table table-responsive">'
		if get_courses:
			html += '<table class="table table-bordered table-striped">'
			html += '<thead><tr>'
			html += '<th scope="col">Code</th>'
			html += '<th scope="col">Last Qualified</th>'
			html += '<th scope="col">To Expire</th>'
			html += '<th scope="col">Skill Title</th>'
			html += '<th scope="col">Dept</th>'
			html += '<th scope="col">Priority</th>'
			html += '<th scope="col">Owner</th>'
			html += '<th scope="col">Outline</th>'
			html += '<th scope="col">Quiz</th>'
			html += '<th scope="col">Completion (%)</th>'
			#html += '<th scope="col">Certificate</th>'
			html += '</tr></thead>'
			html += '<tbody>'

			count = 1
			counter = 0

			for course in get_courses:
				get_data = db.session.query(MyQualification).filter(MyQualification.userid==usernow,MyQualification.training_id==course.tid).first()
				

				# Filter courses that will expire within time_period
				if not get_data or self.check_training_expiry(course.expiry, get_data.q_date, target_date) == 'expired' or (course.suc and self.check_training_expiry(course.expiry, get_data.suc_q_date, target_date) == 'expired'):
					# if not get_data:
					# 	print(f'{course.title}')
					counter += 1
					main = 'tr'
					titles = course.title.split()
					for x in titles:
						main += "_{}".format(x.lower())

					html += '<tr>'
					html += '<td><span style="color:#179cd7">'+course.t_code+'</span></td>'

					if get_data:
						q_date = ''
						exp_date = ''
						if get_data.q_date:
							q_date += '<span style="color:#179cd7; font-size:10px">'+get_data.q_date.strftime("%Y-%m-%d")+'</span>'
							if self.check_training_expiry(course.expiry, get_data.q_date, target_date) == 'expired':
								exp_date += '<span style="color:#179cd7; font-size:10px">'+ self.get_training_expiry_date(course.expiry, get_data.q_date) +'</span>'
						# check if suc is required for the course and that it has been done
						if self.check_for_suc(course.tid) !='not required' and get_data.suc_q_date:
							q_date += '<br><span style="color:#179cd7; font-size:10px">suc- '+get_data.suc_q_date.strftime("%Y-%m-%d")+'</span>'
							if self.check_training_expiry(course.expiry, get_data.suc_q_date, target_date) == 'expired':
								exp_date += '<br><span style="color:#179cd7; font-size:10px">suc- '+ self.get_training_expiry_date(course.expiry, get_data.suc_q_date) +'</span>'
						
						# html += '<td>' + self.get_training_expiry_date(course.expiry, get_data.q_date) +'</td>'
					else:
						q_date = '<span style="color:#179cd7; font-size:10px">never qualified</span>'
						exp_date = '<span style="color:#179cd7; font-size:10px">never qualified</span>'
					
					html += '<td>' + q_date + '</td>'
					html += '<td>' + exp_date + '</td>'
					html += '<td>'+course.title+'</td>'
					html += '<td>'+course.department+'</td>'
					html += '<td>'+course.priority+'</td>'
					html += '<td>'+self.get_course_owner(course.owner)+'</td>'
					html += '<td>'

					if self.check_file(course.doc_link):
						html += '<span><a style="font-size:12px" href="'+course.doc_link+'" target="_blank">course outline</a></span><br>'
					if course.suc and StepupCards.query.filter_by(training_id=course.tid).first():
						suc_rec = StepupCards.query.filter_by(training_id=course.tid).first()
						html += '<span><a style="font-size:12px" href="'+suc_rec.suc_link+'" target="_blank">Stepup card</a></span><br>'	
					if course.extra_resource and len(course.extra_resource) > 0:
						resource = json.loads(course.extra_resource)
						for link in resource:							
							if self.check_file(link):
								filename = link.split('/')[-1]
								filename = filename[:-10] if len(filename)<=10 else "{}...".format(filename[:-10])
								html += '<span><a style="font-size:11px" href="'+link+'" target="_blank">'+filename+'</a></span><br>'						
					html += '</td>'
					if get_data :						
						quizlink = "/templates/e_learning/{}.html".format(main)													
						if self.check_file(quizlink):
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						elif course.suc !=1:							
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(get_data.qid)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						else:
							html +='<td></td>'
						html += '<td>'		
						if get_data.percent == 100:
							html += '<span style="color:green">'+str(get_data.percent)+'</span><br>'
						else:
							html += '<span style="color:red">'+str(get_data.percent)+'</span><br>'						
						if self.check_file(get_data.certificate_link) and self.check_for_suc(course.tid) !='not required':
							html += '<span><a style="font-size:12px" href="'+get_data.certificate_link+'" target="_blank">certificate</a></span>'
						html +='</td>'

					else:
						quizlink = "/templates/e_learning/{}.html".format(main)
						if self.check_file(quizlink):
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/'+main+'.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						elif course.suc !=1:
							#html +='<td></td>'
							html += '<td><a href="/e_learning?action=GET-QUIZ&template=e_learning/tr_default.html&id='+str(0)+'&pass='+str(course.pass_mark)+'&tid='+str(course.tid)+'" target="_blank">qualify</a></td>'
						else:
							html +='<td></td>'
						html += '<td><span style="color:#000">0</span></td>'						
					count += 1
					html += '</tr>'

			html += '</tbody>'
			html += '</table>'

		
		else:
			html += "<div class='alert alert-danger'>No results found for your selection.</div>"
		html += '</div>'

		
		return {
			'status': 1,
			'html': html,
			'count': counter
		}
	
	def fetch_user_expiring_trainings_data(self, data:dict, user_id:int) -> list:
		"""This method returns an object of a user with a list of their expiring trainings within the selected time period"""
		result = []
		
		# Get filter parameters
		time_period = data.get('time_period', '30')
		department = data.get('department', 'all')
		priority = data.get('priority', 'all')
		filter_type = data.get('filter')
		
		# Determine target date
		target_date = datetime.now()
		if time_period != 'expired':
			target_date += timedelta(days=int(time_period))

		# Filter trainings
		get_courses = [
			training for training in self.get_user_trainings(user_id)
			if (priority == 'all' or training.priority == priority) and
			(department == 'all' or training.department == department)
		]

		if get_courses:
			for course in get_courses:
				get_data = db.session.query(MyQualification).filter(MyQualification.userid==user_id,MyQualification.training_id==course.tid).first()

				# Filter courses that will expire within time_period
				if not get_data or self.check_training_expiry(course.expiry, get_data.q_date, target_date) == 'expired' or (course.suc and self.check_training_expiry(course.expiry, get_data.suc_q_date, target_date) == 'expired'):
					mr = {}
					mr['title'] = course.title
					mr['expiry_date'] = ''

					if get_data:
						if get_data.q_date:
							if self.check_training_expiry(course.expiry, get_data.q_date, target_date) == 'expired':
								mr['expiry_date'] += self.get_training_expiry_date(course.expiry, get_data.q_date)
						# check if suc is required for the course and that it has been done
						if self.check_for_suc(course.tid) !='not required' and get_data.suc_q_date:
							if self.check_training_expiry(course.expiry, get_data.suc_q_date, target_date) == 'expired':
								mr['expiry_date'] += f'{"" if mr["expiry_date"]== "" else ", "}suc - {self.get_training_expiry_date(course.expiry, get_data.suc_q_date)}'
					else:
						mr['expiry_date'] = 'never qualified'
					
					result.append(mr)
					
		return result


	def fetch_expiring_trainings_report(self, data):
		"""This function runs a report of trainings that will expire within a selected time period"""
		export_data = []
		emails = []
		html = '''
		<div class="table-responsive">
			<table class="table table-bordered table-striped">
				<thead>
					<tr>
						<th>S/N</th>
						<th>Employee Name</th>
						<th>Expiring Trainings</th>
					</tr>
				</thead>
				<tbody>
		'''
		counter = 0

		if data.get('user', 'all') == 'all':
			users = self.get_user()
			for user in users:
				expiring_training_data = self.fetch_user_expiring_trainings_data(data, user.userid)
				if expiring_training_data:
					emails.append(user.email)
					mr = {}
					mr['user'] = f'{user.fname} {user.sname}'
					mr['trainings'] = []
					counter += 1
					html += f'''
					<tr>
					<td>{counter}</td>
					<td>{user.fname} {user.sname}</td>
					<td>
					'''
					for tr in expiring_training_data:
						mr['trainings'].append(f'{tr["title"]}-({tr["expiry_date"]});')
						html += f'<span style="color:#179cd7; font-size:10px">{tr["title"]}-({tr["expiry_date"]});</span>'
					
					html += f"</td></tr>"
					export_data.append(mr)
		else:
			user = self.get_user(data.get('user'))
			expiring_training_data = self.fetch_user_expiring_trainings_data(data, user.userid)
			if expiring_training_data:
				emails.append(user.email)
				mr = {}
				mr['user'] = f'{user.fname} {user.sname}'
				mr['trainings'] = []
				html += f'''
				<tr>
				<td>1</td>
				<td>{user.fname} {user.sname}</td>
				<td>
				'''
				for tr in expiring_training_data:
					mr['trainings'].append(f'{tr["title"]}-({tr["expiry_date"]});')
					counter += 1
					html += f'<span style="color:#179cd7; font-size:10px">{tr["title"]}-({tr["expiry_date"]});</span>'
				
				html += f"</td></tr>"
				export_data.append(mr)

		return {
			'status': 1,
			'emails': emails if emails else None,
			'export_data': export_data if export_data else None,
			'html': html,
			'count': counter
		}
	
	def run_expiry_report(self,userid=0):
		"""This function checks if training records for selected user scope has expired and then updates the database"""
		if userid == 0:
			qualifications = MyQualification.query.all()
		else:
			qualifications = MyQualification.query.filter_by(userid=userid).all()

		for course in qualifications:
			tr = Trainings.query.filter_by(tid=course.training_id).first()
			if self.check_for_suc(tr.tid) == 'not required':
				if self.check_training_expiry(tr.expiry,course.q_date) == 'expired':
					self.log_qualification_percent(course.qid)
			elif self.check_for_suc(tr.tid) == 'suc only':
				if self.check_training_expiry(tr.expiry,course.suc_q_date) == 'expired':
					self.log_qualification_percent(course.qid)
			else:
				# questionair plus suc
				if self.check_training_expiry(tr.expiry,course.q_date) == 'expired':
					self.log_qualification_percent(course.qid)
				if self.check_training_expiry(tr.expiry,course.suc_q_date) == 'expired':
					self.log_qualification_percent(course.qid)
		return

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
		"""Checks if a file exists"""
		mylink = "{}{}".format(APP_ROOT,link)

		if os.path.exists(mylink) :
			return True
		return False

	def fetch_total_training_percent(self, query,userid=0):
		if userid == 0:
			userid = session['userid']

		passed = []

		if query and len(query) >0:
			for course in query:
				get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()

				if get_data:
					passed.append(get_data.percent)

			passed = sum(passed)
			total = len(query)
			percent = (passed/total)
			percent = "{:0.2f}%".format(percent)

		else:
			percent = "{}".format('N/A')



		return percent

	def fetch_mandatory_training_percent(self, query,userid=0):
		if userid == 0:
			userid = session['userid']

		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'M':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()

					if get_data:
						passed.append(get_data.percent)

			if len(man) > 0:
				passed = sum(passed)
				total = len(man)
				percent = (passed/total)
				percent = "{:0.2f}%".format(percent)
			else:
				percent = 0

		else:
			percent = "{}".format('N/A')



		return percent

	def fetch_priority_a_training_percent(self, query,userid=0):
		if userid == 0:
			userid = session['userid']

		percent = "{}".format('N/A')
		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'A':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()

					if get_data:
						passed.append(get_data.percent)

			if len(man) > 0:
				passed = sum(passed)
				total = len(man)
				percent = (passed/total)
				percent = "{:0.2f}%".format(percent)


		return percent

	def fetch_priority_b_training_percent(self, query, userid=0):
		if userid == 0:
			userid = session['userid']

		percent = "{}".format('N/A')
		passed = []
		man = []

		if query and len(query) >0:
			for course in query:
				if course.priority == 'B':
					man.append(1)

					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()

					if get_data:
						if get_data.score >= course.pass_mark:
							passed.append(1)

			if len(man) > 0:
				passed = sum(passed)
				total = len(man)
				percent = (passed/total)
				percent = "{:0.2f}%".format(percent)

		return percent
	

class MYSCHOOL_REPORT():
	def __init__(self):
		pass

	def fetch_individual_trainings(self,data):
		new = MYSCHOOL()

		results = []

		userid = data['userid']
		get_courses = None

		if data['filter'] == 'all':		
			get_courses = new.get_user_trainings(userid)
		elif data['filter'] == 'priority':
			get_courses = []
			for i in new.get_user_trainings(userid):
				if i.priority == data['value']:
					get_courses.append(i)
		elif data['filter'] == 'department':
			get_courses = []
			for i in new.get_user_trainings(userid):
				if i.department == data['value']:
					get_courses.append(i)
		else:		
			get_courses = new.get_user_trainings(userid)

		if data['value'] != "complete" and data['value'] != "not-complete":
			if get_courses is not None:
				count = 0
				for course in get_courses:
					count += 1
					mr = {}
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()
					mr['count'] = count
					mr['code'] = course.t_code
					#mr['date'] = course.title
					mr['title'] = course.title
					mr['department'] = course.department
					owner = new.get_user(course.owner)
					mr['owner'] = "{} {}".format(owner.sname,owner.fname)
					mr['priority'] = course.priority
					if get_data:
						mr['date'] = get_data.q_date.strftime("%Y-%m-%d")
						mr['completion'] = get_data.percent
					else:
						mr['date'] = ''
						mr['completion'] = 0

					results.append(mr)

		elif data['value'] == "complete":
			if get_courses is not None:
				count = 0
				for course in get_courses:
					count += 1
					mr = {}
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()
					
					if get_data and get_data.percent == 100:						
						mr['count'] = count
						mr['code'] = course.t_code						
						mr['title'] = course.title
						mr['department'] = course.department
						owner = new.get_user(course.owner)
						mr['owner'] = "{} {}".format(owner.sname,owner.fname)
						mr['priority'] = course.priority						
						mr['date'] = get_data.q_date.strftime("%Y-%m-%d")
						mr['completion'] = get_data.percent						

						results.append(mr)

		elif data['value'] == "not-complete":
			if get_courses is not None:
				count = 0
				for course in get_courses:
					count += 1
					mr = {}
					get_data = db.session.query(MyQualification).filter(MyQualification.userid==userid,MyQualification.training_id==course.tid).first()
					
					if get_data is None or get_data.percent < 100:						
						mr['count'] = count
						mr['code'] = course.t_code						
						mr['title'] = course.title
						mr['department'] = course.department
						owner = new.get_user(course.owner)
						mr['owner'] = "{} {}".format(owner.sname,owner.fname)
						mr['priority'] = course.priority						
						if get_data:
							mr['date'] = get_data.q_date.strftime("%Y-%m-%d")
							mr['completion'] = get_data.percent
						else:
							mr['date'] = ''
							mr['completion'] = 0						

						results.append(mr)
		
		total = new.fetch_total_training_percent(get_courses, userid)
		mandatory = new.fetch_mandatory_training_percent(get_courses,userid)
		prio_a = new.fetch_priority_a_training_percent(get_courses,userid)
		prio_b = new.fetch_priority_b_training_percent(get_courses,userid)

		return {'status':1,'data':results,'T':total,'M':mandatory,'A':prio_a}

	def fetch_department_users_report(self,department):
		new = MYSCHOOL()
		result = []
		users = new.get_department_users(department)
		count = 1
		if len(users) > 0:
			for user in users:
				mr = {}
				report = new.get_user_report(user.userid)
				mr['count'] = count
				mr['userid'] = user.userid
				mr['name'] = "{} {}".format(user.sname,user.fname)
				mr['total'] = report['total'] if report['total'] >= 0 else 'Nil'
				mr['m'] = report['m'] if report['m'] >= 0 else 'Nil'
				mr['a'] = report['a'] if report['a'] >= 0 else 'Nil'
				result.append(mr)
				count += 1

		#total records for department
		info = new.get_department_report(int(department))
		t = info['total'] if info['total'] > 0 else 'Nil'
		m = info['m'] if info['m'] > 0 else 'Nil'
		a = info['a'] if info['a'] > 0 else 'Nil'

		return {'status':1,'data':result,'T':t,'A':a,'M':m}

	def fetch_team_members_report(self,team,department):
		new = MYSCHOOL()
		result = []
		users = new.get_team_members(team,department)
		count = 0
		if len(users) >0 :
			for user in users:
				report = new.get_user_report(user.userid)
				count += 1
				mr = {}
				mr['count'] = count
				mr['name'] = "{} {}".format(user.sname,user.fname)
				mr['userid'] = user.userid
				mr['T'] = report['total'] if report['total'] >=0 else 'Nil'
				mr['A'] = report['a'] if report['a'] >=0 else 'Nil'
				mr['M'] = report['m'] if report['m'] >=0 else 'Nil'
				result.append(mr)

		return {'status':1,'data':result}