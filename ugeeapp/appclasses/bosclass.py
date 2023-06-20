from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from ugeeapp.models import User,SAFETY_BOS,QA_BOS,OGC_BOS
import time
import json
import datetime
from datetime import datetime,timedelta
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ugeeapp import db,app
from ugeeapp.helpers import myfunctions as myfunc
import hmac,hashlib


class BOSCLASS:

	def __init__(self):
		pass

	def log_safety_bos(self,form,department):

		##check the value of the bos#
		percent = float(form.percent.data.split()[0])
		if percent <100.00 and form.comment.data == '':

			return {'status':2,'message':'BOS Compliance is less than 100%. You are expected to provide comment(s) on the outage(s).'}
		
		##prepare observations and outages#
		##do not change the order#

		##MSG#
		if department=='MSG':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Employees apply personal locks containing his/her name & phone number to lock-out local disconnects (Pneumatic & Electrical) before performing tasks on equipment.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employee uses detailed QRP for non-routine/non-procedure tasks. Employee performing a maintenance task uses document procedure (SIMTWW/JSP/Job Aid etc).'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employee performing maintenance task wears appropriate PPE (stipulated by procedure) to execute the task?'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employees and contractors wear ear muffs or ear plugs when vibrator is ON at level 18?'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employee replaced flange covers for high pressure slurry lines & corrosive liquid lines after intervention?'
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

		##UTILITY#
		if department=='UTILITY':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Ear muffs is worn inside the Generator yard.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='No Oil/Water/Diesel spillage on the floor inside the Generator yard.'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='No oil / Diesel contamination inside drainage behind the Generator yard.'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='All the Generator Canopy door and the mesh door are closed properly while nobody inside the Generator yard.'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='No spare parts/Tools are not littering the work areas.'
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

		elif department=='QA':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Work Bench is free of any glassware , chemicals, reagent bottles used for analysis and only lablelled DI beaker is on work bench when no analysis is in progress.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Exposed chemicals are not left in the Desicator after usage.'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Analyst used rubber handglove while carrying acid and all other corrosive and fuming chemicals.'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='All chemicals are found in the area allotted to them. Expired chemicals are found in the allotted space ONLY. The entire place is clean, tidy and free of dust.'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="All balances (Top and Analytical balances ) and dusthood area are free from powder spill after all analysis is completed."
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

		elif department=='WHSE':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Contractors operating forklift in the warehouse wear seat belt.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Trucks are chocked  with a pair of chock at the wheel.'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Motor Boys wears reflective vest while directing a driver reversing truck.'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Forklift tyres are not worn and no critical safety defect  found on forklift ( e.g burnt lamp or horn).'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Pallets outside 5's are moved to the pallet shed at FP Dock station"
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

		elif department=='WHSERPM':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Contractors operating forklift in the warehouse wear seat belt.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Trucks are chocked  with a pair of chock at the wheel.'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Motor Boys wears reflective vest while directing a driver reversing truck.'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Forklift tyres are not worn and no critical safety defect  found on forklift ( e.g burnt lamp or horn).'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Employees and contractors clean powder and liquid spills immediately they occur."
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

		else:
			##PSG#
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Employees apply individual locks on local disconnects before working on machines and equipment. Locks have name & phone number.'
			obs1['value']='AT RISK' if form.point1.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employees and contractors dispose waste in the right bin. Only waste on the bin label is found inside the waste bin.'
			obs1['value']='AT RISK' if form.point2.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employees and contractors wear 3M nose mask and Safety Gloves while attending to powder spills.'
			obs1['value']='AT RISK' if form.point3.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Daily and previous week Scissors Lift inspections are done, and ALL doors are closed and Locked during lifting operation.'
			obs1['value']='AT RISK' if form.point4.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Employees in operation wear or hang their PPE pouches by the machine and use PPE as required.'
			obs1['value']='AT RISK' if form.point5.data == 0 else 'SAFE'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)


		log=SAFETY_BOS()

		log.userid = session['userid']
		log.observer = form.observer.data.title()
		log.department = form.department.data
		log.line = form.line.data
		log.shift = form.shift.data
		log.bos_type = form.bos_type.data
		log.team = form.team.data
		log.bos_time = form.bos_time.data
		log.percent = percent
		log.observation=json.dumps(obs)
		log.outages=json.dumps(out)
		log.comment = str(form.comment.data)
		db.session.add(log)
		db.session.commit()		


		return {'status':1,'message':'Safety BOS submission was successful!'}
		 	

	def log_quality_bos(self,form,department):

		##check the value of the bos#
		percent = float(form.percent.data.split()[0])
		if percent <100.00 and form.comment.data == '':

			return {'status':2,'message':'BOS Compliance is less than 100%. You are expected to provide comment(s) on the outage(s).'}
		
		##prepare observations and outages#
		##do not change the order#

		##MSG#
		if department == 'MSG':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Are the doors in the operating area across all floors working and net doors always closed?'
			obs1['value']='NO' if form.point1.data == 0 else 'YES'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all insecticutor bulbs ON? (specify which floor insecticutor bulb is defective).'
			obs1['value']='NO' if form.point2.data == 0 else 'YES'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Is reblend hopper at level 24 covered when not in use?'
			obs1['value']='NO' if form.point3.data == 0 else 'YES'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all raw materials stored at assigned storage location with material GCAS matching GCAS on storage location? (Check that material GCAS matches the GCAS on labels). Are all release labels removed from used EW basse cubitainer & bulk solids bags before reuse?'
			obs1['value']='NO' if form.point4.data == 0 else 'YES'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Bar Code Scanner on all active hoists (dumpspots) working (Level 12&24). (Observe this by using the bar code scanner to scan the bar code on the specifc material label, check if the hoist is activated by the scanning, if not, inform the Team and QA leaders immediately and log quality alert).'
			obs1['value']='NO' if form.point5.data == 0 else 'YES'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are calibration checks timely conducted for all weighing scales: Satellite laboratory? (Ask for calibration records).'
			obs1['value']='NO' if form.point6.data == 0 else 'YES'
			obs.append(obs1)
			if form.point6.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='There are no other observable quality outages on the operating floor? (If NO, please specify in the comment section).'			
			obs1['value']='NO' if form.point7.data == 0 else 'YES'
			obs.append(obs1)
			if form.point7.data == 0:
				 out.append(obs1)	 	 

		
		##QA LAB#
		if department == 'QA':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Are all records of analysis entered into the lab note books directly and are the lab notebooks (RPM, Regulatory, etc)  completely filled and quality issues are fully documented and tracked? (Checked that they filled to  date, peer reviewed and error correction are done, check if there are pieces of paper with analysis record in the lab) Are BPRs, RM  & PM COA stored in the designated area.'
			obs1['value']='NO' if form.point1.data == 0 else 'YES'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all the  equipment labeled, cleaned and well calibrated, and calibration tracking sheet updated? (Look at calibration records on each equipment and ask for calibration certificates for external calibration, check the equipment serial number and model number versus Tracking sheet for correctness)'
			obs1['value']='NO' if form.point2.data == 0 else 'YES'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Is the sample retention area and  lab area clean and tidy, table cleared after each analysis and are used samples discarded. (Check entire cleanliness of area and adherence to 5S standards, check that RM, PM and FP samples not more than one day is kept on the bench)?'
			obs1['value']='NO' if form.point3.data == 0 else 'YES'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all Laboratory excell worksheet  (FP Analytical Sheet, BH Base sheet, DDS worksheets, RM Calculationn sheet, Concentration Calc. software, e.t.c) passworded?,(open any laboratory worksheet and check for password protecton on calculation columns on the worksheet)'
			obs1['value']='NO' if form.point4.data == 0 else 'YES'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all chemicals and reagents stored in designated places, labelled and laboratory solutions unexpired? (Pick a bottle of any reagent, check its label, trace it to the chemical used in its preparation, When was it opened? Does it match with what you have on the Chemical consumption sheet?)'
			obs1['value']='NO' if form.point5.data == 0 else 'YES'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Are all Laboratory PC set to auto-lock after Three (3) minutes (Excuding Gallery PC set to Twenty (20) minutes)?, (Pick any Lab PC including SATLAB, open the PC and check after Three (3) for the set auto-lock setting)'
			obs1['value']='NO' if form.point6.data == 0 else 'YES'
			obs.append(obs1)
			if form.point6.data == 0:
				 out.append(obs1)

		elif department == 'WHSE':
			obs=[]
			out=[]

			obs1={}
			obs1['title']='Are the tops of finished products in their location  covered with tie sheets?  {if less than 5 pallets are seen without tie sheets, add as comment}'
			obs1['value']='NO' if form.point1.data == 0 else 'YES'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are finished products stored in-line with  their assigned stock  locators? (Check that different finished product SKU's are not  co-stored, except extended staging area,picking location and shipping areas)"
			obs1['value']='NO' if form.point2.data == 0 else 'YES'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are  RSDs closed when not in use and warehouse is not exposed? Is there   daylight entry from under when RSD is shut?  (Check that back-up tarpaulin curtain  are used when docks  are faulty)"
			obs1['value']='NO' if form.point3.data == 0 else 'YES'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are finished products  stored on good pallets ?  (Check  that products are not stored on broken or infested Pallets {Minimum of 5 pallets must be seen})"
			obs1['value']='NO' if form.point4.data == 0 else 'YES'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are all the insecticutors powered and working,  {if less than 5 pallets are seen without tie sheets, add as comment}"
			obs1['value']='NO' if form.point5.data == 0 else 'YES'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are the interior of the shipment trucks lined with polythene before FP cases are dead piled."
			obs1['value']='NO' if form.point6.data == 0 else 'YES'
			obs.append(obs1)
			if form.point6.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are the FP pallets stored in line with 5S. (Add as a comment if  less than 6  pallets seen)"			
			obs1['value']='NO' if form.point7.data == 0 else 'YES'
			obs.append(obs1)
			if form.point7.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are the FP pallets loads at s tandard? Checked that there is no fallen pallet loads, no leaking or burst /crushed cases"
			obs1['value']='NO' if form.point8.data == 0 else 'YES'
			obs.append(obs1)
			if form.point8.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are  Finished products shipped in line with FIFO?(Check that there is no batch on SAP NG02 location which is older  than the one being shipped. The shift shipment technician will share SAP snapshot with you)"
			obs1['value']='NO' if form.point9.data == 0 else 'YES'
			obs.append(obs1)
			if form.point9.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']="Are evacuated Finished products from production line stored at the designated place? (Check  that finished product evacuated from the lines are not stored at the shipment area, shipment activities are clearly segregated from FP received into warehouse activity)"			
			obs1['value']='NO' if form.point10.data == 0 else 'YES'
			obs.append(obs1)
			if form.point10.data == 0:
				 out.append(obs1)


		else:
			##PSG#

			obs=[]
			out=[]

			obs1={}
			obs1['title']='Line clearance, Quality checks & Process audit check are done as at when due and Proper Error correction standards are followed. (The LQC for weight sampe and Operator for Process audit, Line Clearance & TAMU check'
			obs1['value']='NO' if form.point1.data == 0 else 'YES'
			obs.append(obs1)
			if form.point1.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='2D Camera on all running machine working. (Observe this by putting your hand in front of the camera for 5 seconds and HMI should display NO READ ERROR. If this does not happen then the camera is not working. Inform the operator to shut down the machine and fill a qualit alert).'
			obs1['value']='NO' if form.point2.data == 0 else 'YES'
			obs.append(obs1)
			if form.point2.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='ICSL contractors weigh finished products in the polywoven case at EOL and the Daily calibration sheets for all the scaes are updated.'
			obs1['value']='NO' if form.point3.data == 0 else 'YES'
			obs.append(obs1)
			if form.point3.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Packing materials (Films and Polywoven) are stored at assigned location with material GCAS matching GCAS on storage location?'
			obs1['value']='NO' if form.point4.data == 0 else 'YES'
			obs.append(obs1)
			if form.point4.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Stacked Pallets are stable, wel-stretchwrapped/bound by nets, and good pallets used for palletising.'
			obs1['value']='NO' if form.point5.data == 0 else 'YES'
			obs.append(obs1)
			if form.point5.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='The washroom is clean with the forming sets properly arranged.'
			obs1['value']='NO' if form.point6.data == 0 else 'YES'
			obs.append(obs1)
			if form.point6.data == 0:
				 out.append(obs1)

			obs1={}
			obs1['title']='Coding Structure are legible and correct on the product, and polywoven: e.g (Product - BN y jjj pppp m tt, MFD mm yy EXP mm yy) and (Polywoven - BN y jjj pppp ln tt MFD dd mm yy EXP dd mm yy). Legend: y-year,j-julian date,p-plant code,m-machine,t-time,m-month,d-date,ln-line number.'
			obs1['value']='NO' if form.point7.data == 0 else 'YES'
			obs.append(obs1)
			if form.point7.data == 0:
				 out.append(obs1)	 	 

		log=QA_BOS()

		log.userid = session['userid']
		log.observer = form.observer.data.title()
		log.department = form.department.data
		log.line = form.line.data
		log.shift = form.shift.data
		log.bos_type = form.bos_type.data
		log.team = form.team.data
		log.bos_time = form.bos_time.data
		log.percent = percent
		log.observation=json.dumps(obs)
		log.outages=json.dumps(out)
		log.comment = str(form.comment.data)
		db.session.add(log)
		db.session.commit()		


		return {'status':1,'message':'Quality BOS Submitted successfully.'}	


	def log_ogc_bos(self,form,department):

		##check the value of the bos#
		percent = float(form.percent.data.split()[0])
		if percent <100.00 and form.comment.data == '':

			return {'status':2,'message':'OGC Compliance is less than 100%. You are expected to provide comment(s) on the outage(s).'}
		
		##prepare observations and outages#
		##do not change the order#

		##MSG#
		if department=='MSG':
			obs=[]
			out=[]

			sec={}
		

			sec['section']='MATERIAL STORAGE (LEVEL 0)'
			sec['inspection_point']=[]
		
			point={}
			point['title']="Material area"
			point['value']=form.point1.data	
			sec['inspection_point'].append(point)
			if form.point1.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point1.data
				out.append(news)

			point={}
			point['title']="Hoist gate"
			point['value']=form.point2.data	
			sec['inspection_point'].append(point)
			if form.point2.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point2.data
				out.append(news)

			obs.append(sec)

			sec={}

			sec['section']='PUMPING AREA (LEVEL 0)'
			sec['inspection_point']=[]

			point={}
			point['title']="Airlift feeding belt hood"
			point['value']=form.point3.data	
			sec['inspection_point'].append(point)
			if form.point3.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point3.data
				out.append(news)

			point={}
			point['title']="Heavies collection spot"
			point['value']=form.point4.data	
			sec['inspection_point'].append(point)
			if form.point4.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point4.data
				out.append(news)

			point={}
			point['title']="Tower cone"
			point['value']=form.point5.data	
			sec['inspection_point'].append(point)
			if form.point5.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point5.data
				out.append(news)

			point={}
			point['title']="Cyclone big bag"
			point['value']=form.point6.data	
			sec['inspection_point'].append(point)
			if form.point6.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point6.data
				out.append(news)

			point={}
			point['title']="Tower cone inspection window"
			point['value']=form.point7.data	
			sec['inspection_point'].append(point)
			if form.point7.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point7.data
				out.append(news)


			obs.append(sec)

			sec={}
		

			sec['section']='CONTROL ROOM (LEVEL 3)'
			sec['inspection_point']=[]
		
			point={}
			point['title']="Airlift inspection window"
			point['value']=form.point8.data	
			sec['inspection_point'].append(point)
			if form.point8.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point8.data
				out.append(news)

			point={}
			point['title']="Density Station (body & top)"
			point['value']=form.point9.data	
			sec['inspection_point'].append(point)
			if form.point9.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point9.data
				out.append(news)

			obs.append(sec)

			sec={}
		

			sec['section']='CRUTCHER FLOOR (LEVEL 6)'
			sec['inspection_point']=[]

			point={}
			point['title']="Crutcher dumping spot"
			point['value']=form.point10.data	
			sec['inspection_point'].append(point)
			if form.point10.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point10.data
				out.append(news)

			point={}
			point['title']="STPP & Sulphate conveyor screw platform"
			point['value']=form.point11.data	
			sec['inspection_point'].append(point)
			if form.point11.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point11.data
				out.append(news)

			point={}
			point['title']="Floor"
			point['value']=form.point12.data	
			sec['inspection_point'].append(point)
			if form.point12.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point12.data
				out.append(news)

			obs.append(sec)

			sec={}
		

			sec['section']='MIXER FLOOR (LEVEL 12)'
			sec['inspection_point']=[]

			point={}
			point['title']="Remelt Tank/Storage"
			point['value']=form.point13.data	
			sec['inspection_point'].append(point)
			if form.point13.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point13.data
				out.append(news)

			point={}
			point['title']="STPP & Sulphate dumping spots"
			point['value']=form.point14.data	
			sec['inspection_point'].append(point)
			if form.point14.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point14.data
				out.append(news)

			point={}
			point['title']="Airlift fines big bag return"
			point['value']=form.point15.data	
			sec['inspection_point'].append(point)
			if form.point15.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point15.data
				out.append(news)
			
			point={}
			point['title']="Mix drum (body, door, entrance)"
			point['value']=form.point16.data	
			sec['inspection_point'].append(point)
			if form.point16.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point16.data
				out.append(news)

			point={}
			point['title']="IVAC/PVC"
			point['value']=form.point17.data	
			sec['inspection_point'].append(point)
			if form.point17.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point17.data
				out.append(news)

			point={}
			point['title']="Admix conveyor, hood & platform"
			point['value']=form.point18.data	
			sec['inspection_point'].append(point)
			if form.point18.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point18.data
				out.append(news)

			point={}
			point['title']="Base powder conveyor, hood & platform"
			point['value']=form.point19.data	
			sec['inspection_point'].append(point)
			if form.point19.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point19.data
				out.append(news)

			point={}
			point['title']="Base powder weight belt"
			point['value']=form.point20.data	
			sec['inspection_point'].append(point)
			if form.point20.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point20.data
				out.append(news)

			point={}
			point['title']="Dry scrap dump spot"
			point['value']=form.point21.data	
			sec['inspection_point'].append(point)
			if form.point21.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point21.data
				out.append(news)

			point={}
			point['title']="CVC return chute"
			point['value']=form.point22.data	
			sec['inspection_point'].append(point)
			if form.point22.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point22.data
				out.append(news)

			point={}
			point['title']="Floor"
			point['value']=form.point23.data	
			sec['inspection_point'].append(point)
			if form.point23.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point23.data
				out.append(news)
					

			obs.append(sec)


			sec={}
			

			sec['section']='LIW FLOOR (LEVEL 18)'
			sec['inspection_point']=[]
			
			

			point={}
			point['title']="Admix weight belt"
			point['value']=form.point24.data	
			sec['inspection_point'].append(point)
			if form.point24.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point24.data
				out.append(news)
			
			point={}
			point['title']="IVAC/PVC"
			point['value']=form.point25.data	
			sec['inspection_point'].append(point)
			if form.point25.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point25.data
				out.append(news)

			point={}
			point['title']="Base powder bins"
			point['value']=form.point26.data	
			sec['inspection_point'].append(point)
			if form.point26.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point26.data
				out.append(news)

			point={}
			point['title']="Base powder extraction belts"
			point['value']=form.point27.data	
			sec['inspection_point'].append(point)
			if form.point27.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point27.data
				out.append(news)

			point={}
			point['title']="Enzyme weighing room"
			point['value']=form.point28.data	
			sec['inspection_point'].append(point)
			if form.point28.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point28.data
				out.append(news)
			
			point={}
			point['title']="Floor"
			point['value']=form.point29.data	
			sec['inspection_point'].append(point)
			if form.point29.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point29.data
				out.append(news)

			obs.append(sec)

			sec={}
			

			sec['section']='LEVEL 24/30'
			sec['inspection_point']=[]

			point={}
			point['title']="Airlift screw/rotary valve"
			point['value']=form.point30.data	
			sec['inspection_point'].append(point)
			if form.point30.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point30.data
				out.append(news)
			
			point={}
			point['title']="Fans exhausts"
			point['value']=form.point31.data	
			sec['inspection_point'].append(point)
			if form.point31.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point31.data
				out.append(news)	
					
			point={}
			point['title']="PWS/Extraction belt"
			point['value']=form.point32.data	
			sec['inspection_point'].append(point)
			if form.point32.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point32.data
				out.append(news)

			point={}
			point['title']="CVC filter rotary valve"
			point['value']=form.point33.data	
			sec['inspection_point'].append(point)
			if form.point33.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point33.data
				out.append(news)
			
			point={}
			point['title']="Admix filter rotary valve"
			point['value']=form.point34.data	
			sec['inspection_point'].append(point)
			if form.point34.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point34.data
				out.append(news)	
					
			point={}
			point['title']="A100 Room"
			point['value']=form.point35.data	
			sec['inspection_point'].append(point)
			if form.point35.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point35.data
				out.append(news)	

			point={}
			point['title']="Minors dump spot"
			point['value']=form.point36.data	
			sec['inspection_point'].append(point)
			if form.point36.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point36.data
				out.append(news)
			
			point={}
			point['title']="Gravity separator inspection door"
			point['value']=form.point37.data	
			sec['inspection_point'].append(point)
			if form.point37.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point37.data
				out.append(news)	
					
			point={}
			point['title']="Floor"
			point['value']=form.point38.data	
			sec['inspection_point'].append(point)
			if form.point38.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point38.data
				out.append(news)	

			obs.append(sec)

		else:
			##PSG#	

			obs=[]
			out=[]

			sec={}
			

			sec['section']='MAIN PACKING FLOOR'
			sec['inspection_point']=[]
			
			point={}
			point['title']="Machine Heads"
			point['value']=form.point1.data	
			sec['inspection_point'].append(point)
			if form.point1.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point1.data
				out.append(news)

			point={}
			point['title']="Spillage hoppers"
			point['value']=form.point2.data	
			sec['inspection_point'].append(point)
			if form.point2.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point2.data
				out.append(news)

			point={}
			point['title']="Conveyor &hoods"
			point['value']=form.point3.data	
			sec['inspection_point'].append(point)
			if form.point3.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point3.data
				out.append(news)

			point={}
			point['title']="Reject Cabinets (body & top)"
			point['value']=form.point4.data	
			sec['inspection_point'].append(point)
			if form.point4.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point4.data
				out.append(news)

			point={}
			point['title']="Hose in Reel & Positioned"
			point['value']=form.point5.data	
			sec['inspection_point'].append(point)
			if form.point5.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point5.data
				out.append(news)

			point={}
			point['title']="Floor"
			point['value']=form.point6.data	
			sec['inspection_point'].append(point)
			if form.point6.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point6.data
				out.append(news)

			point={}
			point['title']="CVC Pickup points (PUP)"
			point['value']=form.point7.data	
			sec['inspection_point'].append(point)
			if form.point7.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point7.data
				out.append(news)


			obs.append(sec)

			sec={}
			

			sec['section']='SIFTER FLOORS'
			sec['inspection_point']=[]
			
			point={}
			point['title']="Oversize Bins"
			point['value']=form.point8.data	
			sec['inspection_point'].append(point)
			if form.point8.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point8.data
				out.append(news)

			point={}
			point['title']="Sifter"
			point['value']=form.point9.data	
			sec['inspection_point'].append(point)
			if form.point9.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point9.data
				out.append(news)

			point={}
			point['title']="Machine Top Perspex"
			point['value']=form.point10.data	
			sec['inspection_point'].append(point)
			if form.point10.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point10.data
				out.append(news)

			point={}
			point['title']="CVC Pickup points (PUP)"
			point['value']=form.point11.data	
			sec['inspection_point'].append(point)
			if form.point11.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point11.data
				out.append(news)

			point={}
			point['title']="Extraction Belt"
			point['value']=form.point12.data	
			sec['inspection_point'].append(point)
			if form.point12.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point12.data
				out.append(news)

			point={}
			point['title']="Scissors Lift"
			point['value']=form.point13.data	
			sec['inspection_point'].append(point)
			if form.point13.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point13.data
				out.append(news)

			point={}
			point['title']="Sifter Hopper"
			point['value']=form.point14.data	
			sec['inspection_point'].append(point)
			if form.point14.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point14.data
				out.append(news)

			point={}
			point['title']="Floor"
			point['value']=form.point15.data	
			sec['inspection_point'].append(point)
			if form.point15.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point15.data
				out.append(news)
			
			point={}
			point['title']="Sifter Motors"
			point['value']=form.point16.data	
			sec['inspection_point'].append(point)
			if form.point16.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point16.data
				out.append(news)



			obs.append(sec)


			sec={}
			

			sec['section']='BUGGY FLOOR'
			sec['inspection_point']=[]
			
			point={}
			point['title']="Buggy Filling Station (Inside & Top)"
			point['value']=form.point17.data	
			sec['inspection_point'].append(point)
			if form.point17.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point17.data
				out.append(news)

			point={}
			point['title']="Density Station (body & top)"
			point['value']=form.point18.data	
			sec['inspection_point'].append(point)
			if form.point18.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point18.data
				out.append(news)

			point={}
			point['title']="Buggy tops"
			point['value']=form.point19.data	
			sec['inspection_point'].append(point)
			if form.point19.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point19.data
				out.append(news)

			point={}
			point['title']="Buggy dumping spots"
			point['value']=form.point20.data	
			sec['inspection_point'].append(point)
			if form.point20.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point20.data
				out.append(news)

			point={}
			point['title']="Buggy storage areas"
			point['value']=form.point21.data	
			sec['inspection_point'].append(point)
			if form.point21.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point21.data
				out.append(news)

			point={}
			point['title']="DCS return lines"
			point['value']=form.point22.data	
			sec['inspection_point'].append(point)
			if form.point22.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point22.data
				out.append(news)

			point={}
			point['title']="CVC Pickup points (PUP)"
			point['value']=form.point23.data	
			sec['inspection_point'].append(point)
			if form.point23.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point23.data
				out.append(news)

			point={}
			point['title']="Floor"
			point['value']=form.point24.data	
			sec['inspection_point'].append(point)
			if form.point24.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point24.data
				out.append(news)
			
			
			obs.append(sec)

			sec={}
			

			sec['section']='FILTER FLOOR (LEVEL 12)'
			sec['inspection_point']=[]

			point={}
			point['title']="Floor"
			point['value']=form.point25.data	
			sec['inspection_point'].append(point)
			if form.point25.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point25.data
				out.append(news)

			point={}
			point['title']="DCS Fan exhausts"
			point['value']=form.point26.data	
			sec['inspection_point'].append(point)
			if form.point26.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point26.data
				out.append(news)

			point={}
			point['title']="DCS hopper inspection window"
			point['value']=form.point27.data	
			sec['inspection_point'].append(point)
			if form.point27.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point27.data
				out.append(news)

			point={}
			point['title']="Diverter/Return chute inspection window"
			point['value']=form.point28.data	
			sec['inspection_point'].append(point)
			if form.point28.data < 3:
				news={}
				news['section']=sec['section']
				news['inspection_point']=point['title']
				news['value']=form.point28.data
				out.append(news)

				
			obs.append(sec)


		log=OGC_BOS()

		log.userid = session['userid']
		log.observer = form.observer.data.title()
		log.department = form.department.data
		log.line = form.line.data
		log.shift = form.shift.data
		log.bos_type = form.bos_type.data
		log.team = form.team.data
		log.bos_time = form.bos_time.data
		log.percent = percent
		log.observation=json.dumps(obs)
		log.outages=json.dumps(out)
		log.comment = str(form.comment.data)
		db.session.add(log)
		db.session.commit()		


		return {'status':1,'message':'OGC submitted successfully!'}
		#return {'status':1,'message':json.dumps(obs)}	
