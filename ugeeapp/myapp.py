from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,Production,StepupCards,UserRoles,MaterialLoss,SKU,ProcessParams,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,SAFETY_BOS,QA_BOS,OGC_BOS
from ugeeapp.forms import LoginForm,PSGProductionReportForm,UTILITY_SAFETYBOSForm,LAB_QABOSForm,LAB_SAFETYBOSForm,AddRoles,PSGProductionEntryForm,WHSE_RPMBOSForm,ViewPSGResultForm,PSGProductionForm,SKUEntryForm,EquipmentEntryForm,EditUserForm,ChangePasswordForm,StopsForm,AddUserForm,forgotPasswordForm,OGCBOSForm,QABOSForm,SAFETYBOSForm,ViewBOSForm,LeadershipBOSForm,MSG_OGCBOSForm,MSG_QABOSForm,MSG_SAFETYBOSForm,WHSE_QABOSForm,WHSE_SAFETYBOSForm
from ugeeapp.models import Trainings,MyQualification
import pycomm3
import os
import time 
import json
import datetime
from datetime import datetime,timedelta
from threading import Thread
import threading
from pycomm3 import LogixDriver
from pylogix import PLC
from flask_migrate import Migrate
from ugeeapp import app,db,APP_ROOT,CERTIFICATE_FOLDER
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from ugeeapp.appclasses.userclass import USERACCOUNT
from ugeeapp.appclasses.bosclass import BOSCLASS
from ugeeapp.appclasses.production import PRODUCTION
from ugeeapp.appclasses.stopsclass import STOPSEVENT
from ugeeapp.appclasses.adminclass import AdminRoles
from ugeeapp.appclasses.globalclass import GLOBALCLASS
from ugeeapp.appclasses.elearning import MYSCHOOL,MYSCHOOL_REPORT
from ugeeapp.helpers import myfunctions as myfunc
import cgi, os
import cgitb; cgitb.enable()





PLC_4A=["143.28.88.6","143.28.88.3"]
PLC_4B=["143.28.88.12","143.28.88.14"]
PLC_L1=["143.28.88.67"]
PLC_L2=["143.28.88.67"]
ctrl_rm='143.28.88.40'

def insert_stop():
	#event1=
	return



def get_uptime(sid,start_time,machine):
	
	stop=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.end_time<=start_time).order_by(StopEvent.start_time.desc()).first()
	stop_time=str(stop.end_time)
	s=datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S.%f")
	up_time=start_time-s

	return up_time

def format_datetime(tyme):
	end=datetime.strptime(str(tyme), "%Y-%m-%d %H:%M:%S.%f")
	#t=str(end.year)+"/"+str(end.month)+"/"+str(end.day)+" "+str(end.hour)+":"+str(end.minute)+":"+str(end.second)
	t={}
	t['date']=str(end.year)[-2:]+"/"+str(end.month)+"/"+str(end.day)
	t['time']=str(end.hour)+":"+str(end.minute)+":"+str(end.second)
	return t

def format_datetime_prime(time):
	end=datetime.strptime(str(time), "%Y-%m-%d, %H:%M:%S.%f")	
	k=str(end.year)+"-"+str(end.month)+"-"+str(end.day)+" "+str(end.hour)+":"+str(end.minute)+":"+str(end.second)+".000001"
	kt=datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S.%f")
	t=datetime.strftime(kt, "%Y-%m-%d %H:%M:%S.%f")
	
	#t={}
	#t['date']=str(end.year)+"/"+str(end.month)+"/"+str(end.day)
	#t['time']=str(end.hour)+":"+str(end.minute)+":"+str(end.second)+"."+str(0) 
	return t	

def insertstop(machine,startTime,endTime,data):
	#get all the stops whose end_time are beyond the start_time of the new stop and and whose start_time are below the end_time of new stop	
	event1=db.session.query(StopEvent).filter(StopEvent.machine==machine,(StopEvent.end_time>startTime) | (StopEvent.end_time==None),StopEvent.start_time<endTime ).order_by(StopEvent.start_time.desc())
	
	#delete some stopevents 
	mylist=[]
	if event1.count()>0:
		for x in event1:
			if x.status !=0:
				p=datetime.strptime(str(x.start_time), "%Y-%m-%d %H:%M:%S.%f")
				q=datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S.%f")
				m=datetime.strptime(str(x.end_time), "%Y-%m-%d %H:%M:%S.%f")
				n=datetime.strptime(str(endTime), "%Y-%m-%d %H:%M:%S.%f")

				#delete all stop events on the machine whose starttime and endtime are within that of the new stop
				if p>q and m<n:
					mylist.append(x)
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).delete()
					db.session.commit()
				elif p==q and m<n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).delete()
					db.session.commit()
				elif p>q and m==n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).delete()
					db.session.commit()
				elif p==q and m>n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({'start_time':n})
					db.session.commit()
				elif p>q and m>n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({'start_time':n})
					db.session.commit()
				elif p<q and m<=n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({'end_time':q})
					db.session.commit()	
				elif p<q and m>n:
					#this order of event is very important. Do not change the sequence
					#create new event
					#avoid saving uptime or downtime values so that their values will remain dynamic with changes in the stopevents table
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=q
					log.end_time=n
					log.error=data['error']
					log.reason_level_one=data['r1']
					log.reason_level_two=data['r2']
					log.reason_level_three=data['r3']
					log.reason_level_four=data['r4']
					log.breakdown=int(data['r5'])
					log.comment=data['comment']
					log.status=1
					db.session.add(log)
					

					#create a third event from the remaining time of the old event
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=n
					log.end_time=x.end_time
					log.error=x.error					
					log.status=1
					db.session.add(log)
					

					#update old event
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({'end_time':q})
					db.session.commit()
					return
				elif p==q and m==n:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({
						'machine':data['machine'],
						'start_time':q,
						'end_time':n,
						'error':data['error'],
						'reason_level_one':data['r1'],
						'reason_level_two':data['r2'],
						'reason_level_three':data['r3'],
						'reason_level_four':data['r4'],
						'breakdown':int(data['r5']),
						'comment':data['comment'],
						'status':1})
					db.session.commit()
					return
				

			elif x.status==0:
				p=datetime.strptime(str(x.start_time), "%Y-%m-%d %H:%M:%S.%f")
				q=datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S.%f")			
				n=datetime.strptime(str(endTime), "%Y-%m-%d %H:%M:%S.%f")

				if p==q:
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({						
						'end_time':n,
						'error':data['error'],
						'reason_level_one':data['r1'],
						'reason_level_two':data['r2'],
						'reason_level_three':data['r3'],
						'reason_level_four':data['r4'],
						'breakdown':int(data['r5']),
						'comment':data['comment'],
						'status':1})
					db.session.commit()	

					#create new event
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=n				
					log.error=data['error']				
					db.session.add(log)
					db.session.commit()
					return

				elif p<q:
					#this order of event is very important. Do not change the sequence
					#create new event
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=q
					log.end_time=n
					log.error=data['error']
					log.reason_level_one=data['r1']
					log.reason_level_two=data['r2']
					log.reason_level_three=data['r3']
					log.reason_level_four=data['r4']
					log.breakdown=int(data['r5'])
					log.comment=data['comment']
					log.status=1
					db.session.add(log)
					

					#create new event again
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=n				
					log.error=data['error']				
					db.session.add(log)

					#update old event
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({						
						'end_time':q,						
						'status':1})
					db.session.commit()
					return

				elif p>q and p<n:
					#update the old stop
					db.session.query(StopEvent).filter(StopEvent.sid==x.sid).update({'start_time':n})
					db.session.commit()

					#create a new stop
					log=StopEvent()
					log.machine=data['machine']
					log.start_time=q
					log.end_time=n
					log.error=data['error']
					log.reason_level_one=data['r1']
					log.reason_level_two=data['r2']
					log.reason_level_three=data['r3']
					log.reason_level_four=data['r4']
					log.breakdown=int(data['r5'])
					log.comment=data['comment']
					log.status=1
					db.session.add(log)
					db.session.commit()
					return			
						

	else:
		log=StopEvent()
		log.machine=data['machine']
		log.start_time=datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S.%f")
		log.end_time=datetime.strptime(str(endTime), "%Y-%m-%d %H:%M:%S.%f")
		log.error=data['error']
		log.reason_level_one=data['r1']
		log.reason_level_two=data['r2']
		log.reason_level_three=data['r3']
		log.reason_level_four=data['r4']
		log.breakdown=int(data['r5'])
		log.comment=data['comment']
		log.status=1
		db.session.add(log)
		db.session.commit()
		return			

	#create event after fulfilling all the conditions above	
	log=StopEvent()
	log.machine=data['machine']
	log.start_time=datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S.%f")
	log.end_time=datetime.strptime(str(endTime), "%Y-%m-%d %H:%M:%S.%f")
	log.error=data['error']
	log.reason_level_one=data['r1']
	log.reason_level_two=data['r2']
	log.reason_level_three=data['r3']
	log.reason_level_four=data['r4']
	log.breakdown=data['r5']
	log.comment=data['comment']
	log.status=1
	db.session.add(log)
	db.session.commit()	
	return

def get_error(code):
	if code is not None:
		code=int(code)
	else:
		code=0	
	causes=db.session.query(StopCode).filter(StopCode.cause_code==code).first()
	if causes is not None:
		return causes.cause
	else:
		return str(code)

#get time range for current and previous shifts
def get_time_range(shift):
	event_time=[]
	current_shift=""
	timenow=datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
	raw_nst=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 07:00:00"+".0"
	nst=datetime.strptime(str(raw_nst), "%Y-%m-%d %H:%M:%S.%f")
	raw_net=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 19:00:00"+".0"
	net=datetime.strptime(str(raw_net), "%Y-%m-%d %H:%M:%S.%f")
	if timenow>=nst and timenow<=net:
		current_shift="morning"
		#event_time.append(nst)
		#event_time.append(net)
	else:
		current_shift="night"
		timenow2=datetime.strptime(str(datetime.now() - timedelta(days=1)), "%Y-%m-%d %H:%M:%S.%f")
		raw_nst=str(timenow2.year)+"-"+str(timenow2.month)+"-"+str(timenow2.day)+" 19:00:00"+".0"
		nst2=datetime.strptime(str(raw_nst), "%Y-%m-%d %H:%M:%S.%f")
		raw_net=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 07:00:00"+".0"
		net2=datetime.strptime(str(raw_net), "%Y-%m-%d %H:%M:%S.%f")
		#event_time.append(nst2)
		#event_time.append(net2)
	if shift ==	"current" and current_shift =="morning":
		event_time.append(nst)
		event_time.append(net)
	elif shift == "current" and current_shift == "night": 
		##if time is btw 19pm and 23pm, return same date
		raw_nst4=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 23:59:59"+".999999"
		sampled=datetime.strptime(str(raw_nst4), "%Y-%m-%d %H:%M:%S.%f")		
		if timenow>=net and timenow <= sampled:
			event_time.append(net) #net is the start time here which is 19pm
			event_time.append(sampled) #sampled is the end time here which is 23:59:59pm
		else:
			timenow3=datetime.strptime(str(datetime.now() - timedelta(days=1)), "%Y-%m-%d %H:%M:%S.%f")
			raw_net3=str(timenow3.year)+"-"+str(timenow3.month)+"-"+str(timenow3.day)+" 19:00:00"+".0"
			net3=datetime.strptime(str(raw_net3), "%Y-%m-%d %H:%M:%S.%f") 
			event_time.append(net3) #net3 is the start time here which is 7pm previous day
			event_time.append(nst) #nst is the end time here which is 7am same day
		
	elif shift == "previous" and current_shift == "morning":
		timenow2=datetime.strptime(str(datetime.now() - timedelta(days=1)), "%Y-%m-%d %H:%M:%S.%f")
		raw_nst=str(timenow2.year)+"-"+str(timenow2.month)+"-"+str(timenow2.day)+" 19:00:00"+".0"
		nst2=datetime.strptime(str(raw_nst), "%Y-%m-%d %H:%M:%S.%f")
		raw_net=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 07:00:00"+".0"
		net2=datetime.strptime(str(raw_net), "%Y-%m-%d %H:%M:%S.%f")

		event_time.append(nst2)
		event_time.append(net2)
	elif shift == "previous" and current_shift == "night":
		#if time is bwt 19pm and 23pm, return same date
		raw_nst4=str(timenow.year)+"-"+str(timenow.month)+"-"+str(timenow.day)+" 23:59:59"+".999999"
		sampled=datetime.strptime(str(raw_nst4), "%Y-%m-%d %H:%M:%S.%f")		
		#if timenow.time>=net.time and timenow.time <= sampled.time:
		if timenow>=net and timenow <= sampled:
			event_time.append(nst)
			event_time.append(net)
		else:
			timenow4=datetime.strptime(str(datetime.now() - timedelta(days=1)), "%Y-%m-%d %H:%M:%S.%f")
			raw_nst5=str(timenow4.year)+"-"+str(timenow4.month)+"-"+str(timenow4.day)+" 07:00:00"+".0"
			net4=datetime.strptime(str(raw_nst5), "%Y-%m-%d %H:%M:%S.%f")
			event_time.append(net4) #net2 is the start time here which is 7am previous day
			event_time.append(nst2)	#nst is the end time here which is 19m previous day 

	return event_time

