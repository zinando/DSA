from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from pylogix import PLC
from datetime import datetime,timedelta
from threading import Thread
#from ugeeapp import app,db
#from ugeeapp.models import StopsEvent



PLC_4A = ["143.28.88.6","143.28.88.3"]
PLC_4B = ["143.28.88.12","143.28.88.14"]
PLC_L1 = ["143.28.88.67"]
PLC_L2 = ["143.28.88.67"]



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
			stop_tag=["UVAA_Running","UVAB_Running","UVAC_Running","UVAD_Running"] #tags for m/c stop/start
			cause_tag=["UVAA_AlarmNum","UVAB_AlarmNum","UVAC_AlarmNum","UVAD_AlarmNum"] #tags for stop code
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