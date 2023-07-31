from flask import Flask
from sqlalchemy.sql import func
from flask_sqlalchemy  import SQLAlchemy
from ugeeapp import db
from flask_login import UserMixin


class StopEvent(db.Model):
	__tablename__ = 'stop_event'

	sid = db.Column(db.Integer, primary_key=True)
	machine=db.Column(db.String(6), nullable=False)
	start_time= db.Column(db.DateTime, default=func.now())
	end_time=db.Column(db.DateTime, nullable=True)
	up_time=db.Column(db.DateTime, nullable=True)
	down_time =db.Column(db.DateTime, nullable=True)
	error = db.Column(db.Integer, nullable=True)
	reason_level_one=db.Column(db.Integer, nullable=True)
	reason_level_two=db.Column(db.Integer, nullable=True)
	reason_level_three=db.Column(db.Integer, nullable=True)
	reason_level_four=db.Column(db.Integer, nullable=True)
	breakdown =db.Column(db.Integer, default=0)
	delete_stat =db.Column(db.Integer, default=0)
	comment = db.Column(db.String(625), nullable=True)
	status= db.Column(db.Integer, default=0)

class StopCode(db.Model):
	__tablename__ = 'causes'

	cid = db.Column(db.Integer, primary_key=True)
	cause=db.Column(db.String(225), nullable=True)
	cause_code = db.Column(db.Integer, nullable=False)

class ReasonOne(db.Model):
	__tablename__ = 'reason_one'

	rid = db.Column(db.Integer, primary_key=True)
	reason = db.Column(db.String(225), nullable=True)

class ReasonTwo(db.Model):
	__tablename__ = 'reason_two'

	tid = db.Column(db.Integer, primary_key=True)
	reason_one=db.Column(db.Integer, nullable=True)
	reason = db.Column(db.String(225), nullable=True)
	end_tag= db.Column(db.Integer, default=0)

class ReasonTri(db.Model):
	__tablename__ = 'reason_three'

	trid = db.Column(db.Integer, primary_key=True)
	reason_two=db.Column(db.Integer, nullable=True)
	reason = db.Column(db.String(225), nullable=True)
	end_tag= db.Column(db.Integer, default=0)

class ReasonFour(db.Model):
	__tablename__ = 'reason_four'

	fid = db.Column(db.Integer, primary_key=True)
	reason_tri=db.Column(db.Integer, nullable=True)
	reason = db.Column(db.String(225), nullable=True)
	end_tag= db.Column(db.Integer, default=0)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    mid = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=True)
    line_number = db.Column(db.Integer, nullable=True) #e.g line 4
    lane=db.Column(db.String(50), nullable=True) #ML
    m_code=db.Column(db.String(6), nullable=True) #U
    product_params=db.Column(db.String(6500), nullable=True,default=None)

class User(db.Model):
    __tablename__ = 'users'

    userid = db.Column(db.Integer, primary_key=True)    
    acctype = db.Column(db.Enum('user','admin'), default='user')
    fname = db.Column(db.String(45), nullable=False)
    sname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(45), nullable=False,unique=True)
    password = db.Column(db.String(255))
    temp_password = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(45), nullable=True)
    role=db.Column(db.Integer) #the major role held by user
    department=db.Column(db.Integer)
    adminlevel = db.Column(db.Integer, nullable=False,default=0) 
    created =  db.Column(db.DateTime, default=func.now())
    createdby = db.Column(db.Integer, nullable=False)
    block_stat = db.Column(db.Integer, nullable=False,default=0)    
    passresetcode = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, default=func.now())
    last_password_reset=db.Column(db.String(50),nullable=True)    
    activated=db.Column(db.Integer,default=0)
    activatecode=db.Column(db.String(255),nullable=True)
    last_activation_code_time=db.Column(db.DateTime())
    username = db.Column(db.String(45), nullable=True)
    user_roles = db.Column(db.String(650), nullable=True,default='') ##includes additional roles held by user
    team = db.Column(db.String(45), nullable=True)

    def get_id(self): 
        return (self.userid)

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False