@app.route('/')
@login_required
def index():
	#user=db.session.query(User).filter(User.userid==).first()
	#db.session.commit()
	

	return render_template('public/index.html', count='count',reason='mach',test='ML U Stops Events')


@app.route('/login',methods=['GET','POST'])
def login():
	response=''
	form = LoginForm()
	url = url_for('login')

	if request.method =='POST':
		if form.validate_on_submit():
			
			loguser=USERACCOUNT()	
			resp=loguser.loginservice(form)

			if resp['status'] == 1:

				return redirect('/')

			elif resp['status'] == 3:

				return redirect('/changetemppass?userid='+str(resp['id']))

			else:
				response = 	resp['message']


		else:
			response='Form error, please try again!'	 

	return render_template('userlogin.html',form=form,resp=response,url=url)

@app.route('/changetemppass',methods=['GET','POST'])
def changetemppass():
	response=''
	form = ChangePasswordForm()
	url = url_for('changetemppass')
	userid = request.args.get("userid",int)

	if request.method =='POST':
		if form.validate_on_submit():

			##check that the two password inputs are the same#

			if form.password1.data == form.password2.data :
				loguser=USERACCOUNT()
				if loguser.is_temp_password(userid,form.password1.data):
					response = "Password must not be the same as the temporary password."
				else:
					##attempt to change password#
					resp=loguser.change_temp_password(userid,form.password1.data)
					
					if resp['status']==2:
						response=resp['message']
					else:
						res=Markup("<div class='alert alert-success'>{}</div>".format('Password reset was successful. Now login with your new password.'))
						flash(res,'info')
						return redirect('/login')

			else:
				response = "Password1 and password2 do not match."				
			
		else:
			response='Form error, please try again!'	 

	return render_template('changetemppass.html',form=form,resp=response,userid=userid,url=url)	

@app.route('/logout',methods=['GET'])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect('/login')	

@app.route('/adduser',methods=['GET','POST'])
@login_required
def adduser():

    if not current_user.is_authenticated:
        return redirect('/login')

    if session['adminlevel'] < 2:
    	return redirect('/')

    new = AdminRoles()

    form = AddUserForm()
    form.role.choices = [(x.rid,x.rname) for x in new.get_admin_roles()]
    form.department.choices = [(x.did,x.abbr) for x in new.get_departments()]
    form.department.choices.insert(0,('','Select'))
    response=""
    if request.method == 'POST':
    	if form.validate_on_submit():
    		loguser=USERACCOUNT()
    		resp=loguser.addnewuser(form)
    		if resp['status'] == 2:
    			response = Markup("<div class='alert alert-danger'>{}</div>".format(resp['message']))
    		else:
    			form = AddUserForm()
    			response = Markup("<div class='alert alert-success'>{}</div>".format(resp['message']))

    	else:
    		form_errors=''
    		for x in dict(form.errors.items()):

    			form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'
    		response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))	


    return render_template('adduser.html',form=form,resp=response)	    

@app.route('/userview',methods=['GET','POST'])
@login_required
def userview():
	if not current_user.is_authenticated:
		return redirect('/login')

	if session['adminlevel'] < 2:
		return abort(403)

	new = MYSCHOOL()
	response=''
	userinfo=new.get_user()

	if request.method =='POST':
		if request.args.get('action')=='DELETE':
			data=request.get_json()
			itemID=data['itemid']
			db.session.query(User).filter_by(userid=itemID).delete()
			db.session.commit()

			response = Markup("<div class='alert alert-success'>{}</div>".format('User successfully deleted.'))
			
			return json.dumps({'status':1,'message':response}) 

		elif request.args.get('action')=='VIEW-SKILLS':
			data=request.get_json()
			userID=data['userid']
			user= USERACCOUNT()
			resp = user.get_skills(userID)

			#response = Markup("<div class='alert alert-success'>{}</div>".format('User successfully deleted.'))
			
			return json.dumps({'status':1,'data':resp}) 

	return render_template('userview.html',resp=response,userinfo=userinfo,count=len(userinfo))


@app.route('/userprofile',methods=['GET','POST'])
@login_required
def profile():

	if not current_user.is_authenticated:
		return redirect('/login')

	userinfo = db.session.query(User).filter_by(userid=session['userid']).first()

	if request.method == 'POST':
		data = request.get_json()
		userid = data['itemid']
		user= USERACCOUNT()
		resp = user.changepassword(userid,data['old'],data['new'])
		return json.dumps(resp)

	return render_template('userprofile.html',userinfo=userinfo)

@app.route('/edituser',methods=['GET','POST'])
@login_required
def useredit():
	if not current_user.is_authenticated:
		return redirect('/login')

	if session['adminlevel'] < 5:
		return abort(403)\

	new = AdminRoles()
	new2 = MYSCHOOL()	
	
	form = EditUserForm()
	form.role.choices = [(x.rid,x.rname) for x in new.get_admin_roles()]
	form.department.choices = [(x.did,x.abbr) for x in new.get_departments()]

	userid = request.args.get('userid',int)
	response = ''
	user = new2.get_user(userid)

	user_edit="{} {}".format(user.fname,user.sname)

	if request.method =='GET':
		form.acctype.data=user.acctype
		form.fname.data=user.fname.title()
		form.sname.data=user.sname.title()
		form.email.data=user.email
		form.phone.data=user.phone
		if user.user_roles:
			roles = json.loads(user.user_roles)
			form.role.data=roles
		form.adminlevel.data=user.adminlevel
		form.department.data=user.department
		form.block_stat.data=user.block_stat
		form.team.data = user.team
		form.username.data=user.username

	elif request.method =='POST':

		if form.validate_on_submit():

			db.session.query(User).filter(User.userid==userid).update({
				'acctype':form.acctype.data,
				'fname':form.fname.data,
				'sname':form.sname.data,
				'phone':form.phone.data,
				'email':form.email.data,
				'role':1,
				'user_roles': json.dumps(form.role.data) if form.role.data else '',
				'adminlevel':form.adminlevel.data,
				'department':form.department.data,
				'block_stat':form.block_stat.data,
				'team': form.team.data,
				'username':form.username.data})
			db.session.commit()


			res=Markup("<div class='alert alert-success'>{}</div>".format('User information successfully updated.'))
			flash(res,'info')
			return redirect('/userview') 

	return render_template('edituser.html',resp=response,userid=userid, form=form,user=user_edit)

@app.route('/reset_password',methods=['GET','POST'])
def reset_password():
	form=forgotPasswordForm()
	response=''

	if not current_user.is_authenticated:
		return redirect('/login')

	if session['adminlevel'] < 5:
		return redirect('/')

	if request.method == 'POST' :
		if form.validate_on_submit():
			user=db.session.query(User).filter_by(username=form.username.data).count()
			if user ==0:
				response = Markup("<div class='alert alert-danger'>User does not exist. Please recheck the username provided.</div>")
				return render_template('passwordreset.html',resp=response,form=form)

			loguser=USERACCOUNT()
			resp=loguser.reset_password(form)	

			if resp['status'] == 2:
				response = Markup("<div class='alert alert-danger'>{}</div>".format(resp['message']))
			else:
				response = Markup("<div class='alert alert-success'>{}</div>".format(resp['message']))

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'
			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))
				
	return render_template('passwordreset.html',resp=response,form=form)

@app.route('/bos',methods=['GET','POST'])
@login_required
def bos_observation():

	if not current_user.is_authenticated:
		return redirect('/login')

	response=''

	bos=request.args.get('type') 
	depart= request.args.get('department')

	if bos == 'SAFETY':
		if depart=='PSG':
			form = SAFETYBOSForm()
			template = 'safetybos.html'
		elif depart=='MSG':
			form=MSG_SAFETYBOSForm()
			template='bos/msgsafetybos.html'
		elif depart=='WHSE':
			form=WHSE_SAFETYBOSForm()
			template='bos/whsesafetybos.html'
		elif depart=='WHSERPM':
			form=WHSE_RPMBOSForm()
			template='bos/whsesafetyrpmbos.html'
		elif depart=='QA':
			form=LAB_SAFETYBOSForm()
			template='bos/labsafetybos.html'
		elif depart=='UTILITY':
			form=UTILITY_SAFETYBOSForm()
			template='bos/utilitysafetybos.html'

		if request.method == "POST":
			if form.validate_on_submit():

				Bos=BOSCLASS()
				resp=Bos.log_safety_bos(form,depart)

				if resp["status"] == 1:
					response=Markup("<div class='alert alert-success'>{}</div>".format(resp["message"]))
					return redirect("/bos_status?message={}".format(response))
				else:
					response=Markup("<div class='alert alert-danger'>{}</div>".format(resp["message"]))	
			else:
				form_errors=''
				for x in dict(form.errors.items()):
					form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

				response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))

	elif bos == 'QUALITY':
		if depart=='PSG':
			form = QABOSForm()
			template = 'qualitybos.html'
		elif depart=='MSG':
			form=MSG_QABOSForm()
			template='bos/msgqualitybos.html'
		elif depart=='WHSE':
			form=WHSE_QABOSForm()
			template='bos/whsequalitybos.html'
		elif depart=='QA':
			form=LAB_QABOSForm()
			template='bos/labqualitybos.html'					

		if request.method== 'POST':
			if form.validate_on_submit():
				Bos=BOSCLASS()
				resp=Bos.log_quality_bos(form,depart)

				if resp["status"] == 1:
					response=Markup("<div class='alert alert-success'>{}</div>".format(resp["message"]))
					return redirect("/bos_status?message={}".format(response))
				else:
					response=Markup("<div class='alert alert-danger'>{}</div>".format(resp["message"]))	

			else:
				form_errors=''
				for x in dict(form.errors.items()):
					form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

				response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))

	elif bos == 'OGC':		
		if depart=='PSG':
			form = OGCBOSForm()
			template = 'ogcbos.html'
		elif depart=='MSG':
			form=MSG_OGCBOSForm()
			template='bos/msgogcbos.html'

		if request.method == 'POST':
			if form.validate_on_submit():
				Bos=BOSCLASS()
				resp=Bos.log_ogc_bos(form,depart)

				if resp["status"] == 1:
					response=Markup("<div class='alert alert-success'>{}</div>".format(resp["message"]))
					return redirect("/bos_status?message={}".format(response))

				else:
					response=Markup("<div class='alert alert-danger'>{}</div>".format(resp["message"]))	
			
			else:
				form_errors=''
				for x in dict(form.errors.items()):
					form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

				response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))	


	form.observer.data=session['fullname']
	
	return render_template(template,form=form,resp=response)


@app.route('/bos_status',methods=['GET'])
@login_required
def bos_observation_status():

	if not current_user.is_authenticated:
		return redirect('/login')

	report=request.args.get('message')
	response=Markup("<div class='alert alert-danger'>{}</div>".format(report))	
		
	return render_template('bos_status.html',resp=response)

@app.route('/viewbos',methods=['GET','POST'])
@login_required
def viewbos():

	if not current_user.is_authenticated:
		return redirect('/login')

	if session['adminlevel'] <=1:
		abort(403)

	response=''
	myquery=[]
	bos=''	
	
	form= ViewBOSForm()	
	
	if request.method == 'POST' and request.args.get('type')=='form':

		
		if form.validate_on_submit():
			bos=form.bos_type.data
			start=str(form.start.data) + ' 00:00:00'
			end=str(form.end.data) + ' 00:00:01'

			if bos == 'SAFETY': #(ProductOrder.ordertime > request.args.get('start_date')) | (ProductOrder.ordertime > request.args.get('end_date'))
				myquery=db.session.query(SAFETY_BOS).filter(SAFETY_BOS.bos_time.between(start,end)).all()				
			elif bos == 'QUALITY':
				myquery=db.session.query(QA_BOS).filter(QA_BOS.bos_time.between(start,end)).all()
			elif bos == 'OGC':
				myquery=db.session.query(OGC_BOS).filter(OGC_BOS.bos_time.between(start,end)).all()

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))

	elif request.method == 'POST' and request.args.get('type')=='ajax':

		if request.args.get('action')=='OGC':
			data = request.get_json()
			itemID=int(data['itemid'])

			db.session.query(OGC_BOS).filter(OGC_BOS.ogcid==itemID).delete()
			db.session.commit()
			return json.dumps({'status':1,'message':'Item deleted successfully!'})

		elif request.args.get('action')=='SAFETY':
			data = request.get_json()
			itemID=int(data['itemid'])

			db.session.query(SAFETY_BOS).filter(SAFETY_BOS.sid==itemID).delete()
			db.session.commit()
			return json.dumps({'status':1,'message':'Item deleted successfully!'})

		elif request.args.get('action')=='QUALITY':
			data = request.get_json()
			itemID=int(data['itemid'])

			db.session.query(QA_BOS).filter(QA_BOS.qid==itemID).delete()
			db.session.commit()
			return json.dumps({'status':1,'message':'Item deleted successfully!'})		

		return json.dumps({'status':2,'message':'Your request could not be executed.'})	

	return render_template('viewbos.html',form=form,resp=str(form.end.data),enteries=myquery,bos=bos)		

@app.route('/leadershipbos',methods=['GET'])
@login_required
def leadershipbos():

	form = LeadershipBOSForm()

	return render_template('bos/leadershipbos.html',form=form)


