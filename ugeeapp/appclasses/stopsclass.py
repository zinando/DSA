from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import StopEvent,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
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
#from ugeeapp.myapp import get_uptime



class STOPSEVENT():

	def __init__(self):
		pass

	def get_date_from_datetime(self,datime):

		end=datetime.strptime(str(datime), "%Y-%m-%d %H:%M:%S.%f")
		#t=str(end.year)+"/"+str(end.month)+"/"+str(end.day)+" "+str(end.hour)+":"+str(end.minute)+":"+str(end.second)
		t={}
		t['date']=end.strftime("%Y-%m-%d") #str(end.year)+"-"+str(end.month)+"-"+str(end.day)
		t['time']=end.strftime("%H:%M:%S") #str(end.hour)+":"+str(end.minute)+":"+str(end.second)
		return t

	def fetch_stops_reason_one(self):
		stops = ReasonOne.query.order_by(ReasonOne.reason.asc()).all()
		return stops
	def fetch_stops_reason_two(self):
		stops = ReasonTwo.query.order_by(ReasonTwo.reason.asc()).all()
		return stops	

	def get_date_time_from_date_and_time(self,date,time):


		return 

	def get_total_uptime(self,machine,start,end):

		k1=str(start)
		skedule_start=datetime.strptime(k1, "%Y-%m-%d %H:%M:%S.%f")
		k2=str(end)
		skedule_end=datetime.strptime(k2, "%Y-%m-%d %H:%M:%S.%f")

		news=myfunc
		downtyme=[]
		xy={}
		

		myevent=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time.between(start,end)).order_by(StopEvent.start_time.asc()).all()
		count=0

		if len(myevent) >0: ##checking that machine has downtime within the schedule time			
			for i in myevent:
				count +=1
				##get the first stop event
				if count==1:
					##check if it's the only stop
					if len(myevent)==1:
						##check if the stop has end_time
						if i.end_time is not None:
							##check if end time is greater than schedule end time
							stopend=datetime.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S.%f")

							if stopend <= skedule_end:
								down=news.calc_skedule_time(i.start_time,i.end_time)
								downtyme.append(down)
							else:
								down=news.calc_skedule_time(i.start_time,end)
								downtyme.append(down)
						else:
							down=news.calc_skedule_time(i.start_time,end)
							downtyme.append(down)
					else:
						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtyme.append(down)
				else:
					##check if stop has end time record#
					if i.end_time is not None:
						##check if end time is greater than schedule end time
						stopend=datetime.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S.%f")

						if stopend <= skedule_end:
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtyme.append(down)
						else:
							down=news.calc_skedule_time(i.start_time,end)
							downtyme.append(down)
						
					else:
						down=news.calc_skedule_time(i.start_time,end)
						downtyme.append(down) 
				
		else:
			downtyme.append(0)

		
		##look for a stop whose end time from previous event is within the skedule time
		myevent2=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.end_time.between(start,end),StopEvent.start_time<start).first()
		if myevent2 is not None:
			down=news.calc_skedule_time(start,myevent2.end_time)
			downtyme.append(down)

		skeduletyme=news.calc_skedule_time(start,end)
		dtime=sum(downtyme)
		uptime=skeduletyme-dtime

		xy['uptime']=uptime
		xy['downtime']=dtime

		return xy

	def get_total_uptimeX(self,machine,start,end):
		news=myfunc
		k1=str(start)
		skedule_start=datetime.strptime(k1, "%Y-%m-%d %H:%M:%S.%f")
		k2=str(end)
		skedule_end=datetime.strptime(k2, "%Y-%m-%d %H:%M:%S.%f")
				
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time.between(start,end)).order_by(StopEvent.start_time.asc()).all()
		count=0	

		t=''
		num=len(myevent)
		xy={}
		uptime=[]
		downtime=[]
		for i in myevent:
			count=count+1			
			#down=news.calc_skedule_time(i.start_time,i.end_time)
			##get the first stop#
			if count == 1:
				##ensure stop is not the only stop present#
				if count < num:				
					f=str(i.start_time)
					stopstart=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
					l=str(i.end_time)
					stopend=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
					#time=end-start
					if stopstart >skedule_start and stopend<skedule_end:
						##stop happened after schedule start.#
						##look for another stop that happened in the previous shift but extended into the current shift#
						myevent2=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time<start,StopEvent.end_time>start).first()
						if myevent2 is not None:
							##get part of the downtime that enxtended into the schedule time#
							down=news.calc_skedule_time(start,myevent2.end_time)
							downtime.append(int(down))
							##get uptime of i between end of event2 and start of i#
							up=news.calc_skedule_time(myevent2.end_time,i.start_time)					
							uptime.append(int(up))
							##now get downtime for i#
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtime.append(int(down))
						else:
							up=news.calc_skedule_time(start,i.start_time)					
							uptime.append(int(up))
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtime.append(int(down))

					elif stopstart==skedule_start and stopend<skedule_end:
						##stop happened at start time#
						uptime.append(0)
						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtime.append(down)
				elif count == num:
					##i is the only stop#
					f=str(i.start_time)
					stopstart=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
					l=str(end)
					stopend=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
					if stopstart >skedule_start and stopend<skedule_end:
						##stop happened after schedule start.#
						##look for another stop that happened in the previous shift but extended into the current shift#
						myevent2=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time<start,StopEvent.end_time>start).first()
						if myevent2 is not None:
							##get part of the downtime that enxtended into the schedule time#
							down=news.calc_skedule_time(start,myevent2.end_time)
							downtime.append(int(down))
							##get uptime of i between end of event2 and start of i#
							up=news.calc_skedule_time(myevent2.end_time,i.start_time)					
							uptime.append(int(up))
							##now get downtime for i#
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtime.append(int(down))
						else:
							up=news.calc_skedule_time(start,i.start_time)					
							uptime.append(int(up))
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtime.append(int(down))

					elif stopstart==skedule_start and stopend<skedule_end:
						##stop happened at start time#
						uptime.append(0)
						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtime.append(down)
					elif stopstart==skedule_start and stopend>skedule_end:
						##stop happened at start time#
						uptime.append(0)
						down=news.calc_skedule_time(i.start_time,end)
						downtime.append(down)
					else:
						##stop end time is beyond the schedule end
						##look for another stop that happened in the previous shift but extended into the current shift#
						myevent2=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time<start,StopEvent.end_time>start).first()
						if myevent2 is not None:
							##get part of the downtime that enxtended into the schedule time#
							down=news.calc_skedule_time(start,myevent2.end_time)
							downtime.append(int(down))
							##get uptime of i between end of event2 and start of i#
							up=news.calc_skedule_time(myevent2.end_time,i.start_time)					
							uptime.append(int(up))
							##now get downtime for i#
							down=news.calc_skedule_time(i.start_time,end)
							downtime.append(int(down))
						else:
							up=news.calc_skedule_time(start,i.start_time)					
							uptime.append(int(up))
							down=news.calc_skedule_time(i.start_time,end)
							downtime.append(int(down))

			elif count == num:
				##this is the last stop event#
				if i.end_time is not None:
					f=str(i.start_time)
					stopstart=datetime.strptime(f, "%Y-%m-%d %H:%M:%S.%f")
					l=str(i.end_time)
					stopend=datetime.strptime(l, "%Y-%m-%d %H:%M:%S.%f")
					#time=end-start
					if stopend >skedule_end:
						up=news.get_uptime(i.sid,i.start_time,machine)
						mytime=	divmod(up.total_seconds(), 60)
						uptyme=int(mytime[0])
						uptime.append(uptyme)

						down=news.calc_skedule_time(i.start_time,end)
						downtime.append(int(down))

					elif stopend == skedule_end:
						up=news.get_uptime(i.sid,i.start_time,machine)
						mytime=	divmod(up.total_seconds(), 60)
						uptyme=int(mytime[0])
						uptime.append(uptyme)

						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtime.append(int(down))

					elif stopend < skedule_end:
						up=news.calc_skedule_time(i.end_time,end)
						uptime.append(up)

						up1=news.get_uptime(i.sid,i.start_time,machine)
						mytime1=	divmod(up1.total_seconds(), 60)
						uptyme1=int(mytime1[0])
						uptime.append(uptyme1)						

						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtime.append(int(down))

				else:
					##i has no end_time record#
					down=news.calc_skedule_time(i.start_time,end)
					downtime.append(int(down))
					
					up=news.get_uptime(i.sid,i.start_time,machine)
					mytime=	divmod(up.total_seconds(), 60)
					uptyme=int(mytime[0])
					uptime.append(uptyme)

			else:
				down=news.calc_skedule_time(i.start_time,i.end_time)
				downtime.append(int(down))
				
				up=news.get_uptime(i.sid,i.start_time,machine)
				mytime=	divmod(up.total_seconds(), 60)
				uptyme=int(mytime[0])
				uptime.append(uptyme)



			
		
		xy['uptime']=sum(uptime)
		xy['downtime']=sum(downtime)				

		return xy


	def get_user_defined_stops(self,SD,ST,ED,ET,mach):

		tr1=datetime.strptime(str(SD+' '+ST), "%Y-%m-%d %H:%M:%S")		
		tr2=datetime.strptime(str(ED+' '+ET), "%Y-%m-%d %H:%M:%S")		
		#myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,StopEvent.start_time.between(tr1,tr2)).order_by(StopEvent.start_time.desc()).all()
		myevent=db.session.query(StopEvent).filter(StopEvent.machine==mach,((StopEvent.start_time>=tr1) & (StopEvent.start_time<=tr2))).order_by(StopEvent.start_time.desc()).all()
		
		return myevent

	def get_formated_date(self,data):
		end=datetime.strptime(str(data), "%Y-%m-%d")
		return end


	def get_stop_data(self,machine,start,end,skeduletyme):

		#start=self.get_date_from_datetime(start)['date']
		#end=self.get_date_from_datetime(end)['date']

		#production=db.session.query(Production).filter(Production.mcode==machine,Production.prodate.between(start,end)).first()
		#start=production.start_tyme
		#end=production.end_tyme
		#skeduletyme=production.skedule_time

		##the journey begins here#

		k1=str(start)
		skedule_start=datetime.strptime(k1, "%Y-%m-%d %H:%M:%S")
		k2=str(end)
		skedule_end=datetime.strptime(k2, "%Y-%m-%d %H:%M:%S")

		news=myfunc
		downtyme=[]
		upst=[]
		updt=[] 
		xy={}
		

		myevent=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.start_time.between(start,end)).order_by(StopEvent.start_time.asc()).all()
		count=0

		if len(myevent) >0: ##checking that machine has downtime within the schedule time			
			for i in myevent:
				count +=1
				stopid=i.sid
				##get the first stop event
				if count==1:
					##check if it's the only stop
					if len(myevent)==1:
						##check if the stop has end_time
						if i.end_time is not None:
							##check if end time is greater than schedule end time
							stopend=datetime.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S.%f")

							if stopend <= skedule_end:
								down=news.calc_skedule_time(i.start_time,i.end_time)
								downtyme.append(down)
								##check if stop is planned or not#
								if self.is_planned(stopid):
									upst.append(0)
									updt.append(0)
								else:
									upst.append(1)
									updt.append(down)
							else:
								down=news.calc_skedule_timexY(i.start_time,end)
								downtyme.append(down)

								##check if stop is planned or not#
								if self.is_planned(stopid):
									upst.append(0)
									updt.append(0)
								else:
									upst.append(1)
									updt.append(down)
						else:
							down=news.calc_skedule_timexY(i.start_time,end)
							downtyme.append(down)

							##check if stop is planned or not#
							if self.is_planned(stopid):
								upst.append(0)
								updt.append(0)
							else:
								upst.append(1)
								updt.append(down)
					else:
						down=news.calc_skedule_time(i.start_time,i.end_time)
						downtyme.append(down)

						##check if stop is planned or not#
						if self.is_planned(stopid):
							upst.append(0)
							updt.append(0)
						else:
							upst.append(1)
							updt.append(down)
				else:
					##check if stop has end time record#
					if i.end_time is not None:
						##check if end time is greater than schedule end time
						stopend=datetime.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S.%f")

						if stopend <= skedule_end:
							down=news.calc_skedule_time(i.start_time,i.end_time)
							downtyme.append(down)

							##check if stop is planned or not#
							if self.is_planned(stopid):
								upst.append(0)
								updt.append(0)
							else:
								upst.append(1)
								updt.append(down)

						else:
							down=news.calc_skedule_timexY(i.start_time,end)
							downtyme.append(down)

							##check if stop is planned or not#
							if self.is_planned(stopid):
								upst.append(0)
								updt.append(0)
							else:
								upst.append(1)
								updt.append(down)
						
					else:
						down=news.calc_skedule_timexY(i.start_time,end)
						downtyme.append(down) 

						##check if stop is planned or not#
						if self.is_planned(stopid):
							upst.append(0)
							updt.append(0)
						else:
							upst.append(1)
							updt.append(down)
				
		else:
			downtyme.append(0)
			upst.append(0)
			updt.append(0)


		
		##look for a stop whose end time from previous event is within the skedule time
		myevent2=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.end_time.between(start,end),StopEvent.start_time<start).first()
		if myevent2 is not None:
			stopid=myevent2.sid
			down=news.calc_skedule_timeXy(start,myevent2.end_time)
			downtyme.append(down)

			##check if stop is planned or not#
			if self.is_planned(stopid):
				upst.append(0)
				updt.append(0)
			else:
				upst.append(1)
				updt.append(down)



		#skeduletyme=20 #news.calc_skedule_timeXY(start,end)
		if len(myevent) > 0:
			dtime = sum(downtyme)
			uptime = skeduletyme-dtime
			stops = sum(upst)
			DT = sum(updt)
		else:
			dtime = 0
			uptime = 0
			stops = 0
			DT = 0

		xy['uptime']=uptime
		xy['downtime']=dtime
		xy['upst']=stops #self.calc_upst(stops,skeduletyme)
		xy['updt']=DT #self.calc_updt(DT,skeduletyme)


		return xy

	def is_planned(self,stopid):

		##get the stop#
		myevent=db.session.query(StopEvent).filter(StopEvent.sid==stopid).first()

		if myevent is not None:
			if myevent.reason_level_one is not None:

				##get the reason#
				event = ReasonOne.query.filter_by(rid=myevent.reason_level_one).first()

				if event.reason.title() =='Planned Stop' or event.reason.title() == 'Utilities':

					return True
				else:
					return False

			else:
				return False		
		
		else:
			return True

	def calc_upst(self,stops,skedule_time):

		if skedule_time ==0:
			stop = 0
		else:
			calc=(1440*int(stops))/int(skedule_time)

			stop="{:0.2f}".format(calc)


		return float(stop)

	def calc_updt(self,dt,skedule_time):

		if skedule_time ==0:
			UPDT = 0
		else:
			calc=(int(dt)*100)/int(skedule_time)

			UPDT="{:0.2f}".format(calc)


		return float(UPDT)

	def get_reason_name(self,rid,level):

		item = ''
		try:
			if level == 1:
				reason = ReasonOne.query.filter_by(rid=rid).first()
			elif level == 2:
				reason = ReasonTwo.query.filter_by(tid=rid).first()
			elif level == 3:
				reason = ReasonTri.query.filter_by(trid=rid).first()
			elif level == 4:
				reason = ReasonFour.query.filter_by(fid=rid).first()
			item = reason.reason
		except:
			return item

		return item