class Alogin(db.Model):
    __tablename__ = 'alogin'

    login_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    usertype = db.Column(db.String(30), nullable=False)
    loginTime = db.Column(db.String(50), nullable=False)
    loginDate = db.Column(db.String(50), nullable=False)
    lcount = db.Column(db.BigInteger, nullable=False)
    loginkey = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(30), nullable=False)

class Asession(db.Model):
    __tablename__ = 'asessions'

    id = db.Column(db.Integer, primary_key=True)
    set_time = db.Column(db.String(45), nullable=False)
    data = db.Column(db.Text, nullable=False)
    session_key = db.Column(db.Text, nullable=False)

class AdminAuditlog(db.Model):
    __tablename__ = 'admin_auditlog'

    useraction_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    adminuser = db.Column(db.String(50), nullable=False)
    regdate = db.Column(db.DateTime, default=func.now())
    narration = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(30), nullable=False)

class FailedLogin(db.Model):
    __tablename__ = 'failed_logins'     

    failedid = db.Column(db.BigInteger, primary_key=True)
    usertype = db.Column(db.String(30), nullable=False)
    logon_email = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(30), nullable=False)
    is_real_user = db.Column(db.Integer, nullable=False)
    regtime = db.Column(db.String(30), nullable=False)

class Department(db.Model):
    __tablename__ = 'departments'

    did = db.Column(db.Integer, primary_key=True)
    abbr = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    hod = db.Column(db.Integer, nullable=False)

class OGC_BOS(db.Model):
    __tablename__ = 'ogc_bos'

    ogcid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.BigInteger, nullable=False)
    observer = db.Column(db.String(60), nullable=False)
    department = db.Column(db.BigInteger, nullable=False)
    line = db.Column(db.String(50), nullable=False)
    shift = db.Column(db.String(50), nullable=False)
    bos_type = db.Column(db.String(50), nullable=False)
    team = db.Column(db.String(50), nullable=True)
    bos_time = db.Column(db.DateTime, nullable=False)    
    percent = db.Column(db.Numeric(18, 2), nullable=False)
    observation=db.Column(db.String(650), nullable=True,default='')
    outages=db.Column(db.String(650), nullable=True,default='')
    comment = db.Column(db.String(265), nullable=True)
    action = db.Column(db.String(265), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())

class QA_BOS(db.Model):
    __tablename__ = 'qa_bos'

    qid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.BigInteger, nullable=False)
    observer = db.Column(db.String(60), nullable=False)
    department = db.Column(db.BigInteger, nullable=False)
    line = db.Column(db.String(50), nullable=False)
    shift = db.Column(db.String(50), nullable=False)
    bos_type = db.Column(db.String(50), nullable=False)
    team = db.Column(db.String(50), nullable=True)
    bos_time = db.Column(db.DateTime, nullable=False)    
    percent = db.Column(db.Numeric(18, 2), nullable=False)
    observation=db.Column(db.String(650), nullable=True,default='')
    outages=db.Column(db.String(650), nullable=True,default='')
    comment = db.Column(db.String(265), nullable=True)
    action = db.Column(db.String(265), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())

class SAFETY_BOS(db.Model):
    __tablename__ = 'safety_bos'

    sid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.BigInteger, nullable=False)
    observer = db.Column(db.String(60), nullable=False)
    department = db.Column(db.BigInteger, nullable=False)
    line = db.Column(db.String(50), nullable=False)
    shift = db.Column(db.String(50), nullable=False)
    bos_type = db.Column(db.String(50), nullable=False)
    team = db.Column(db.String(50), nullable=True)
    bos_time = db.Column(db.DateTime, nullable=False)    
    percent = db.Column(db.Numeric(18, 2), nullable=False)
    observation=db.Column(db.String(650), nullable=True,default='')
    outages=db.Column(db.String(650), nullable=True,default='')
    comment = db.Column(db.String(265), nullable=True)
    action = db.Column(db.String(265), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())   