@app.route('/psgproduction',methods=['GET','POST'])
@login_required
def psgproduction():

	if not current_user.is_authenticated:
		return redirect('/login')

	form=PSGProductionForm()
	form.productcode.choices=[(g.productcode,g.description) for g in SKU.query.order_by(SKU.weight.asc()).all()]
	form.productcode.choices.insert(0,(0,"Select"))
	form.start.data = '00:00'
	form.end.data = '00:00'
	response= ''

	if request.method == 'POST':

		if request.args.get('action')=='FETCH-MACHINES':
			data = request.get_json()

			machine=Equipment.query.filter_by(line_number=data['line']).order_by(Equipment.m_code.asc()).all()
			
		
			machine_option='';

			for m in machine :
				machine_option +='<option value="'+m.m_code+'">'+m.name+'</option>'
			

			return json.dumps({'status':1,'options':machine_option})

		elif request.args.get('action')=='ADD-PRODUCTION':
			
			data = request.get_json()
			data['start']=myfunc.format_datetyme(data['start'])
			data['end']=myfunc.format_datetyme(data['end'])

			newpro=PRODUCTION()
			#newpr=STOPSEVENT()						
			#kt=newpr.get_stop_data('W',data['start'],data['end'])
			#return json.dumps({'status':1,'message':str(kt)})

			##check if cases were added#

			if data["cases"]:
				##indicate that cases is included#
				
				resp=newpro.log_production_data(data,1)

			else:
				##indicate that cases is NOT included#
				#allstops = db.session.query(StopEvent).filter(StopEvent.machine=='R',StopEvent.start_time.between(data['start'],data['end'])).count()
				#resp = str(mmm.product_params)
				resp=newpro.log_production_data(data,0)
				#response = Markup("<div class='alert alert-success'>{}</div>".format("Production was successfully updated."))
				

			
			return json.dumps({'status':1,'message':resp})
				

	return render_template('psg/production.html', form=form,resp=response)

@app.route('/skuentry',methods=['GET','POST'])
@login_required
def skuentry():

	if not current_user.is_authenticated:
		return redirect('/login')

	form=SKUEntryForm()
	response=''
	
	codes=db.session.query(SKU).order_by(SKU.weight.desc()).all()

	if request.method == 'POST':


		if request.args.get('action')=='ADD' and form.validate_on_submit():

			##validate gcas and product code
			#check = SKU.query.filter_by(gcas=form.gcas.data).count()
			check_again = SKU.query.filter_by(productcode=form.productcode.data).count()
			if check_again>0:
				response = Markup("<div class='alert alert-danger'>{}</div>".format('this product code has already been registered.'))
			else:

				##add the sku to database#

				new=SKU()
				#new.gcas=form.gcas.data
				new.productcode=form.productcode.data
				new.weight=form.weight.data
				new.description=form.description.data
				db.session.add(new)
				db.session.commit()

				form.productcode.data=""
				form.weight.data=""
				form.description.data=""

				codes=db.session.query(SKU).order_by(SKU.weight.desc()).all()

				response = Markup("<div class='alert alert-success'>{}</div>".format('SKU registered successfully.'))

		elif request.args.get('action') == 'DELETE':

			data=request.get_json()
			itemID=int(data['itemid'])

			##delete all production parameters associated with this sku on all the machines#
			man=db.session.query(SKU).filter(SKU.skuid==itemID).first()			
			machine=Equipment.query.order_by(Equipment.mid.desc()).all()
			code=man.productcode

			for i in machine:
				if i.product_params and i.product_params !='[]':
					params = json.loads(i.product_params)
					check=[d for d in params if d['sku']!=code]
					db.session.query(Equipment).filter_by(mid=i.mid).update({'product_params':json.dumps(check)})
					db.session.commit()

			##now delete sku#		
			db.session.query(SKU).filter(SKU.skuid==itemID).delete()
			db.session.commit()
			return json.dumps({'status':1,'message':'Item deleted successfully!'})

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))	
	
	return render_template('psg/skuentry.html', form=form,resp=response,codes=codes)


@app.route('/machineview',methods=['GET','POST'])
@login_required
def equipment():

	if not current_user.is_authenticated:
		return redirect('/login')

	form=EquipmentEntryForm()	
	response=''
	
	codes=db.session.query(Equipment).order_by(Equipment.m_code.asc()).all()

	if request.method == 'POST':


		if request.args.get('action')=='ADD' and form.validate_on_submit():

			##validate machine code 
			check = Equipment.query.filter_by(m_code=form.mcode.data).count()
			
			if check >0 :
				response = Markup("<div class='alert alert-danger'>{}</div>".format('This machine code already exists. Machine code must be unique.'))
			else:
				
				##prepare process params#
				
				##add the sku to database#

				new=Equipment()
				new.name=form.name.data
				new.line_number=form.line_number.data
				new.lane=form.lane.data
				new.m_code=form.mcode.data
				#new.product_params=json.dumps(params)
				db.session.add(new)
				db.session.commit()

				codes=db.session.query(Equipment).order_by(Equipment.m_code.asc()).all()

				response = Markup("<div class='alert alert-success'>{}</div>".format('Machine registered successfully.'))

		elif request.args.get('action') == 'DELETE':

			data=request.get_json()
			itemID=int(data['itemid'])

			db.session.query(Equipment).filter(Equipment.mid==itemID).delete()
			db.session.commit()
			return json.dumps({'status':1,'message':'Machine deleted successfully!'})

		elif request.args.get('action')	=='FETCH-DATA' :
			machine=Equipment.query.order_by(Equipment.m_code.desc()).all()
			sku=SKU.query.order_by(SKU.weight.desc()).all()

			sku_option='<option value="">Select SKU</option>'
			machine_option='';

			for m in machine :
				machine_option +='<option value="'+m.m_code+'">'+m.name+'</option>'

			for s in sku :
				sku_option += '<option value="'+s.productcode+'">'+s.description+'</option>'

			return json.dumps({'status':1,'sku':sku_option,'machine':machine_option})

		elif request.args.get('action')=='ADD-PARAMS':
			data=request.get_json()
			
			errors=[]
			check=""

			sku=SKU.query.filter_by(productcode=data['sku']).first()

			info={'sku':data['sku'],'sku_name':sku.description,'bpc':data['bpc'],'cpp':data['cpp'],'speed':data['speed'],}
			

			for x in data['machines']:
				params=[]
				##check that the sku is not existing already#
				infor=db.session.query(Equipment).filter_by(m_code=x).first()

				if infor.product_params and infor.product_params !='[]':					
					inform=json.loads(infor.product_params)
					params=inform
					check=[d for d in inform if d['sku']==data['sku']]
										
				params.append(info)	

				if check:
					errors.append(x)
				else:
					
					db.session.query(Equipment).filter_by(m_code=x).update({'product_params':json.dumps(params)})
					db.session.commit()

			if errors:
				error= Markup("<div class='alert alert-danger'>{}: {}</div>".format('However, the following machines were not processed because selected sku data already exists for them',errors))
			else:
				error=""

			response =  Markup("<div class='alert alert-success'>{}</div><br>{}".format('Data added successfully.',error))
			return json.dumps({'status':1,'message':response,'error':error})		

		elif request.args.get('action') == 'DELETE-PARAM':
			data=request.get_json()
			infor=db.session.query(Equipment).filter_by(m_code=data['mcode']).first()

			param=json.loads(infor.product_params)

			newparam =[d for d in param if d['sku']!=data['sku']]

			if param is None:
				db.session.query(Equipment).filter_by(m_code=data['mcode']).update({'product_params':None})
				db.session.commit()	 	
			else:
				db.session.query(Equipment).filter_by(m_code=data['mcode']).update({'product_params':json.dumps(newparam)})
				db.session.commit()	

			response =  Markup("<div class='alert alert-success'>{}</div>".format('Item delted successfully.'))
			return json.dumps({'status':1,'message':response}) 	

		elif request.args.get('action') == 'EDIT ITEM':

			
			itemID=request.args.get('id')

			##check that the mcode does not already exist#
			check = Equipment.query.filter(Equipment.m_code==form.mcode.data,Equipment.mid!=itemID).count()

			if check >0:
				response =  Markup("<div class='alert alert-danger'>{}</div>".format('This machine code already exists.'))

			db.session.query(Equipment).filter(Equipment.mid==itemID).update({
				'm_code':form.mcode.data,
				'name':form.name.data,
				'lane':form.lane.data,
				'line_number':form.line_number.data})
			db.session.commit()
			response =  Markup("<div class='alert alert-success'>{}</div>".format('Machine information updated successfully.'))
			form=EquipmentEntryForm()
		
		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))	
	
	elif request.method == 'GET' and request.args.get('action') == 'EDIT':
		
		machine=db.session.query(Equipment).filter_by(mid=request.args.get('id')).first()

		form.mcode.data=machine.m_code
		form.name.data=machine.name
		form.lane.data=machine.lane
		form.line_number.data=machine.line_number
				
		return render_template('psg/machines.html', form=form,resp=response,codes=codes,action='EDIT ITEM',id=request.args.get('id'))

	return render_template('psg/machines.html', form=form,resp=response,codes=codes,action='ADD',id=0)


@app.route('/viewpsgproduction',methods=['GET','POST'])
@login_required
def psgproduction_result():
	results=''
	if not current_user.is_authenticated:
		return redirect('/login')

	response = ''
	form = ViewPSGResultForm()
	form.machine.choices = [(g.m_code,g.name) for g in Equipment.query.order_by(Equipment.m_code.asc()).all()]

	if request.method=='POST' and request.args.get('action')=='VIEW-RESULT':
		if form.validate_on_submit():
			fetch=PRODUCTION()			
			form.start.data = request.form['dateTimePicker1']
			form.end.data = request.form['dateTimePicker2']
			result = fetch.get_results(form)

			#x = form.start.data
			#y = form.end.data
			#result = {'status':2,'message': "{} {}".format(x,y)}

			if result['status']==1:
				results=result['data']
				total=result['total']
				
			else:				
				results=None
				response=Markup("<div class='alert alert-warning'>{}</div>".format(result['message']))

			total=result['total']
			start=result['start']
			end=result['end']
			
			return render_template('psg/resultview.html',start=start,end=end,form=form,total=total,results=results,resp=response)

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))	


	return render_template('psg/resultform.html',form=form,resp=response)

	
@app.route('/psgproduction_entries',methods=['GET','POST'])
@login_required
def psgproduction_entries():
	fetch=PRODUCTION()
	response =''
	form = PSGProductionEntryForm()
	form.machine.choices = [(g.m_code,g.name) for g in Equipment.query.order_by(Equipment.m_code.asc()).all()]
	if request.method == 'POST':
		if request.args.get('action')=='DELETE-ENTRY':
			data=request.get_json()			
			resp=fetch.erase_production_entries(data)
			return json.dumps(resp)

		if form.validate_on_submit():
			form.start.data = request.form['dateTimePicker1']
			form.end.data = request.form['dateTimePicker2']
			
			resp=fetch.get_production_entries(form)
			response =resp
			start=form.start.data
			end=form.end.data

			return render_template('psg/viewproductionentry.html',form=form,resp=response,start=start,end=end)

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))


	return render_template('psg/productionentry.html',form=form,resp=response)

@app.route('/psgproduction_report',methods=['GET','POST'])
@login_required
def psgproduction_report():
	new1 = MYSCHOOL()
	new2 = STOPSEVENT()
	new3 = PRODUCTION()
	report = None
	label = ''
	response = ''
	count = 0
	raw = None


	form = PSGProductionReportForm()
	form.machine.choices = [(x.m_code,x.name) for x in Equipment.query.order_by(Equipment.m_code.asc()).all()]
	form.include_downtime.choices = [(x.rid,x.reason) for x in new2.fetch_stops_reason_one()]
	form.exclude_downtime.choices = [(x.rid,x.reason) for x in new2.fetch_stops_reason_one()]
	form.transformation.choices = [(x.tid,x.reason) for x in new2.fetch_stops_reason_two()]
	
	action = request.args.get("action")	
	template = "psg/report_index.html"

	if request.method == 'POST' and action =='VIEW-REPORT':
		if form.validate_on_submit():			
			template = 'psg/dt_report_view.html'
			form.start.data = request.form['dateTimePicker1']
			form.end.data = request.form['dateTimePicker2']

			report = new3.get_psg_dt_report(form)
			label = Markup("<div class='alert alert-info'>From {} To {}</div>".format(form.start.data,form.end.data))
			count = len(report)
			raw = json.dumps(report)

		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'

			response =Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))

	elif request.method == 'POST' and action == 'NORMALIZED-REPORT':
		info = request.get_json()
		resp = new3.normalize_dt_report(info['data'])
		return resp

	return render_template(template,form=form,count=count,raw=raw,report=report,label=label,response=response)

