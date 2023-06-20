from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,StopCode,ReasonOne,SKU,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
import time
import json
import datetime
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib
from ugeeapp.appclasses.stopsclass import STOPSEVENT 
from operator import itemgetter



class PRODUCTION:

	def __init__(self):
		pass

	def log_production_data(self,data,case_status):

		news=STOPSEVENT()
		error=[]
		eke=[]
		ddt=''
		cas=''
		if case_status == 0:
			##there is no case, add production data#
			for man in data['machines']:
				##delete all production data of this sku on the machine for the shift#				
				prodate = news.get_date_from_datetime(data['start'])['date']
				#kt=datetime.strptime(str(prodate), "%Y-%m-%d")
				check = db.session.query(Production).filter(Production.mcode==man,Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).count()
				if check >0:
					db.session.query(Production).filter(Production.line==data['line'],Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).delete()
					db.session.commit()

				###check if machine has parameters for the sku#
				if self.check_param(man,data['product']):

					##get product parameters for the sku#
					params = self.fetch_params(man,data['product'])
					##now log production data for the machine#
					log = Production()
					log.prodate = datetime.strptime(str(prodate), "%Y-%m-%d")
					log.product_code =data['product']
					log.mcode=man
					log.product_params= json.dumps(params)
					log.line = data['line'] 
					log.shift = data['shift']
					log.skedule_time = self.calc_skedule_time(data['start'],data['end'])	
					log.team = data['team']
					#log.cases = ''
					#db.session.add(log)
					#db.session.commit()
					
					
				else:
					error.append(man)

		elif case_status ==1:
			dtime=[]

			##check if all the machines have downtime record for that day#
			for man in data['machines']:
				if self.check_downtime(man,data['start'],data['end']):
					report='good'
				else:
					dtime.append(man)

			if len(dtime) >0:
				##one or more machines have no downtime record. Therefore, share cases by number of machines#
				cas='no downtime record'
				num = len(data['machines'])

				for man in data['machines']:
					##delete all production data of this sku on the machine for the shift#
					prodate = news.get_date_from_datetime(data['start'])['date']
					check = db.session.query(Production).filter(Production.mcode==man,Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).count()
					if check >0:
						db.session.query(Production).filter(Production.line==data['line'],Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).delete()
						db.session.commit()

					###check if machine has parameters for the sku#
					if self.check_param(man,data['product']):

						##get product parameters for the sku#
						params = self.fetch_params(man,data['product'])
						##now log production data for the machine#
						log = Production()
						log.prodate = datetime.strptime(str(prodate), "%Y-%m-%d")
						log.product_code =data['product']
						log.mcode=man
						log.product_params= json.dumps(params)
						log.line = data['line'] 
						log.shift = data['shift']
						stym = self.calc_skedule_time(data['start'],data['end'])
						log.skedule_time = stym	
						log.team = data['team']
						cas = int(int(data['cases'])/num)
						log.cases = cas
						log.msu = self.calc_msu(data['product'],cas,man,stym)['msu']
						log.volume = self.calc_msu(data['product'],cas,man,stym)['volume']
						log.exp_volume = self.calc_msu(data['product'],cas,man,stym)['exp_volume']
						log.start_tyme = datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S.%f")
						log.end_tyme = datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S.%f")

						db.session.add(log)
						db.session.commit()
						
					else:
						error.append(man)

			else:
				##there is downtime records, share cases according to uptime by machines#
				uptime_total=[]
				machine_uptime={}
				for man in data['machines']:
					uptime=news.get_total_uptime(man,data['start'],data['end'])
					uptime_total.append(int(uptime['uptime']))
					machine_uptime[man]=uptime['uptime']

				total_uptime = sum(uptime_total)

				for man in data['machines']:
					##delete all production data of this sku on the machine for the shift#
					prodate = news.get_date_from_datetime(data['start'])['date']
					check = db.session.query(Production).filter(Production.mcode==man,Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).count()
					if check >0:
						db.session.query(Production).filter(Production.line==data['line'],Production.prodate==prodate,Production.shift==data['shift'],Production.product_code==data['product']).delete()
						db.session.commit()

					###check if machine has parameters for the sku#
					if self.check_param(man,data['product']):

						##get product parameters for the sku#
						params = self.fetch_params(man,data['product'])
						##now log production data for the machine#
						log = Production()
						log.prodate = datetime.strptime(str(prodate), "%Y-%m-%d")
						log.product_code =data['product']
						log.mcode=man
						log.product_params= json.dumps(params)
						log.line = data['line'] 
						log.shift = data['shift']
						stym = self.calc_skedule_time(data['start'],data['end'])
						log.skedule_time = stym
						log.team = data['team']
						cas = self.share_cases_by_uptime(total_uptime,machine_uptime[man],data['cases'])
						log.cases = cas
						log.msu = self.calc_msu(data['product'],cas,man,stym)['msu']
						log.volume = self.calc_msu(data['product'],cas,man,stym)['volume']
						log.exp_volume = self.calc_msu(data['product'],cas,man,stym)['exp_volume']
						log.start_tyme = datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S.%f")
						log.end_tyme = datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S.%f")

						db.session.add(log)
						db.session.commit()
					else:
						error.append(man)

		if len(error) == len(data['machines']):
			resp1=""
		else:
			resp1 = Markup("<div class='alert alert-success'>{}</div>".format("Production data was successfully logged."))
		if len(error) >0:
			resp2 = Markup("<div class='alert alert-danger'>{}: {}</div>".format("However, the following machine data were not logged because they have no product parameters for the selected SKU",str(error)))
		else:
			resp2 =''

		response =''
		response +=resp1
		response +=resp2
		return response

	def check_param(self,machine,productcode):

		mmm=Equipment.query.filter_by(m_code=machine).first()
		if mmm.product_params is not None and mmm.product_params !='None':
			##product parameters are present, get the one you need, if not boot out#
			params = json.loads(mmm.product_params)
			if len(params) ==0:
				return False

			param = [d for d in params if d['sku']==productcode]
			if param is not None:
				pass
			else:
				return False
		else:
			return False		
		
		return True	

	def fetch_params(self,machine,productcode):

		mmm=Equipment.query.filter_by(m_code=machine).first()
		
		params = json.loads(mmm.product_params)
		parame = [d for d in params if d['sku']==productcode]
		param = parame[0]
		
		return {'speed':param['speed'],'bpc':param['bpc'],'cpp':param['cpp']}

	def check_downtime(self,machine,start,end):
		##check for stop event on machine with start time or end tim btw prodduction schedule time#
		allstops = db.session.query(StopEvent).filter(StopEvent.machine==machine,((StopEvent.start_time.between(start,end) | StopEvent.end_time.between(start,end)))).count()
		#allstops = db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time.between(start,end)).all()

		if allstops >0:
			##machine has downtime records#					
			return True
		else:
			return False	

	def calc_skedule_time(self,start,end):

		s=str(start)
		s1=datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

		e=str(end)
		e1=datetime.strptime(e, "%Y-%m-%d %H:%M:%S.%f")
		t = e1 - s1
		mytime=divmod(t.total_seconds(), 60)
		tyme=int(mytime[0])
		
				
		return tyme 
	
	def share_cases_by_uptime(self,total_uptime,machine_uptime,total_cases):

		cases = (machine_uptime/total_uptime)*int(total_cases)

		return int(round(cases))


	def get_results(self,form):

		frog=STOPSEVENT()

		machine_data = []
		total_data = {}

		total_pr = []
		total_skduletime = []
		total_dwntime = []
		total_msu = []
		total_volume = []
		total_exp_volume = []
		total_upst = []
		total_updt = []
		total_metrictone = []
		total_scrap_uptime = 0
		total_scrap_skedule_time = 0

		##process the datetime inputs#
		sub = timedelta(seconds=1)
		start = datetime.strptime(form.start.data, "%Y-%m-%d, %H:%M:%S.%f")
		end = datetime.strptime(form.end.data, "%Y-%m-%d, %H:%M:%S.%f")	- sub	

		##get individual machine data#
		for man in form.machine.data:
			if form.team.data !='0' and form.shift.data !='0':
				## filter query by team and shift#
				production=db.session.query(Production).filter(Production.mcode==man,Production.start_tyme.between(start,end),Production.shift==form.shift.data,Production.team==form.team.data).order_by(Production.prodate.asc()).all()
			elif form.team.data !='0' and form.shift.data == '0':
				##filter query by team only
				production=db.session.query(Production).filter(Production.mcode==man,Production.start_tyme.between(start,end),Production.team==form.team.data).order_by(Production.prodate.asc()).all()
			elif form.shift.data !='0' and form.team.data == '0':
				##filter query by shift only#
				production=db.session.query(Production).filter(Production.mcode==man,Production.start_tyme.between(start,end),Production.shift==form.shift.data).order_by(Production.prodate.asc()).all()
			else:
				##don't filter query#
				production=db.session.query(Production).filter(Production.mcode==man,Production.start_tyme.between(start,end)).order_by(Production.prodate.asc()).all()

			if len(production) >0:
				##calculate each production parameter#
				mr={}

				pr=[]
				skdultime=[] 
				dwntime=[]
				volume=[]
				exp_volume=[]
				msu=[]
				upst=[]
				updt=[]
				metrictone = []
				scrap_uptime = 0
				scrap_skedule_time = 0

				for x in production :
					#PR=self.get_pr(x.cases,x.skedule_time,json.loads(x.product_params))
					PR=self.get_pr_from_volume(x.volume,x.exp_volume)
					pr.append(PR)

					skdultime.append(x.skedule_time)

					DT = self.calc_downtime_from_pr(PR,x.skedule_time)
					dwntime.append(float(DT))

					msu.append(x.msu)

					volume.append(x.volume)
					exp_volume.append(x.exp_volume)

					mt = self.convert_to_metrictones(x.msu,x.product_code)
					metrictone.append(mt)

					##get upst and updt#
					stop=frog.get_stop_data(man,x.start_tyme,x.end_tyme,x.skedule_time)['upst']
					upst.append(stop)
					dt=frog.get_stop_data(man,x.start_tyme,x.end_tyme,x.skedule_time)['updt']
					updt.append(dt)

					## calculate uptime for scrap analysis
					# if machine does not have uptime record, then uptime and thus scrap should return 0
					upt = frog.get_stop_data(man,x.start_tyme,x.end_tyme,x.skedule_time)['uptime']
					if upt > 0:
						scrap_uptime += upt
						scrap_skedule_time += int(x.skedule_time)
					else:
						scrap_uptime += 0
						scrap_skedule_time += 1
				
				mr['mcode']=man
				#mr['pr'] = "{:0.2f}".format(sum(pr)/float(len(production))) #pr average for each machine production entry
				mr['pr'] = "{:0.2f}".format(sum(volume)*100/sum(exp_volume))
				mr['skeduletime']=sum(skdultime)
				mr['downtime'] = "{:0.2f}".format(sum(dwntime)) #self.calc_downtime_from_pr(mr['pr'],mr['skeduletime']) 
				mr['upst']=frog.calc_upst(sum(upst),sum(skdultime))
				mr['msu'] =sum(msu)
				mr['updt'] = frog.calc_updt(sum(updt),sum(skdultime))
				mr['updt_mins'] = "{:0.2f}".format(sum(updt)) #updt in mins
				mr['metrictone'] = sum(metrictone)
				mr['scrap'] = self.calc_scrap(scrap_uptime,scrap_skedule_time,mr['pr'])

				machine_data.append(mr)

				##get total pr with below data
				total_volume.append(sum(volume))
				total_exp_volume.append(sum(exp_volume))

				##calculate Total data for all machines#
				total_pr.append(float(mr['pr']))
				total_skduletime.append(mr['skeduletime'])
				total_dwntime.append(float(mr['downtime']))    
				total_msu.append(mr['msu'])				
				total_upst.append(sum(upst))
				total_updt.append(sum(updt))
				total_metrictone.append(mr['metrictone'])
				total_scrap_uptime += scrap_uptime
				total_scrap_skedule_time += scrap_skedule_time


			else:
				mr={}

				mr['mcode']=man
				mr['pr'] = 0 #pr average
				mr['skeduletime']=0
				mr['downtime'] = 0
				mr['upst']=0
				mr['msu'] =0
				mr['updt'] =0
				mr['updt_mins'] = 0
				mr['metrictone'] = 0
				mr['scrap'] = 0

				machine_data.append(mr)

				##get total pr with below data
				total_volume.append(0)
				total_exp_volume.append(1) ## this will add 1g to the total volume for every machine that does not have data within the period of run

				total_scrap_uptime += 0
				total_scrap_skedule_time += 1

				##calculate Total data for all machines#
				total_pr.append(mr['pr'])
				total_skduletime.append(mr['skeduletime'])
				total_dwntime.append(mr['downtime'])
				total_msu.append(mr['msu'])
				total_upst.append(mr['upst'])
				total_updt.append(mr['updt'])
				total_metrictone.append(mr['metrictone'])

		total_data['pr'] = "{:0.2f}".format(sum(total_volume)*100/sum(total_exp_volume))
		total_data['skeduletime'] = sum(total_skduletime)
		total_data['downtime'] = "{:0.2f}".format(sum(total_dwntime)) #"{:0.2f}".format(float(100 - float(total_data['pr']))) 
		total_data['msu'] = sum(total_msu)
		total_data['metrictone'] = sum(total_metrictone)
		total_data['upst'] = frog.calc_upst(sum(total_upst),sum(total_skduletime))
		total_data['updt'] = frog.calc_updt(sum(total_updt),sum(total_skduletime))
		total_data['updt_mins'] = "{:0.2f}".format(sum(total_updt)) #updt in mins
		total_data['scrap'] = self.calc_scrap(total_scrap_uptime,total_scrap_skedule_time,total_data['pr'])



		if len(machine_data) ==0:	
			return {'status':2,'end':str(form.end.data),'start':str(form.start.data),'data':'','message':'No results found.', 'total':total_data}

		return {'status':1,'end':str(form.end.data),'start':str(form.start.data),'data':machine_data,'message':'All good.','total':total_data}

	def get_pr(self,cases,skeduletime,params):
		value = (int(cases) * int(params['bpc'])*100)/(int(params['speed'])*skeduletime)
		pr = "{:0.2f}".format(value)
		pr = float(pr)

		return pr

	def get_pr_from_volume(self,volume,exp_volume):
		value = float(volume*100)/float(exp_volume)
		pr = "{:0.2f}".format(value)
		pr = float(pr)

		return pr

	def calc_pr_from_uptime(self,uptime,skedule_time):

		u = int(uptime)
		s = int(skedule_time)

		data = "{:0.2f}".format((u / s) * 100)

		result = float(data)

		return result

	def calc_scrap(self,uptime,skedule_time,pr):

	 	##This will give scrapped products based on volume produced
	 	if uptime > 0:
	 		up_time_pr = self.calc_pr_from_uptime(uptime,skedule_time)
	 		volume_pr = float(pr)

	 		data = "{:0.2f}".format(up_time_pr - volume_pr)
	 	else:
	 		data = "{:0.2f}".format(0)

	 	result = float(data)

	 	return result

	def calc_downtime_from_pr(self, pr,skedule_time):

		dt = ((100-float(pr))*skedule_time)/100 #dt in minutes
		pc=100-float(pr) #dt in %

		return "{:0.2f}".format(dt) #round(dt)

	def calc_msu(self,productcode,cases,man,skedule_time):

		low_surd_codes=[str(81716944),str(81756803),str(81756800),str(81716943),str(81756802),str(81756799),str(81756801)]

		data=db.session.query(SKU.weight,Equipment.product_params).filter(SKU.productcode==productcode,Equipment.m_code==man).first()

		if data is not None and data.product_params is not None:
			product_param=json.loads(data.product_params)
			params=[i for i in product_param if i['sku']==productcode]
			param=params[0]
			
			bpc=int(param['bpc'])
			WT=int(data.weight)/1000 #weight in KG
			wt=int(data.weight) #weight in grams
			st=int(skedule_time)
			cp=int(cases)
			sp=int(param['speed'])

			##calculate msu for low surds differently#
			if str(productcode) in low_surd_codes:
				msu="{:0.2f}".format((bpc*cp*WT)/16000)
				exp_msu="{:0.2f}".format((sp*st*WT)/16000)
				m_tones = "{:0.2f}".format(float(msu) * 16) #volume in metric tones				
			else:
				##calculate msu for other surds#
				msu="{:0.2f}".format((bpc*cp*WT)/7500)
				exp_msu="{:0.2f}".format((sp*st*WT)/7500)
				m_tones = "{:0.2f}".format(float(msu) * 7.5) #volume in metric tones

			volume = "{:0.2f}".format((bpc*cp*wt)) #in grams
			exp_volume = "{:0.2f}".format((sp*st*wt)) #in grams



		return {'msu':float(msu),'exp_msu':float(exp_msu),'volume':float(volume),'exp_volume':float(exp_volume),'m_tones':float(m_tones)}

	def get_production_entries(self,form):

		tick=STOPSEVENT()
		myentry=[]
		sub = timedelta(seconds=1) #subtract this amount of time from end time
		start=datetime.strptime(form.start.data, "%Y-%m-%d, %H:%M:%S.%f")
		end=datetime.strptime(form.end.data, "%Y-%m-%d, %H:%M:%S.%f") - sub

		if form.shift.data !='0' and form.machine.data :
			for man in form.machine.data:
				prodata=db.session.query(Production).filter(Production.start_tyme.between(start,end),Production.shift==form.shift.data,Production.mcode==man).order_by(Production.prodate.desc()).all()
				if prodata is not None:
					for i in prodata:
						mr={}
						mr['prodate']=i.prodate
						mr['shift']=i.shift
						mr['start_tyme']=i.start_tyme.strftime("%H:%M:%S")
						mr['team']=i.team
						mr['line']=i.line
						mr['mcode']=man
						mr['product_code']=i.product_code
						mr['skedule_time']=i.skedule_time
						mr['cases']=i.cases
						mr['pid']=i.pid
						mr['msu']=i.msu
						mr['volume']=i.volume
						mr['exp_volume']=i.exp_volume

						myentry.append(mr)

		elif form.machine.data and form.shift.data =='0':
			for man in form.machine.data:
				prodata=db.session.query(Production).filter(Production.start_tyme.between(start,end),Production.mcode==man).order_by(Production.prodate.desc()).all()
				if prodata is not None:
					for i in prodata:
						mr={}
						mr['prodate']=i.prodate 
						mr['shift']=i.shift
						mr['team']=i.team
						mr['start_tyme']=i.start_tyme.strftime("%H:%M:%S")
						mr['line']=i.line
						mr['mcode']=man 
						mr['product_code']=i.product_code
						mr['skedule_time']=i.skedule_time
						mr['cases']=i.cases
						mr['pid']=i.pid
						mr['msu']=i.msu
						mr['volume']=i.volume
						mr['exp_volume']=i.exp_volume

						myentry.append(mr)


		elif not form.machine.data and form.shift.data !='0':

			myentry=db.session.query(Production).filter(Production.start_tyme.between(start,end),Production.shift==form.shift.data).order_by(Production.prodate.desc(),).all()

		else:
			myentry=db.session.query(Production).filter(Production.start_tyme.between(start,end)).order_by(Production.prodate.desc()).all()

		return myentry

	def erase_production_entries(self,data):
		news=STOPSEVENT()

		#prodate = news.get_date_from_datetime(data['start'])['date']
		#kt=news.get_date_from_datetime('2024-08-24 07:00:00.001')['date']
		#tym=datetime.strptime(kt, "%Y-%m-%d")
		#Production.mcode==man,Production.prodate==kt,Production.shift==data['shift'],Production.product_code==data['product']
		check = db.session.query(Production).filter(Production.prodate==data['date'],Production.product_code==data['code'],Production.line==data['line'],Production.shift==data['shift']).count()
		if check >0:
			db.session.query(Production).filter(Production.prodate==data['date'],Production.product_code==data['code'],Production.line==data['line'],Production.shift==data['shift']).delete()
			db.session.commit()
			return {'status':1, 'message':str(check) +' entries deleted successfully.'}
		else:
			return {'status':2, 'message':'No matching entries found.'}


	def convert_to_metrictones(self,msu,productcode):

		low_surd_codes=[str(81716944),str(81756803),str(81756800),str(81716943),str(81756802),str(81756799),str(81756801)]

		##calculate metric tones for low surds#
		if str(productcode) in low_surd_codes:			
			m_tones = "{:0.2f}".format(float(msu) * 16) #volume in metric tones				
		else:
			##calculate metric tones for other surds#			
			m_tones = "{:0.2f}".format(float(msu) * 7.5)

		result = float(m_tones)
		
		return result

	def get_psg_dt_report(self, form):
		new = STOPSEVENT()
		sub = timedelta(seconds=1)
		start=datetime.strptime(form.start.data, "%Y-%m-%d, %H:%M:%S.%f")
		end=datetime.strptime(form.end.data, "%Y-%m-%d, %H:%M:%S.%f") - sub

		entry = []

		if len(form.include_downtime.data)>0 and len(form.machine.data)==0:
			stops = []
			for dwntime in form.include_downtime.data:
				items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end),StopEvent.reason_level_one==dwntime).all()
				if items is not None:
					for item in items:
						stops.append(item)

		elif len(form.include_downtime.data)>0 and len(form.machine.data)>0:
			stops = []
			for machine in form.machine.data:
				for dwntime in form.include_downtime.data:
					items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end),StopEvent.reason_level_one==dwntime,StopEvent.machine==machine).all()
					if items is not None:
						for item in items:
							stops.append(item)

		elif len(form.exclude_downtime.data)>0 and len(form.machine.data)==0:
			items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end)).all()
			stops = []
			if items is not None:
				stops = [x for x in items if x.reason_level_one not in form.exclude_downtime.data]
		
		elif len(form.exclude_downtime.data)>0 and len(form.machine.data)>0:
			stops = []
			for machine in form.machine.data:
				items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end),StopEvent.machine==machine).all()
				if items is not None:
					events = [x for x in items if x.reason_level_one not in form.exclude_downtime.data]
					if len(events) > 0:
						stops.extend(events)
		
		elif len(form.transformation.data)>0 and len(form.machine.data)==0:
			items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end)).all()
			stops = []
			if items is not None:
				stops = [x for x in items if x.reason_level_two in form.transformation.data]
			
		elif len(form.transformation.data)>0 and len(form.machine.data)>0:
			stops = []
			for machine in form.machine.data:
				for dwntime in form.transformation.data:
					items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end),StopEvent.reason_level_two==dwntime,StopEvent.machine==machine).all()
					if items is not None:
						for item in items:
							stops.append(item)

		elif len(form.transformation.data)==0 and len(form.include_downtime.data)==0 and len(form.exclude_downtime.data)==0 and len(form.machine.data)>0:
			stops = []
			for machine in form.machine.data:
				items = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end),StopEvent.machine==machine).all()
				if items is not None:
					for item in items:
						stops.append(item)

		else:
			stops = db.session.query(StopEvent).filter(StopEvent.start_time.between(start,end)).all()

		if stops is not None:
			for x in stops:
				mr = {}
				if x.end_time is None:
					x.end_time = datetime.now()
				mr['dwntime'] = myfunc.calc_skedule_time(x.start_time,x.end_time)
				mr['reason1'] = new.get_reason_name(x.reason_level_one,1)
				mr['reason2'] = new.get_reason_name(x.reason_level_two,2)
				mr['reason3'] = new.get_reason_name(x.reason_level_three,3)
				mr['reason4'] = new.get_reason_name(x.reason_level_four,4)
				mr['comment'] = x.comment
				mr['machine'] = x.machine
				mr['start_date'] = x.start_time.strftime("%m-%d-%Y")
				mr['start_time'] = x.start_time.strftime("%H:%M:%S")
				mr['end_date'] = x.end_time.strftime("%m-%d-%Y")
				mr['end_time'] = x.end_time.strftime("%H:%M:%S")

				entry.append(mr)

			entry = sorted(entry, key=itemgetter('dwntime'), reverse=True)

		return entry

	def normalize_dt_report(self, data):
		
		items = []
		
		def group_list_dicts(dic):

			if len(dic) >0:
				for dis in dic:					
					transformation = dis['reason2']					 
					group = [x for x in dic if x['reason2']==transformation]
					mr = {}
					mr['name'] = transformation
					if transformation == '' or transformation is None:
						mr['name'] = 'Blank'
					mr['dwntime'] = 0
					machines_affected = []
					for i in group:
						mr['dwntime'] += int(i['dwntime'])
						machines_affected.append(i['machine'])
						dic.remove(i)
					machines_affected = [i for i in set(machines_affected)]
					mr['machines'] = ",".join(machines_affected)
					items.append(mr)
					group_list_dicts(dic)

			else:
				return

		group_list_dicts(data)

		if items != []:
			items = sorted(items, key=itemgetter('dwntime'), reverse=True)

		return json.dumps({'status':1,'data':items})
	