class Production(db.Model):
    __tablename__ = 'production'

    pid = db.Column(db.Integer, primary_key=True)
    prodate = db.Column(db.Date, nullable=False)
    product_code = db.Column(db.String(50), nullable=True)
    mcode=db.Column(db.String(6), nullable=True) #U
    product_params= db.Column(db.String(655), nullable=True,default=None)
    line = db.Column(db.String(50), nullable=True,default=None) 
    shift = db.Column(db.String(50), nullable=True)
    reliability = db.Column(db.Numeric(18, 2), nullable=True)
    msu = db.Column(db.Numeric(18, 2), nullable=True)
    volume = db.Column(db.Numeric(18, 2), nullable=True)
    exp_volume = db.Column(db.Numeric(18, 2), nullable=True)
    skedule_time = db.Column(db.BigInteger, nullable=True)
    downtime = db.Column(db.BigInteger, nullable=True)
    uptime = db.Column(db.Integer, nullable=True)
    upst = db.Column(db.Integer, nullable=True) 
    updt = db.Column(db.BigInteger, nullable=True)
    major_loss = db.Column(db.String(655), nullable=True,default=None) #a dic with ffg keys: updt,descriptn,upst for 3 events  
    scrap = db.Column(db.Integer, nullable=True) # ID for scrap table entry for the shift
    team = db.Column(db.String(50), nullable=True)
    cases = db.Column(db.String(655), nullable=True,default=None)
    start_tyme = db.Column(db.DateTime, nullable=True)
    end_tyme = db.Column(db.DateTime, nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())

class MaterialLoss(db.Model):
    __tablename__ = 'material_scrap'

    mlid =  db.Column(db.Integer, primary_key=True)
    scrap = db.Column(db.String(650), nullable=True)
    shift = db.Column(db.String(50), nullable=True)
    team = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    scrap_type = db.Column(db.String(50), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())

class SKU(db.Model):
    __tablename__ = 'skus'

    skuid = db.Column(db.Integer, primary_key=True)
    productcode = db.Column(db.String(50), nullable=True)
    gcas = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    brand = db.Column(db.String(50), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now())
    
class ProcessParams(db.Model):
    __tablename__ = 'process_params'

    ppid = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer, nullable=True)
    line = db.Column(db.Integer, nullable=True)
    technology = db.Column(db.String(50), nullable=True)
    parameters = db.Column(db.String(6550), nullable=True)
    regdate = db.Column(db.DateTime, default=func.now()) 

class Trainings(db.Model):

    __tablename__ = 'trainings'

    tid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    owner = db.Column(db.Integer, nullable=True)
    expiry = db.Column(db.Integer, nullable=True)
    last_review = db.Column(db.DateTime, nullable=True)
    quiz_link = db.Column(db.String(650), nullable=True)
    suc_id = db.Column(db.Integer, nullable=True)
    doc_link = db.Column(db.String(650), nullable=True)
    pass_mark = db.Column(db.Integer, nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    extra_resource = db.Column(db.String(650), nullable=True) #will hold json data in form of arrays
    t_code = db.Column(db.String(50), nullable=True)
    suc = db.Column(db.Integer, default=0) #if suc is required or not

class MyQualification(db.Model):

    __tablename__ = 'my_qualifications'

    qid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=True)
    q_date = db.Column(db.DateTime, nullable=True)
    training_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(250), nullable=False)
    department = db.Column(db.String(50), nullable=False) #e.g PSG, QA
    score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum('PASSED','REPEAT'), nullable=True)    
    suc_status = db.Column(db.Enum('completed','pending','na'), default='na')
    suc_q_date = db.Column(db.DateTime, nullable=True)
    percent = db.Column(db.Integer, nullable=True)
    #attr for manual qualification
    qualifier = db.Column(db.Integer, nullable=True) #person that qualified the user on paper
    logged_by = db.Column(db.Integer, nullable=True) #person who logged the manual qualification

class StepupCards(db.Model):
    __tablename__ = 'stepup_cards'

    sucid = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.String(250), nullable=False)    
    last_review = db.Column(db.DateTime, default=func.now())
    suc_link = db.Column(db.String(650), nullable=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    rid = db.Column(db.Integer, primary_key=True)    
    rname = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    trainings = db.Column(db.String(6550), nullable=True)
    rnr = db.Column(db.String(6550), nullable=True) 
    report_to = db.Column(db.Integer, nullable=True) #role id that this role reports to
    regdate = db.Column(db.DateTime, default=func.now())
    