@app.route('/user_roles',methods=['GET','POST'])
@login_required
def user_roles():
	new = AdminRoles()
	action = request.args.get("action")	
	template = "admin/admin_roles.html"
	form = AddRoles()	
	roles = new.get_admin_roles()	
	form.report_to.choices = [(x.rid,x.rname) for x in roles]
	form.report_to.choices.insert(0,(0,'Select'))
	form.skills.choices = [(str(x.t_code),x.title) for x in db.session.query(Trainings).filter(Trainings.priority!= 'A').order_by(Trainings.title.asc())]
	#resp = str(form.skills.data)
	resp = ''
	rid = ''

	if request.method !='POST' and action == 'UPDATE-ROLE': 
		template = "admin/edit_admin_role.html"
		rid = request.args.get('id')
		role = new.get_admin_roles(rid)
		form.name.data = role.rname
		form.description.data = role.description
		form.report_to.data = role.report_to
		if role.rnr:
			form.rnr.data = ';'.join(json.loads(role.rnr))
		form.report_to.data = role.report_to

		
	if request.method =='POST' and action == 'UPDATE-ROLE':	
		idd = request.args.get('id',int)
		role = new.update_admin_role(idd,form)		
		flash(role)

		
	if request.method=='POST' and action == 'ADD-ROLE':
		if form.validate_on_submit():
			response = new.add_user_role(form)
			flash(response['message'],'information')
		else:
			form_errors=''
			for x in dict(form.errors.items()):
				form_errors +='<span>'+x+'</span><span> is not valid.</span><br>'				

			response = Markup("<div class='alert alert-danger'>{}</div>".format(form_errors))
			

	if request.method=='POST' and action == 'DELETE-ROLE':
		data = request.get_json()
		response = new.delete_admin_role(data['itemid'])
		return response

	if request.method=='POST' and action == 'DELETE-SKILL':
		data = request.get_json()
		response = new.delete_skill_from_role(data['rid'],data['tcode'])
		return response

	if request.method=='POST' and action == 'FETCH-SKILL-SET':
		data = request.get_json()		
		response = new.fetch_skillset(data['rid'])
		if response is not None:
			return json.dumps({'status':1, 'data': response})
		else:
			return json.dumps({'status':2, 'data': None})

	if request.method=='POST' and action == 'ADD-SKILLS-TO-ROLE':
		data = request.get_json()		
		response = new.add_skills_to_role(data['rid'],data['trainings'])
		return response
	
	roles = new.get_admin_roles()
	
	return render_template(template, roles = roles, form = form, resp = resp, rid=rid)

@app.route('/e_learning',methods=['GET','POST'])
@login_required
def my_e_learning():

	if not current_user.is_authenticated:
		return redirect('/login')

	response = ''
	new = MYSCHOOL()
	new2 = AdminRoles()

	template = 'e_learning/index.html'
	my_users = [x for x in new.get_user() if x.userid != session['userid']]

	if request.args.get('action') == '' and request.method=='GET':
		new.run_expiry_report(session['userid'])

	if request.args.get('action') == 'ADD-TRAINING':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))

		template = 'e_learning/add_training.html'
		departments = new2.get_departments()

		return render_template(template,department=departments)

	elif request.args.get( 'action') == 'ADD-QUIZ':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))
		response = ''
		qualification_type = ''	

		quiz_infor = None	

		template = 'e_learning/add_quiz.html'
		tid = request.args.get('tid')

		course = new.get_training(tid)		

		if request.method == 'POST':
			if request.args.get('what') == 'UPDATE-SETTINGS':
				form = {}
				form["attempt"] = request.form["attempt"]
				form["qualification_type"] = request.form["qualification_type"]
				form["banner"] = request.files["banner_img"]
				form["tid"] = request.args.get("tid")
				data = new.update_quiz_questions(form,'settings')

				if data['status'] == 1:
					response = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
				else:
					response = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))

				flash(response,'information')

			elif request.args.get('what') == 'ADD-QUIZ_QUESTION':
				info = request.get_json()
				form = {}
				form["question"] = info["question"]
				form["question_type"] = info["questionType"]
				form["options"] = info["options"].split(";")
				form["answer"] = info["answers"]
				form["tid"] = request.args.get("tid")
				data = new.update_quiz_questions(form,'question')

				if data['status'] == 1:
					response = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
				else:
					response = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))

				return json.dumps({'status':data['status'], 'message':response})

			elif request.args.get('what') == 'DELETE-QUESTION':
				info = request.get_json()
				form = {}
				form["question"] = info["question"]				
				form["tid"] = info["tid"]
				data = new.delete_quiz_question(form)

				if data['status'] == 1:
					response = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
				else:
					response = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))

				return json.dumps({'status':data['status'], 'message':response})	

		if course.quiz_link is not None:
			quiz_infor = json.loads(course.quiz_link)
			qualification_type = quiz_infor['qualification_type'] #if 'qualification_type' in quiz_infor.keys() else ''	

		return render_template(template,course=course,quiz_infor=quiz_infor,qualification_type=qualification_type)	

	elif request.args.get( 'action') == 'FETCH-USERS':

		kyc = ''
		depart = ''

		users = User.query.filter(User.adminlevel > 2).order_by(User.sname.asc())
		departments = new2.get_departments()

		for user in users:
			fullname = "{} {}".format(user.sname, user.fname)
			kyc += '<option value='+str(user.userid)+'>'+fullname+'</option>'
		for department in departments:
			depart += '<option value="SAFETY">'+department.abbr+'</option>' if department.abbr == 'HS&E' else '<option value="'+department.abbr+'">'+department.abbr+'</option>'
			
		return json.dumps({'status':1, 'data':kyc,"departments":depart})

	elif request.args.get('action') == 'GET-QUIZ':			
		quiz_infor = None
		page_banner = None

		template = request.args.get('template')
		pass_mark = request.args.get('pass')
		qid = request.args.get('id')
		tid = request.args.get('tid')

		course = Trainings.query.filter_by(tid=tid).first()

		if course.quiz_link is not None:
			quiz_infor = json.loads(course.quiz_link)			
			page_banner = quiz_infor['banner_image']
			if quiz_infor['qualification_type'] == 'acknowledgement':
				template = 	'e_learning/tr_acknowledge_template.html'		

		return render_template(template,page_banner=page_banner,pass_mark=pass_mark,qid=qid,tid=tid,training=course,quiz_infor=quiz_infor)

	elif request.args.get('action') == 'manual_qualification':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))

		template = 'e_learning/manual_qualification.html'				

		course = Trainings.query.order_by(Trainings.title.desc())
		users = new.get_user()
		q = users #[x for x in users if x.adminlevel > 2 ]		

		if request.method == 'POST':
			form = request.form			
			mlist = [int(form['trainee'])] #request.form.getlist('trainees')
			new_form = {}
			new_form['tid'] = int(form['tid'])
			new_form['qualifier'] = int(form['qualifier'])
			new_form['score'] = form['score']
			new_form['suc'] = form['suc']
			new_form['certificate'] = request.files['certifikate']
						
			for trainee in mlist:
				new_form['userid'] = trainee				
				get_data = db.session.query(MyQualification).filter(MyQualification.userid==new_form['userid'],MyQualification.training_id==new_form['tid']).first()
				new_form['quizid'] = get_data.qid if get_data else 0
				user = new.get_user(trainee)				
				folder_name = "{}_{}/".format(user.userid,user.sname)
				new_form['certificate_path'] = "{}{}".format(CERTIFICATE_FOLDER,folder_name)
				if not new.check_file(new_form['certificate_path']):
					os.mkdir("{}{}".format(APP_ROOT,new_form['certificate_path']))			
				new.record_training_score(new_form,1)			
			response = Markup("<div class='alert alert-success'>{}</div>".format('Training records updated successfully for users.'))
			
			flash(response,"info")

		return render_template(template,trainings=course,qualifier_list=q,users=users)	

	elif request.args.get('action') == 'VIEW-RECORDS':
		if session['adminlevel'] < 2:
			return redirect(url_for('index'))
		new.run_expiry_report()

		template = 'e_learning/record_view.html'
		courses = Trainings.query.order_by(Trainings.title.asc())
		users = new.get_user()

		records = None
		title = ''
		overall = ""
		
		if request.method == 'POST':
			if request.form['id'] and request.form['id'].isnumeric(): #specific training report
				data = new.fetch_qualification_records(request.form)
				records = data['data']
				title = "{}".format(data['title'])
				overall = data["overall"]			 				

		return render_template(template,records=records, title=title,courses=courses,overall=overall,users=users)

	elif request.args.get('action') == 'VIEW-GENERAL-RECORDS':		
		info = request.get_json()
		instance = request.args.get('instance')
		if instance == 'exportable':
			data = new.get_exportable_training_report(info)
		else:
			data = new.get_training_report(info)		

		return json.dumps({'status':1, 'data':data, 'message':''})

	elif request.args.get('action') == 'MANAGE':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))
		
		template = 'e_learning/manage_courses.html'
		courses = Trainings.query.order_by(Trainings.title.asc())

		records = None
		
		
		if request.method == 'POST' and request.args.get('what') =='DELETE':

			data = new.delete_course(request.get_json())

			if data['status'] == 1:

				response = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
			else:
				response = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))
			
			return json.dumps({'status':data['status'], 'message':response})

		if request.method == 'POST' and request.args.get('what') =='DELETE-FILE':
			data = request.get_json()

			try:
				os.remove("{}{}".format(APP_ROOT,data["link"]))				
				if data['doc_type'] == 'extra':
					training = Trainings.query.filter_by(tid=data['tid']).first()
					if len(training.extra_resource) > 1:
						extra_resource = json.loads(training.extra_resource)
						extra_resource = json.dumps([x for x in extra_resource if x != data['link']])
					else:
						extra_resource = None	
					Trainings.query.filter_by(tid=data['tid']).update({'extra_resource':extra_resource})
					db.session.commit()
				elif data['doc_type'] == 'doc':
					Trainings.query.filter_by(tid=data['tid']).update({'doc_link':None})
					db.session.commit()
				elif data['doc_type'] == 'suc':
					StepupCards.query.filter_by(training_id=data['tid']).delete()
					db.session.commit()				
				response = Markup("<div class='alert alert-success'>File deleted successfully.</div>")
				status = 1
			except:
				response = Markup("<div class='alert alert-danger'>Could not delete file.</div>")
				status = 2

			return json.dumps({'status':status, 'message':response})		

		return render_template(template,records=records,courses=courses)

	elif request.args.get('action') == 'EDIT-COURSE':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))
		resp = ''
		extra_resource = ''
		suc_link = ''
		doc_link = ''
		template = 'e_learning/edit_training.html'
		tid = request.args.get('tid')

		if request.method == 'POST':
			form = request.form
			files = request.files 
			data = new.add_training(form,int(tid),files)

			if data['status'] == 1:
				mess = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
				flash(mess,'information')
				return redirect('/e_learning?action=MANAGE')
			else:
				resp = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))
				flash(resp,"information")	

		##get the course
		course = Trainings.query.filter_by(tid=tid).first()
		if course.extra_resource and len(course.extra_resource) > 0:
			resource = json.loads(course.extra_resource)
			for link in resource:
				extra_resource += Markup('<label style="font-size:12px;color:red">'+link.split('/')[-1].split('.')[0][0:35]+'<span style="color: #179cd7;" onclick="deleteFile(\''+link+'\',\'extra\')">......x</span></label><br>')
		if course.suc:
			stepup = StepupCards.query.filter_by(training_id=course.tid).first()
			if stepup and stepup.suc_link:
				suc_link = Markup('<label style="font-size:12px;color:red">'+stepup.suc_link.split('/')[-1].split('.')[0][0:35]+'<span style="color: #179cd7;" onclick="deleteFile(\''+stepup.suc_link+'\',\'suc\')">......x</span></label>')
		if course.doc_link:
			doc_link = 	Markup('<label style="font-size:12px;color:red">'+course.doc_link.split('/')[-1].split('.')[0][0:35]+'<span style="color: #179cd7;" onclick="deleteFile(\''+course.doc_link+'\',\'doc\')">......x</span></label>')
		
		return render_template(template, course = course,extra_resource=extra_resource,suc_link=suc_link,doc_link=doc_link)


	if request.method == 'POST' and request.args.get('action') == 'PROCESS-DATA':
		if session['adminlevel'] < 3:
			return redirect(url_for('index'))

		template = 'e_learning/add_training.html'
		form = request.form
		files = request.files		
		
		data = new.add_training(form,0,files)

		if data['status'] == 1:

			response = Markup("<div class='alert alert-success'>{}</div>".format(data['message']))
		else:
			response = Markup("<div class='alert alert-danger'>{}</div>".format(data['message']))
		
		flash(response,"info")	
		return render_template(template)

	elif request.method == 'POST' and request.args.get('action') == 'POST-RESULT':
		
		mes = request.get_json()
		
		data = new.record_training_score(mes)

		return json.dumps(data)

	elif request.method == 'POST' and request.args.get('action') == 'EXPORT-DATA':
		data = request.get_json()
		
		file = new.export_data_to_excell(data)
		return file #json.dumps({'status':1,'message':'good'})

	elif request.method == 'POST' and request.args.get('action') == 'FETCH-TRAININGS':
		
		mes = request.get_json()
		
		data = new.fetch_trainings(mes)

		return json.dumps(data)

	return render_template(template,my_users=my_users)

@app.route('/skills_matrix',methods=['GET','POST'])
@login_required
def skills_matrix():
	
	username = ''
	records = None
	new = MYSCHOOL()
	new2 = AdminRoles()
	new3 = MYSCHOOL_REPORT()
	teams = []	
	A = 0
	T = 0
	M = 0
	userid = 0

	my_users = [x for x in new.get_user() if x.userid != session['userid']]


	action = request.args.get('action')

	if action == 'INDIVIDUAL':
		userid = request.args.get('userid')
		user = new.get_user(userid)		
		username = "{} {}".format(user.sname,user.fname)
		template = 'e_learning/individual_skillz.html'		
		form = {}
		form['userid'] = userid
		form['filter'] = request.args.get('filter')
		form['value'] = ''
		data = new3.fetch_individual_trainings(form)
		T = data['T']
		A = data['A']
		M = data['M']

	elif action == 'DEPARTMENT':
		template = 'e_learning/department_users_completion_view.html'
		dept = request.args.get('id',int)
		data = new3.fetch_department_users_report(dept)
		info = new2.get_departments(dept)
		T = data['T']
		A = data['A']
		M = data['M']
		username = info.abbr
		userid = int(dept)
		if userid == 1 or userid == 2:
			TEAMS = ['A','B','C','SUPPORT']
			count = 0
			for x in TEAMS:
				report = new.get_teams_report(int(dept),x)
				count += 1
				mr = {}
				mr['count'] = count
				mr['title'] = x
				mr['T'] = report['total'] if report['total'] >0 else 'Nil'
				mr['M'] = report['m'] if report['m'] >0 else 'Nil'
				mr['A'] = report['a'] if report['a'] >0 else 'Nil'
				teams.append(mr)

	elif action == 'FILTER-RESULT':
		data = request.get_json()
		result = new3.fetch_individual_trainings(data)
		return json.dumps(result)

	elif action == 'TEAM-REPORT':
		data = request.get_json()
		result = new3.fetch_team_members_report(data['team'],data['department'])
		return json.dumps(result)

	return render_template(template,A=A,M=M,T=T,records=data['data'],username=username,userid=userid,teams = teams)

@app.route('/uva_a')
@login_required
def uvaa():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="A"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('a.html',stops=xk,form=form)

@app.route('/uva_b')
@login_required
def uvab():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="B"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('b.html',stops=xk,form=form)

@app.route('/uva_c')
@login_required
def uvac():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="C"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
		#elif i.end_time is not None and count ==num:
			#l=str(i.end_time)
			#end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			#time=end-start
			#mytime=divmod(time.total_seconds(), 60)
			#downtime=int(mytime[0])

			#xy['startdate']=format_datetime(i.start_time)['date']
			#xy['start_time']=format_datetime(i.start_time)['time']
			#xy['uptime']=''
			#xy['downtime']=str(downtime)
			#xy['error']=get_error(i.error)
			#xy["sid"]=i.sid
			#xk.append(xy)

	return render_template('c.html',stops=xk,form=form)

@app.route('/uva_d')
@login_required
def uvad():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="D"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('d.html',stops=xk,form=form)


@app.route('/uva_e')
@login_required
def uvae():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="E"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('e.html',stops=xk,form=form)

@app.route('/uva_f')
@login_required
def uvaf():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="F"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('f.html',stops=xk,form=form)

@app.route('/uva_g')
@login_required
def uvag():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="G"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('g.html',stops=xk,form=form)

@app.route('/uva_h')
@login_required
def uvah():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="H"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('h.html',stops=xk,form=form)

@app.route('/ml_i')
@login_required
def mli():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="I"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('i.html',stops=xk,form=form)

@app.route('/ml_j')
@login_required
def mlj():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="J"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('j.html',stops=xk,form=form)

	
@app.route('/ml_k')
@login_required
def mlk():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="K"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('k.html',stops=xk,form=form)

@app.route('/ml_l')
@login_required
def mll():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="L"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('l.html',stops=xk,form=form)

	
@app.route('/ml_m')
@login_required
def mlm():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="M"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('m.html',stops=xk,form=form)

	
@app.route('/ml_n')
@login_required
def mln():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="N"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('n.html',stops=xk,form=form)

	

@app.route('/ml_r')
@login_required
def mlr():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="R"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('r.html',stops=xk,form=form)
	
@app.route('/ml_s')
@login_required
def mls():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="S"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)


	return render_template('s.html',stops=xk,form=form)

@app.route('/ml_t')
@login_required
def mlt():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="T"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			

	return render_template('t.html',stops=xk,form=form)
	
@app.route('/ml_u',methods=['GET','POST'])
@login_required
def mlu():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="U"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		#myevent=StopEvent.query.filter_by(machine=mach,(start_time>=tr1)|((start_time<=tr1)&(end_time<=tr2)),(end_time<=tr2)|((end_time>=tr2)&(start_time<=tr2))|((end_time=None)&(start_time<=tr2))).order_by(StopEvent.start_time.desc())
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			#t +=Markup('<p style="color: green;"><div style="color:green;height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span style="color: green;"><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span style="color: green;"><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span style="color: green;">...</span></p>')
		
	return render_template('u.html',stops=xk,form=form)

@app.route('/ml_v')
@login_required
def mlv():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="V"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('v.html',stops=xk,form=form)	

@app.route('/ml_w')
@login_required
def mlw():
	if not current_user.is_authenticated:
		return redirect('/login')

	mach="W"
	form=StopsForm()
	if request.args.get("shift")=="current":
		tr1=get_time_range("current")[0]
		tr2=get_time_range("current")[1]
		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="previous":
		tr1=get_time_range("previous")[0]		
		tr2=get_time_range("previous")[1]		
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		count=-1
	elif request.args.get("shift")=="userdefined":
		fetch=STOPSEVENT()
		myevent=fetch.get_user_defined_stops(request.args.get("startD"),request.args.get("startT"),request.args.get("endD"),request.args.get("endT"),mach)	
		count=-1
	else:
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach).order_by(StopEvent.start_time.desc()).limit(30).all()
		count=0

	t=''
	num=len(myevent)
	
	xk=[]
	for i in myevent:
		count=count+1
		xy={}
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			if i.reason_level_one:
				xy['r1']='<option value="'+str(i.reason_level_one)+'"></option>'
			else:
				xy['r1']='<option value="">Select</option>'

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=str(downtime)
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)
			
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])

			xy['startdate']=format_datetime(i.start_time)['date']
			xy['start_time']=format_datetime(i.start_time)['time']
			xy['uptime']=str(uptime)
			xy['downtime']=''
			xy['error']=get_error(i.error)
			xy["sid"]=i.sid
			xk.append(xy)

	return render_template('w.html',stops=xk,form=form)

@app.route('/livechat')
@login_required
def livechat():
	if not current_user.is_authenticated:
		return redirect('/login')

	return render_template('public/livestops.html')


@app.route('/fetchreasons',methods=['GET','POST'])
def fetchreasons():
	k=int(request.args.get('id'))
	w=request.args.get('field')
	t='<option value="">Select...</option>'
	if w=='stop_trans':
		mystop=ReasonTwo.query.filter_by(reason_one=k).order_by(ReasonTwo.tid.asc())
		for x in mystop:
			t+='<option value="'+str(x.tid)+'">'+x.reason+'</option>'

	elif w=='stop_comp':
		mystop=ReasonTri.query.filter_by(reason_two=k).order_by(ReasonTri.trid.asc())
		for x in mystop:
			t+='<option value="'+str(x.trid)+'">'+x.reason+'</option>'

	elif w=='stop_mode':
		mystop=ReasonFour.query.filter_by(reason_tri=k).order_by(ReasonFour.fid.asc())
		for x in mystop:
			t+='<option value="'+str(x.fid)+'">'+x.reason+'</option>'

	elif w=="fetch_all":
		def get_reas(num,id):
			if num==1:
				sew=ReasonOne.query.filter_by(rid=id).first()
				if sew is not None:
					return sew.reason
			elif num==2:
				sew=ReasonTwo.query.filter_by(tid=id).first()
				if sew is not None:
					return sew.reason
			elif num==3:
				sew=ReasonTri.query.filter_by(trid=id).first()
				if sew is not None:
					return sew.reason
			elif num==4:
				sew=ReasonFour.query.filter_by(fid=id).first()
				if sew is not None:
					return sew.reason		
			return ""	

		data=[]
		mystop=StopEvent.query.order_by(StopEvent.start_time.asc())
		for i in mystop:
			bus={}
			if i.reason_level_one is not None:
				bus["r1"]=str(i.reason_level_one)
				bus["reas1"]=get_reas(1,i.reason_level_one)
			else:
				bus["reas1"]=""
				bus["r1"]=""

			if i.reason_level_two:
				bus["r2"]=str(i.reason_level_two)
				bus["reas2"]=get_reas(2,i.reason_level_two)
			else:
				bus["reas2"]=""
				bus["r2"]=""
			if i.reason_level_three:
				bus["r3"]=str(i.reason_level_three)
				bus["reas3"]=get_reas(3,i.reason_level_three)
			else:
				bus["reas3"]=""
				bus["r3"]=""
			if i.reason_level_four:
				bus["r4"]=str(i.reason_level_four)
				bus["reas4"]=get_reas(4,i.reason_level_four)
			else:
				bus["reas4"]=""
				bus["r4"]=""
			if i.breakdown ==1:
				bus["r5"]=str(i.breakdown)
			else:
				bus["r5"]=None			
			if i.comment is not None:
				bus["comment"]=i.comment
			else:
				bus["comment"]=""	
				
			bus["sid"]=i.sid
			data.append(bus)
		t=data										

	return jsonify({'message':t})


@app.route('/modstop',methods=['GET','POST'])
@login_required
def modstop():
	if not current_user.is_authenticated:
		return redirect('/login')

	action=request.args.get("action")
	t="Not done"
	if action=="DELETE_STOP":
		sid=int(request.args.get('sid'))
		db.session.query(StopEvent).filter(StopEvent.sid==sid).delete()
		db.session.commit()
		t="deleted"
	if action=="UPDATE_STOP":
		data=json.loads(request.args.get("data"))
		#return jsonify({'message':str(data['r1'])+'***'+str(data['r2'])+'***'+str(data['r3'])+'***'+str(data['r4'])+'***'+
			#str(data['r5'])+'***'+str(data['comment'])})
		for i in data:
			if not i:
				i=None

		db.session.query(StopEvent).filter(StopEvent.sid==data["sid"]).update({
			'reason_level_one':data['r1'],
			'reason_level_two':data['r2'],
			'reason_level_three':data['r3'],
			'reason_level_four':data['r4'],
			'breakdown':int(data['r5']),
			'comment':data['comment']

			})	
		db.session.commit()
		t="updated"

	if action=="MERGE_STOP":
		data=json.loads(request.args.get("data"))
		S1=StopEvent.query.filter_by(sid=data["stop1"]).first()
		S2=StopEvent.query.filter_by(sid=data["stop2"]).first()
		t='merge unsuccessful!'


		##assign the ealier start time to lower variable while the later time to higher variable
		X1=datetime.strptime(str(S1.start_time), "%Y-%m-%d %H:%M:%S.%f")
		X2=datetime.strptime(str(S2.start_time), "%Y-%m-%d %H:%M:%S.%f")
		Y1=datetime.strptime(str(S1.end_time), "%Y-%m-%d %H:%M:%S.%f")
		Y2=datetime.strptime(str(S2.end_time), "%Y-%m-%d %H:%M:%S.%f")
		if X1 < X2: #X1 happened before X2 therefore give it the endtime of X2
			#delete all stops on the machine whose time falls between the two stops
			db.session.query(StopEvent).filter(StopEvent.machine==S1.machine,(StopEvent.start_time>X1)&(StopEvent.end_time<X2)).delete()
			

			#give X1 the ENDTIME of X2
			StopEvent.query.filter_by(sid=data["stop1"]).update({'start_time':S2.start_time})

			#delete X2
			StopEvent.query.filter_by(sid=data["stop2"]).delete()
			db.session.commit()

			t='ekele'

		elif X1>X2: #X1 happened AFTER X2 therefore give its starttime to X2	
			##delete all stops on the machine whose time falls between the two stops
			db.session.query(StopEvent).filter(StopEvent.machine==S1.machine,(StopEvent.start_time>X2)&(StopEvent.end_time<X1)).delete()
			
			#give X2 the STARTTIME of X1
			StopEvent.query.filter_by(sid=data["stop2"]).update({'end_time':S1.end_time})

			#delete X1
			StopEvent.query.filter_by(sid=data["stop1"]).delete()
			db.session.commit()

			#t=str(S1.start_time)+'  mma mma  ' + str(S2.start_time)
			t='mma mma'


	return jsonify({'message':t})

@app.route('/insertstopevent',methods=['GET','POST'])
@login_required	
def insertstopevent():
	if not current_user.is_authenticated:
		return redirect('/login')

	data=json.loads(request.args.get('data'))
	startformat=format_datetime_prime(data['start'])
	endformat=format_datetime_prime(data['end'])
	t=datetime.strptime(str(endformat), "%Y-%m-%d %H:%M:%S.%f")
	insertstop(data['machine'],startformat,endformat,data)
	
	return jsonify({'status':1,'message':'success!'})

@app.route('/testpage',methods=['GET','POST'])
@login_required
def testpage():

	reasonsOne=[{'r':'Specify in comment','p':14,'tag':1},
	{'r':'Specify in comment','p':16,'tag':1},
	{'r':'Specify in comment','p':18,'tag':1},
	{'r':'Specify in comment','p':19,'tag':1},
	{'r':'Powder caking in triverter','p':20,'tag':1},
	{'r':'Specify in comment','p':21,'tag':1},
	{'r':'Specify in comment','p':22,'tag':1},
	{'r':'Powder build-up on product level sensor','p':23,'tag':1},{'r':'Defective product level sensor','p':23,'tag':1},
	{'r':'Broken flapper','p':24,'tag':1},
	{'r':'Pneumatic failure','p':25,'tag':1},
	{'r':'Slant angle of motor/counter-weight setting not at centerline','p':26,'tag':1},{'r':'No power supply to motor','p':26,'tag':1},{'r':'Loose fasteners on motor','p':26,'tag':1},{'r':'Burnt/Loose terminals on motor','p':26,'tag':1},
	{'r':'Specify in comment','p':27,'tag':1},
	{'r':'Incorrect mesh angle- wrong mesh installed','p':28,'tag':1},{'r':'Incorrect mesh angle- loose mesh tensioner','p':28,'tag':1},{'r':'Clogged mesh- lumpy powder','p':28,'tag':1},{'r':'Clogged mesh- ineffective CIL/RLS','p':28,'tag':1},
	{'r':'Powder build-up on sensor','p':29,'tag':1},{'r':'Broken level sensor','p':29,'tag':1},{'r':'Broken level sensor terminal','p':29,'tag':1},
	{'r':'Incorrect chute distance from mesh','p':30,'tag':1},{'r':'Blocked oversize bin duct- ineffective RLS','p':30,'tag':1},
	{'r':'Blocked oversize bin duct- Unacceptable powder moisture','p':31,'tag':1},
	{'r':'Loose/Broken diverter plate','p':32,'tag':1},
	{'r':'Torn chute','p':33,'tag':1},
	{'r':'Compressor/Generator- Specify in comment','p':36,'tag':1},
	{'r':'Sewing head','p':48,'tag':1},{'r':'Infeed unit','p':48,'tag':1},{'r':'Conveyors','p':48,'tag':1},
	{'r':'Duct cleaning','p':50,'tag':1},{'r':'Drive system- Belt replacement','p':50,'tag':1},
	{'r':'State EO details in comment','p':58,'tag':1},
	{'r':'Sewing head','p':74,'tag':1},{'r':'Infeed unit','p':74,'tag':1},{'r':'Conveyors','p':74,'tag':1},
	{'r':'State SKU in comment','p':78,'tag':1},
	{'r':'State SKU in comment','p':79,'tag':1},
	{'r':'Specify in comment','p':80,'tag':1},
	{'r':'Specify in comment','p':81,'tag':1},
	{'r':'Specify in comment','p':82,'tag':1},
	{'r':'Specify in comment','p':83,'tag':1},
	{'r':'Specify in comment','p':84,'tag':1},
	{'r':'Specify in comment','p':95,'tag':1},
	{'r':'Specify in comment','p':86,'tag':1},
	{'r':'Specify in comment','p':87,'tag':1},
	{'r':'Specify in comment','p':88,'tag':1},
	{'r':'Specify in comment','p':89,'tag':1},
	{'r':'Specify in comment','p':90,'tag':1},
	{'r':'Specify in comment','p':91,'tag':1},
	{'r':'Specify in comment','p':92,'tag':1},
	{'r':'Specify in comment','p':93,'tag':1},
	{'r':'Damaged VFD','p':94,'tag':1},{'r':'Damaged motor','p':94,'tag':1},{'r':'Damaged gearbox','p':94,'tag':1},
	{'r':'Wrong coder roller positioning- wrong CL','p':96,'tag':1},{'r':'Worn roller surface','p':96,'tag':1},{'r':'Worn rack-and-pinion teeth','p':96,'tag':1},{'r':'Stiff bearings','p':96,'tag':1},
	{'r':'Worn roller surface','p':95,'tag':1},{'r':'Stiff bearings','p':95,'tag':1},
	{'r':'Wrong photocell roller positioning- wrong CL','p':97,'tag':1},{'r':'Worn roller surface','p':97,'tag':1},{'r':'Worn rack-and-pinion teeth','p':97,'tag':1},{'r':'Stiff bearings','p':97,'tag':1},
	{'r':'Wrong infeed roller positioning- wrong CL','p':98,'tag':1},{'r':'Worn roller surface','p':98,'tag':1},
	{'r':'Misaligned forming shoulder','p':99,'tag':1},{'r':'Dented forming shoulder','p':99,'tag':1},
	{'r':'Damaged dancing bar sensor- specify in comment','p':100,'tag':1},
	{'r':'Worn dancing bar shaft','p':101,'tag':1},{'r':'Worn dancing bar bearing','p':101,'tag':1},{'r':'Loose dancing bar sensor','p':101,'tag':1},{'r':'Damaged seal on dancing bar cylinder','p':101,'tag':1},
	{'r':'Vertical jaw cylinder damaged','p':102,'tag':1},{'r':'Vertical jaw block misaligned/loose','p':102,'tag':1},{'r':'Vertical jaw assy misaligned/too near/distant','p':102,'tag':1},{'r':'Vertical cooling bar misaligned','p':102,'tag':1},
	{'r':'Low resistance on thermocouple','p':103,'tag':1},{'r':'Loose thermocouple terminal','p':103,'tag':1},{'r':'Broken thermocouple cable','p':103,'tag':1},
	{'r':'PID controller issues','p':104,'tag':1},{'r':'Low resistance on heating element','p':104,'tag':1},{'r':'Loose heating element terminal','p':104,'tag':1},{'r':'Broken heating element cable','p':104,'tag':1},
	{'r':'Damaged contactor','p':105,'tag':1},
	{'r':'Loose/Burnt pullbelt motor terminals','p':106,'tag':1},
	{'r':'Worn pullbelt shaft/hub','p':107,'tag':1},{'r':'Misaligned pulleys','p':107,'tag':1},
	{'r':'Wrong pullbelt traction input','p':108,'tag':1},{'r':'Wrong pullbelt tension','p':108,'tag':1},{'r':'Wrong pullbelt pressure','p':108,'tag':1},{'r':'Worn/Missing side teflon on forming set','p':108,'tag':1},{'r':'Worn/Grooved pullbelt surface','p':108,'tag':1},{'r':'Loose pulley fasteners','p':108,'tag':1},{'r':'Broken pullbelt','p':108,'tag':1},
	{'r':'Photocell lost calibration','p':109,'tag':1},{'r':'No signal from photocell','p':109,'tag':1},{'r':'Manufacturer splice','p':109,'tag':1},
	{'r':'Damaged tension sensors','p':110,'tag':1},
	{'r':'Worn/Misaligned rollers','p':111,'tag':1},{'r':'Broken ribbon- operational error(wrong webbing)','p':111,'tag':1},{'r':'Broken ribbon- defective ribbon','p':111,'tag':1},
	{'r':'Restriction on printhead solenoid','p':112,'tag':1},
	{'r':'Worn printhead','p':113,'tag':1},{'r':'Loose/Broken printhead flex connection','p':113,'tag':1},
	{'r':'No power supply to board','p':114,'tag':1},{'r':'Blown fuse on power supply unit','p':114,'tag':1},
	{'r':'Main board not calibrating','p':115,'tag':1},{'r':'Broken flex connector on board','p':115,'tag':1},
	{'r':'Loose/Worn hub','p':116,'tag':1},
	{'r':'Wrong coder roller positioning- wrong CL','p':117,'tag':1},{'r':'Worn roller surface','p':117,'tag':1},{'r':'Stiff roller bearings','p':117,'tag':1},
	{'r':'Restriction on splines- product build-up','p':118,'tag':1},{'r':'Misaligned splines','p':118,'tag':1},
	{'r':'Stuck gears- lack of lubrication','p':119,'tag':1},
	{'r':'Reversed motor cabling-direction','p':120,'tag':1},{'r':'No power supply to motor','p':120,'tag':1},{'r':'Burnt motor coil','p':120,'tag':1},
	{'r':'Low resistance on thermocouple','p':121,'tag':1},{'r':'Loose thermocouple terminal','p':121,'tag':1},{'r':'Broken thermocouple cable','p':121,'tag':1},
	{'r':'Low resistance on heating element','p':122,'tag':1},{'r':'Loose heating element terminal','p':122,'tag':1},{'r':'Broken heating element cable','p':122,'tag':1},
	{'r':'Worn pullet hole','p':123,'tag':1},{'r':'No power supply to main drive motor','p':123,'tag':1},{'r':'Loose tension on drive belt','p':123,'tag':1},{'r':'Burnt motor coil','p':123,'tag':1},{'r':'Broken V-belt teeth','p':123,'tag':1},
	{'r':'Worn hole on linkages','p':124,'tag':1},{'r':'Broken linear bearings','p':124,'tag':1},{'r':'Broken HK1616 bearings','p':124,'tag':1},
	{'r':'Broken cam follower bolt','p':125,'tag':1},{'r':'Broken cam follower bearing','p':125,'tag':1},
	{'r':'Solenoid coil not getting signal','p':126,'tag':1},{'r':'Solenoid coil not actuating','p':126,'tag':1},{'r':'Expanded hole on main cylinder flange','p':126,'tag':1},{'r':'Broken spherical bearing','p':126,'tag':1},
	{'r':'Worn teeth on horizontal jaw block','p':127,'tag':1},{'r':'Servo motor timimg belts loosed','p':127,'tag':1},{'r':'Servo motor timing belts damaged','p':127,'tag':1},{'r':'Loose fastener on horizontal jaw block holder','p':127,'tag':1},{'r':'Horizontal jaw block misalligned','p':127,'tag':1},{'r':'Defective servo drive','p':127,'tag':1},{'r':'Build-up on horizontal jaw block','p':127,'tag':1},{'r':'Broken fastener on horizontal jaw block holder','p':127,'tag':1},
	{'r':'Low resistance on thermocouple','p':128,'tag':1},{'r':'Loose thermocouple terminal','p':128,'tag':1},{'r':'Broken thermocouple cable','p':128,'tag':1},
	{'r':'Low resistance on heating element','p':129,'tag':1},{'r':'Loose heating element terminal','p':129,'tag':1},{'r':'Broken heating element cable','p':129,'tag':1},
	{'r':'Damaged contactor','p':130,'tag':1},
	{'r':'Powder build-up on bag pressers','p':131,'tag':1},{'r':'Missing bag presser- Rear jaw','p':131,'tag':1},{'r':'Missing bag presser- Front jaw','p':131,'tag':1},{'r':'Damaged bag presser plate','p':131,'tag':1},{'r':'Broken fasteners on bag pressers','p':131,'tag':1},
	{'r':'Powder caking in triverter','p':132,'tag':1},{'r':'Powder build-up on product level sensor','p':132,'tag':1},{'r':'Pneumatic failure- specify in comment','p':132,'tag':1},{'r':'Other- specify in comment','p':132,'tag':1},{'r':'Electrical failure- specify in comment','p':132,'tag':1},{'r':'Defective product level sensor','p':132,'tag':1},{'r':'Broken flapper','p':132,'tag':1},
	{'r':'Loose servo motor power cables','p':133,'tag':1},{'r':'Loose servo motor control cables','p':133,'tag':1},{'r':'Loose mounting fasteners on motor','p':133,'tag':1},{'r':'Encoder failure','p':133,'tag':1},
	{'r':'Cake formation in funnel- powder quality','p':134,'tag':1},{'r':'Cake formation in funnel- Ineffective RLS','p':134,'tag':1},
	{'r':'Wrong turnset input','p':135,'tag':1},{'r':'Servo controller drive fault- Under/over voltage error','p':135,'tag':1},{'r':'Servo controller drive fault- Restriction','p':135,'tag':1},{'r':'Servo controller drive fault- Position loss','p':135,'tag':1},{'r':'Servo controller drive fault- Internal servo controller fault','p':135,'tag':1},{'r':'Loose terminal from PLC port','p':135,'tag':1},
	{'r':'Misaligned auger screw','p':136,'tag':1},{'r':'Loose auger screw','p':136,'tag':1},{'r':'Bent/Broken auger screw','p':136,'tag':1},
	{'r':'No supply from solenoid valve- damaged solenoid','p':137,'tag':1},{'r':'No signal to solenoid coil','p':137,'tag':1},
	{'r':'Worn knife blocker','p':138,'tag':1},
	{'r':'Worn knife teeth','p':139,'tag':1},{'r':'Worn knife holder bolt','p':139,'tag':1},
	{'r':'Ruptured/broken tubings','p':140,'tag':1},{'r':'Damaged cylinder seal','p':140,'tag':1},
	{'r':'Blocked tube- ineffective RLS','p':141,'tag':1},{'r':'Blocked tube- low suction','p':141,'tag':1},
	{'r':'Wrong spreader finger length/distance','p':142,'tag':1},{'r':'Missing/Bent spreader finger','p':142,'tag':1},
	{'r':'Wrongly installed FS Insert','p':143,'tag':1},{'r':'Contamination on formingset wall','p':143,'tag':1},
	{'r':'Specify in comment','p':144,'tag':1},
	{'r':'Contractor indiscipline','p':149,'tag':1},
	{'r':'Coordinator does not provide back-up for incomplete staffing','p':150,'tag':1},{'r':'Communication gap between line leader and coordinator','p':150,'tag':1},
	{'r':'Contractor indiscipline','p':151,'tag':1},
	{'r':'Specify in comment','p':152,'tag':1},
	{'r':'Build-up under belt','p':154,'tag':1},
	{'r':'Specify in comment','p':155,'tag':1},
	{'r':'No power supply to motor','p':156,'tag':1},{'r':'Loose/Burnt motor terminals','p':156,'tag':1},
	{'r':'Worn shaft','p':157,'tag':1},
	{'r':'Worn bearing inner/outer race','p':158,'tag':1},
	{'r':'Worn bearing inner/outer race','p':159,'tag':1},
	{'r':'Misaligned belt','p':160,'tag':1},{'r':'Low tension on belt','p':160,'tag':1},{'r':'Broken main conveyor belt','p':160,'tag':1},
	{'r':'Build-up on sensor','p':161,'tag':1},
	{'r':'Restriction from dirt/contamination on rollers','p':162,'tag':1},{'r':'No power supply to motor','p':162,'tag':1},{'r':'Misalligned/Broken drive chain','p':162,'tag':1},{'r':'Loose/Burnt motor terminals','p':162,'tag':1},{'r':'Broken/Worn rollers','p':162,'tag':1},
	{'r':'Specify in comment','p':163,'tag':1},
	{'r':'VFD not activating motors','p':164,'tag':1},{'r':'Tension button not responding','p':164,'tag':1},{'r':'No signal from pallet sensor','p':164,'tag':1},{'r':'No signal from carriage level sensor','p':164,'tag':1},{'r':'No power supply to VFD','p':164,'tag':1},{'r':'Main board not sending signal','p':164,'tag':1},{'r':'Low sensitivity on pallet sensor','p':164,'tag':1},{'r':'HMI board malfunction','p':164,'tag':1},
	{'r':'Uncallibrated potentiometer','p':165,'tag':1},{'r':'SW film OOS- Not stretchy enough','p':165,'tag':1},{'r':'Safety guard circuit malfunction','p':165,'tag':1},{'r':'Photoeye not detecting pallet','p':165,'tag':1},{'r':'No power supply to motor','p':165,'tag':1},{'r':'Loose/Missing motor fasteners','p':165,'tag':1},{'r':'Loose/Burnt motor terminals','p':165,'tag':1},{'r':'ineffective level sensors','p':165,'tag':1},{'r':'Inappropriate (Low/High) roller speed','p':165,'tag':1},{'r':'Damaged gearbox','p':165,'tag':1},{'r':'Carriage belt overload','p':165,'tag':1},{'r':'Broken SW film web','p':165,'tag':1},{'r':'Broken carriage belt','p':165,'tag':1},
	{'r':'Specify in comment','p':166,'tag':1},{'r':'Ineffective pump','p':166,'tag':1},{'r':'Incorrect viscosity','p':166,'tag':1},
	{'r':'Specify in comment','p':167,'tag':1},{'r':'Gutter blockage','p':167,'tag':1},{'r':'Drop-off point not okay','p':167,'tag':1},
	{'r':'Specify in comment','p':168,'tag':1},{'r':'No power supply to board','p':168,'tag':1},{'r':'Damaged main Imaje board','p':168,'tag':1},
	{'r':'No signal from sensor','p':169,'tag':1},{'r':'No power supply to sensor','p':169,'tag':1},{'r':'Low sensitivity','p':169,'tag':1},{'r':'Wrong sensor positioning','p':169,'tag':1},
	{'r':'Touch screen not responding','p':170,'tag':1},
	{'r':'Blockage in printhead','p':171,'tag':1},
	{'r':'Specify in comment','p':176,'tag':1},
	{'r':'Make-up cartridge mismatch with ITM','p':172,'tag':1},
	{'r':'Defective ITM','p':173,'tag':1},
	{'r':'Ink cartridge mismatch with ITM','p':174,'tag':1},
	{'r':'No signal from sensor','p':175,'tag':1},{'r':'No power supply to sensor','p':175,'tag':1},{'r':'Low sensitivity','p':175,'tag':1},{'r':'Wrong sensor positioning','p':175,'tag':1},
	{'r':'Specify in comment','p':177,'tag':1},
	{'r':'Power plug not connected','p':178,'tag':1},{'r':'Defective weighing scale','p':178,'tag':1},{'r':'Burnt fuse on plug','p':178,'tag':1},
	{'r':'Scale not calibrated','p':179,'tag':1},{'r':'False reading from scale','p':179,'tag':1},
	{'r':'Specify in comment','p':180,'tag':1},
	{'r':'Specify in comment','p':181,'tag':1},{'r':'Broken thread','p':181,'tag':1},
	{'r':'Thread contamination on pulleys','p':182,'tag':1},{'r':'Specify in comment','p':182,'tag':1},{'r':'Burt motor terminals','p':182,'tag':1},{'r':'Broken belt','p':182,'tag':1},{'r':'No power supply to sewing head motor','p':182,'tag':1},
	{'r':'Stiff conveyor bearing','p':183,'tag':1},{'r':'Specify in comment','p':183,'tag':1},{'r':'No power supply to conveyor motor','p':183,'tag':1},{'r':'Low tension on conveyor belt','p':183,'tag':1},{'r':'Loose/Burnt conveyor motor terminals','p':183,'tag':1},
	{'r':'Specify in comment','p':184,'tag':1},
	{'r':'Specify in comment','p':185,'tag':1},{'r':'Broken needle','p':185,'tag':1},
	{'r':'Wrong operation- contractor did not feed polywoven properly','p':186,'tag':1},{'r':'Wrong connection on infeed motor','p':186,'tag':1},{'r':'Worn universal coupline shaft/housing','p':186,'tag':1},{'r':'Thread accumulation on pulleys/bearing','p':186,'tag':1},{'r':'Stiff needle bearing','p':186,'tag':1},{'r':'Specify in comment','p':186,'tag':1},{'r':'Loose/Burnt motor terminals','p':186,'tag':1},{'r':'Loose tension on infeed belt','p':186,'tag':1},{'r':'Broken belt','p':186,'tag':1},
	{'r':'Specify in comment','p':187,'tag':1},
	{'r':'Disconnected wires','p':190,'tag':1},
	{'r':'No voltage','p':191,'tag':1},
	{'r':'Damaged component- specify in comment','p':192,'tag':1},
	{'r':'Damaged transformer','p':193,'tag':1},
	{'r':'HMI not responding','p':194,'tag':1},
	{'r':'Communication loss','p':189,'tag':1},{'r':'Damaged component- specify in comment','p':188,'tag':1},
	{'r':'Damaged component- specify in comment','p':189,'tag':1},
	{'r':'Motor overload trip','p':197,'tag':1},{'r':'SDS switched off','p':197,'tag':1},{'r':'SDS defective','p':197,'tag':1},{'r':'Incomplete phase voltage','p':197,'tag':1},{'r':'Burnt motor winding','p':197,'tag':1},{'r':'Burnt motor terminal','p':197,'tag':1},
	{'r':'Specify in comment','p':202,'tag':1},
	{'r':'Specify in comment','p':212,'tag':1},
	{'r':'Worn key-way in gearbox','p':213,'tag':1},{'r':'Worn key','p':213,'tag':1},
	{'r':'No power supply to motor','p':214,'tag':1},{'r':'Loose/Burnt motor terminal','p':214,'tag':1},{'r':'Excessive temperation on motor','p':214,'tag':1},
	{'r':'Restriction from weight of product accumulation','p':215,'tag':1},{'r':'Low tension on inclined conveyor belt','p':215,'tag':1},{'r':'Inclined coneyor belt mistrack','p':215,'tag':1},{'r':'Broken/Loose drive chain','p':215,'tag':1},{'r':'Ruptured inclined conveyor belt','p':215,'tag':1},
	{'r':'Worn bearing inner/outer race','p':216,'tag':1},
	{'r':'Worn shaft/roller','p':217,'tag':1},
	{'r':'Worn bearing inner/outer race','p':218,'tag':1},
	{'r':'Worn shaft/roller','p':219,'tag':1},
	{'r':'Worn sprocket','p':256,'tag':1},
	{'r':'Specify in comment','p':220,'tag':1},
	{'r':'Worn key-way in gearbox','p':221,'tag':1},{'r':'Worn key','p':221,'tag':1},
	{'r':'No power supply to motor','p':222,'tag':1},{'r':'Loose/Burnt motor terminal','p':222,'tag':1},{'r':'Excessive temperation on motor','p':222,'tag':1},
	{'r':'Restriction from weight of product accumulation','p':223,'tag':1},{'r':'Low tension on inclined conveyor belt','p':223,'tag':1},{'r':'Inclined coneyor belt mistrack','p':223,'tag':1},{'r':'Broken/Loose drive chain','p':223,'tag':1},{'r':'Ruptured inclined conveyor belt','p':223,'tag':1},
	{'r':'Worn bearing inner/outer race','p':224,'tag':1},
	{'r':'Worn shaft/roller','p':225,'tag':1},
	{'r':'Worn bearing inner/outer race','p':226,'tag':1},
	{'r':'Worn shaft/roller','p':227,'tag':1},
	{'r':'Specify in comment','p':228,'tag':1},
	{'r':'Worn key-way in gearbox','p':229,'tag':1},{'r':'Worn key','p':229,'tag':1},
	{'r':'No power supply to motor','p':230,'tag':1},{'r':'Loose/Burnt motor terminal','p':230,'tag':1},{'r':'Excessive temperation on motor','p':230,'tag':1},
	{'r':'Restriction from weight of product accumulation','p':231,'tag':1},{'r':'Low tension on inclined conveyor belt','p':231,'tag':1},{'r':'Inclined coneyor belt mistrack','p':231,'tag':1},{'r':'Broken/Loose drive chain','p':231,'tag':1},{'r':'Ruptured inclined conveyor belt','p':231,'tag':1},
	{'r':'Worn bearing inner/outer race','p':232,'tag':1},
	{'r':'Worn shaft/roller','p':233,'tag':1},
	{'r':'Worn bearing inner/outer race','p':234,'tag':1},
	{'r':'Worn shaft/roller','p':235,'tag':1},
	{'r':'Worn sprocket','p':236,'tag':1},
	{'r':'Specify in comment','p':237,'tag':1},
	{'r':'Worn key-way in gearbox','p':238,'tag':1},{'r':'Worn key','p':238,'tag':1},
	{'r':'No power supply to motor','p':239,'tag':1},{'r':'Loose/Burnt motor terminal','p':239,'tag':1},{'r':'Excessive temperation on motor','p':239,'tag':1},
	{'r':'Restriction from weight of product accumulation','p':240,'tag':1},{'r':'Low tension on inclined conveyor belt','p':240,'tag':1},{'r':'Inclined coneyor belt mistrack','p':240,'tag':1},{'r':'Broken/Loose drive chain','p':240,'tag':1},{'r':'Ruptured inclined conveyor belt','p':240,'tag':1},
	{'r':'Worn bearing inner/outer race','p':241,'tag':1},
	{'r':'Worn shaft/roller','p':242,'tag':1},
	{'r':'Worn bearing inner/outer race','p':243,'tag':1},
	{'r':'Worn shaft/roller','p':244,'tag':1},
	{'r':'Emergency button pressed','p':245,'tag':1},{'r':'Defective E-stop','p':245,'tag':1},{'r':'Broken E-stop terminal','p':245,'tag':1},
	{'r':'Specify in comment','p':249,'tag':1},{'r':'2D NO READ (specify in comment)','p':249,'tag':1},{'r':'2D NO MATCH (specify in comment)','p':249,'tag':1},
	{'r':'Blocked buggy hopper','p':255,'tag':1},
	{'r':'Contractor indiscipline','p':251,'tag':1},
	{'r':'Powder OOS from making','p':252,'tag':1},{'r':'MSG not prodcing (issue on MSG line)','p':252,'tag':1},{'r':'Delay in quality check','p':252,'tag':1},
	{'r':'Restriction in buggy movement (Ditches on the floor)','p':253,'tag':1},{'r':'Restriction in buggy movement (defective buggy tyres)','p':253,'tag':1},{'r':'Low level indicator does not come up','p':253,'tag':1},{'r':'Contractor indiscipline','p':253,'tag':1},{'r':'Buggy PC not working (Buggy card not available)','p':253,'tag':1},{'r':'Buggy operators not complete','p':253,'tag':1},{'r':'BFS dump push button not working','p':253,'tag':1},{'r':'BFS density scale not working','p':253,'tag':1}]
	
	#reasontwo=[{'r':'Sprocket','p':46,'tag':0}]

		
	for i in reasonsOne:
		log=ReasonFour()
		log.reason=i['r']
		log.reason_tri=i['p']
		log.end_tag=i["tag"]
		#db.session.add(log)	
		#db.session.commit()

	#count=18
	#for i in reasonsOne:
		#if count<36:
	#ReasonTri.query.filter_by(trid=173).update({'reason':'ITM'})
	#db.session.commit()
			#count=count+1
	ERROR = [{'cause':'operator stop', 'code':1000},{'cause':'Power supply switched off', 'code':1001},
	{'cause':'Emergency stop', 'code':1002},{'cause':'Sealsystem changed', 'code':1003},
	{'cause':'No air pressure', 'code':1004},{'cause':'Door opened', 'code':1005},
	{'cause':'Main motor / invertor drive', 'code':1006},{'cause':'Jaw protection', 'code':1007},
	{'cause':'Encoder / counter error', 'code':1008},{'cause':'Film motor / invertor drive', 'code':1009},
	{'cause':'Pulse unit longseal', 'code':1010},{'cause':'Pulse unit (upper) jaw', 'code':1011},
	{'cause':'Pulse unit (lower) jaw', 'code':1012},{'cause':'Error cooling system', 'code':1013},
	{'cause':'ERROR', 'code':1014},{'cause':'Error cooling system . no flow', 'code':1015},
	{'cause':'Overload conveyor motor', 'code':1016},{'cause':'ERROR', 'code':1017},
	{'cause':'Speed out of limits', 'code':1018},{'cause':'Conveyor disconnected', 'code':1019},
	{'cause':'Emergency stop Conveyor', 'code':1020},{'cause':'ERROR', 'code':1021},
	{'cause':'Auto film sensor faulted', 'code':1022},{'cause':'Film reel positioning', 'code':1023},
	{'cause':'Basic module ~-----~ PLC error', 'code':1024},{'cause':'Longseal arm', 'code':1025},
	{'cause':'Photocell', 'code':1026},{'cause':'Servo motor alarm', 'code':1027},
	{'cause':'Downstream line alarm', 'code':1028},{'cause':'Printer stop', 'code':1029},
	{'cause':'End of film', 'code':1030},{'cause':'No filmfeed possible', 'code':1031},
	{'cause':'Bagcounter reached maximum', 'code':1032},{'cause':'Temperature out of range longseal', 'code':1033},
	{'cause':'Temperature out of range Crosseal front', 'code':1034},{'cause':'Temperature out of range Crosseal rear', 'code':1035},
	{'cause':'ERROR', 'code':1036},{'cause':'Buggy floor no change', 'code':1037},
	{'cause':'Powerfill , main motor / drive', 'code':1038},{'cause':'Powerfill , adjustment motor', 'code':1039},
	{'cause':'Powerfill , index prox not found', 'code':1040},{'cause':'No POWDER in machine', 'code':1041},
	{'cause':'Downstream not ready', 'code':1042},{'cause':'Waiting for sync signal', 'code':1042},
	{'cause':'Film (reel) not in position', 'code':1044},{'cause':'ERROR', 'code':1045},
	{'cause':'Droptime limited to 250 percent cycle', 'code':1046},{'cause':'Process out of center line: BFM', 'code':1047},
	{'cause':'Double stroke not allowed', 'code':1048},{'cause':'Downstream line not ready', 'code':1049},
	{'cause':'Powerfill volume on maximum', 'code':1050},{'cause':'Powerfill volume on minimum', 'code':1051},
	{'cause':'Film feed limiteed warrning', 'code':1052},{'cause':'Longseal time limited to maximum', 'code':1053},
	{'cause':'Crosseal time limited to maximum', 'code':1054},{'cause':'Production', 'code':1058},
	{'cause':'Process out: Longseal time', 'code':1064},{'cause':'Process out of centreline:SPEED', 'code':1066},
	{'cause':'No Match 2D error', 'code':1072},{'cause':'No read 2D error', 'code':1073},
	{'cause':'Operator Stop', 'code':1074}]

	for x in ERROR:

		newEvent=StopCode()				
		newEvent.cause = x['cause'].title()
		newEvent.cause_code = x['code']
		
		#db.session.add(newEvent)
		#db.session.commit()

	#db.session.query(ReasonOne).filter(ReasonOne.rid==8).update({'reason':'Blank'})
	#db.session.commit()
		

	myevent=ReasonOne.query.order_by(ReasonOne.rid.desc()).all()

	
	

	return render_template('public/test_page.html', stop=myevent)	


@app.route('/updatenew',methods=['GET','POST'])
@login_required
def updatenew():

	mach=["R","S","T","U","V","W","I","J","K","L","M","N"]
	s={}
	for i in mach:
		myevent=StopEvent.query.filter_by(machine=i).order_by(StopEvent.start_time.desc()).first()
		if myevent.status==0:
			s[i]="stopped"
			s[i+'error']=get_error(myevent.error)
		else:
			s[i]="running"
			s[i+'error']=''
	

	##troubleshoot plc comm#
	
	heads = ["143.28.88.14"]
	#for x in heads:
		#stop_tag=["L1.Running","L2.Running","L3.Running"] #tags for m/c stop/start
		#cause_tag=["M1.AlarmNum","M2.AlarmNum","M3.AlarmNum"] #tags for stop code
		#with PLC(x) as comm:
			#stop=[comm.Read(g,1) for g in stop_tag]
			#cause=[comm.Read(g,1) for g in cause_tag]

			#s['L'] = stop[0].Value
			#s['Lerror'] = stop[0].Value #cause[0].Value

			#s['M'] = stop[1].Value
			#s['Merror'] = stop[1].Value #cause[1].Value

			#s['N'] = stop[2].Value
			#s['Nerror'] = stop[2].Value #cause[2].Value

			#if x == "143.28.88.67":
				#log_stop(stop[0].Value,cause[0].Value,"E","2")
				#log_stop(stop[1].Value,cause[1].Value,"F","2")
				#log_stop(stop[2].Value,cause[2].Value,"G","2")
				#log_stop(stop[3].Value,cause[3].Value,"H","2")
				
		#time.sleep(1)

		
	return jsonify({'R':s['R'],'r_e':s['Rerror'],'S':s['S'],'s_e':s['Serror'],'T':s['T'],'t_e':s['Terror'],'U':s['U'],'u_e':s['Uerror'],'V':s['V'],'v_e':s['Verror'],'W':s['W'],'w_e':s['Werror'],'I':s['I'],'i_e':s['Ierror'],'J':s['J'],'j_e':s['Jerror'],'K':s['K'],'k_e':s['Kerror'],'L':s['L'],'l_e':s['Lerror'],'M':s['M'],'m_e':s['Merror'],'N':s['N'],'n_e':s['Nerror']})

@app.route('/update',methods=['GET','POST'])
@login_required
def update():

	mach=request.args.get('c')
	myevent=StopEvent.query.filter_by(machine=mach).order_by(StopEvent.start_time.desc())
	t=''
	num=myevent.count()
	count=0
	for i in myevent:
		count=count+1
		if i.end_time is not None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			l=str(i.end_time)
			end=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
			time=end-start
			mytime=divmod(time.total_seconds(), 60)
			downtime=int(mytime[0])
			up=get_uptime(i.sid,start,mach)
			mytime=divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])
			t +=Markup('<p><div style="height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span><strong>Downtime: </strong>'+str(downtime)+' mins.</span><span><strong>End Time: </strong>'+str(format_datetime(i.end_time))+'</span></p><span data-nb-sid="'+str(i.sid)+'" onclick="deleItem(this)"><i class="fa fa-trash-o"></i></span>')
		elif i.end_time is None and count <num:
			f=str(i.start_time)
			start=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
			up=get_uptime(i.sid,start,mach)
			mytime=	divmod(up.total_seconds(), 60)
			uptime=int(mytime[0])
			t +=Markup('<p style="color: green;"><div style="color:green;height:auto;width:60px;"><strong>Cause: </strong>'+get_error(i.error)+'</div><span style="color: green;"><strong>Start Time: </strong>'+str(format_datetime(i.start_time))+'</span><span style="color: green;"><strong>Uptime: </strong>'+str(uptime)+' mins.</span><span style="color: green;">...</span></p>')
		
		
	return jsonify({'status':1, 'message':'data','stop':t})

@app.route('/factorytalk', methods=['POST'])
def talktoplc():
	response = 'Success'
	data = request.get_json()
	with PLC(ctrl_rm) as comm:
		comm.Timeout = 5000
		res = comm.Write('B_Density',data['value'])
		response = res.Status
		comm.Close()

	return json.dumps({'status': response}), 200


def log_msg_event(plc):

	while True:
		heads=plc
		for x in heads:
			stop_tag=["L.Running","L.Running"] #tags for admix and tower
			cause_tag=["M.AlarmNum","M.AlarmNum"] #tags for stop code
			with PLC(x) as comm:
				stop=[comm.Read(g,1) for g in stop_tag]
				cause=[comm.Read(g,1) for g in cause_tag]
				if x == "172.23.47.100":
					log_stop(stop[0].Value,cause[0].Value,"U","4A")
					
				else:
					log_stop(stop[0].Value,cause[0].Value,"R","4A")
					
		time.sleep(1)

	return


def log_4a_event(plc):

	while True:
		heads=plc
		for x in heads:
			stop_tag=["L1.Running","L2.Running","L3.Running"] #tags for m/c stop/start
			cause_tag=["M1.AlarmNum","M2.AlarmNum","M3.AlarmNum"] #tags for stop code
			with PLC(x) as comm:
				stop=[comm.Read(g,1) for g in stop_tag]
				cause=[comm.Read(g,1) for g in cause_tag]
				if x == "143.28.88.6":
					log_stop(stop[0].Value,cause[0].Value,"U","4A")
					log_stop(stop[1].Value,cause[1].Value,"V","4A")
					log_stop(stop[2].Value,cause[2].Value,"W","4A")
				else:
					log_stop(stop[0].Value,cause[0].Value,"R","4A")
					log_stop(stop[1].Value,cause[1].Value,"S","4A")
					log_stop(stop[2].Value,cause[2].Value,"T","4A")
		time.sleep(1)
	return

def log_4b_event(plc):

	while True:
		heads=plc
		for x in heads:
			stop_tag=["L1.Running","L2.Running","L3.Running"] #tags for m/c stop/start
			cause_tag=["M1.AlarmNum","M2.AlarmNum","M3.AlarmNum"] #tags for stop code
			with PLC(x) as comm:
				stop=[comm.Read(g,1) for g in stop_tag]
				cause=[comm.Read(g,1) for g in cause_tag]
				if x == "143.28.88.12":
					log_stop(stop[0].Value,cause[0].Value,"I","4B")
					log_stop(stop[1].Value,cause[1].Value,"J","4B")
					log_stop(stop[2].Value,cause[2].Value,"K","4B")
				else:
					log_stop(stop[0].Value,cause[0].Value,"L","4B")
					log_stop(stop[1].Value,cause[1].Value,"M","4B")
					log_stop(stop[2].Value,cause[2].Value,"N","4B")
		time.sleep(1)
	return

def log_L1_event(plc):

	while True:
		heads=plc
		for x in heads:
			stop_tag=["UVAA_Running","UVAB_Running","UVAC_Running","UVAD_Running"] #tags for m/c stop/start
			cause_tag=["UVAA_AlarmNum","UVAB_AlarmNum","UVAC_AlarmNum","UVAD_AlarmNum"] #tags for stop code
			with PLC(x) as comm:
				stop=[comm.Read(g,1) for g in stop_tag]
				cause=[comm.Read(g,1) for g in cause_tag]
				if x == "143.28.88.67":
					log_stop(stop[0].Value,cause[0].Value,"A","1A")
					log_stop(stop[1].Value,cause[1].Value,"B","1A")
					log_stop(stop[2].Value,cause[2].Value,"C","1B")
					log_stop(stop[3].Value,cause[3].Value,"D","1B")
				
		time.sleep(1)
	return

def log_L2_event(plc):

	while True:
		heads=plc
		for x in heads:
			stop_tag=["UVAE_Running","UVAF_Running","UVAG_Running","UVAH_Running"] #tags for m/c stop/start
			cause_tag=["UVAE_AlarmNum","UVAF_AlarmNum","UVAG_AlarmNum","UVAH_AlarmNum"] #tags for stop code
			with PLC(x) as comm:
				stop=[comm.Read(g,1) for g in stop_tag]
				cause=[comm.Read(g,1) for g in cause_tag]
				if x == "143.28.88.67":
					log_stop(stop[0].Value,cause[0].Value,"E","2")
					log_stop(stop[1].Value,cause[1].Value,"F","2")
					log_stop(stop[2].Value,cause[2].Value,"G","2")
					log_stop(stop[3].Value,cause[3].Value,"H","2")
				
		time.sleep(1)
	return

def log_stop(status,cause_code,machine,line):
	query=db.session.query(StopEvent).filter(StopEvent.machine==machine).order_by(StopEvent.sid.desc()).first()
	
	if query is not None:

		if query.status==0 and status==True:
			#update event
			db.session.query(StopEvent).filter(StopEvent.sid==query.sid).update({'end_time':datetime.now(),'status':1})
			db.session.commit()
		elif query.status==1 and status==False:
			#log event
			newEvent=StopEvent()				
			newEvent.start_time=datetime.now()
			newEvent.machine=machine
			if line=="4B" and cause_code==85:
				cause_code=0
			elif line == "1A" or line == "1B" or line == "2":
				cause_code = 1000+int(cause_code)

			newEvent.error=cause_code
			db.session.add(newEvent)
			db.session.commit()
		else:
			pass

	elif line!='4A' and line!='4B':

		if status == False:
			dat="1989-04-17 07:00:00.0001"
			end=datetime.strptime(str(dat), "%Y-%m-%d %H:%M:%S.%f")

			newEvent=StopEvent()				
			newEvent.start_time=end #datetime.now()
			newEvent.machine=machine
			if line=="4B" and cause_code==85:
				cause_code=0
			elif line == "1A" or line == "1B" or line == "2":
				cause_code = 1000+int(cause_code)

			newEvent.error=cause_code
			db.session.add(newEvent)
			db.session.commit()
		else:
			pass


	
	return 

p1 = Thread(target=log_4a_event, args=(PLC_4A,))
p1.start()
p2 = Thread(target=log_4b_event, args=(PLC_4B,))
p2.start()
p3 = Thread(target=log_L1_event, args=(PLC_L1,))
p3.start()
p4 = Thread(target=log_L2_event, args=(PLC_L2,))
p4.start()
