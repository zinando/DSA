import ipaddress
from flask import Markup
from uuid import uuid4
from ugeeapp.models import StopEvent,StopCode,ReasonOne,ReasonTwo,ReasonTri,ReasonFour,Equipment,User,Production
from datetime import datetime
#from weasyprint import HTML
import random
import string
import time
import re #pip install regex
import json
from slugify import slugify
import requests
from ugeeapp import db,app


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


def validate_ip_address(ip):
    try:
        if ipaddress.ip_address(ip):
            return True
        else:
            return False
    except:
        return False


def generateToken():
     return uuid4()


def check_date(value):
    mydate = value.split('-')  # expecting 2012-09-12
    try:
        checkdate = datetime(int(mydate[0]), int(mydate[1]),int(mydate[2]))
        return True
    except :
        return False


def randomStringwithDigitsAndSymbols(stringLength=8):
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))

def randomString(stringLength=8):
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))


def check_password_strengthV1(password):

    if  len(password) < 8:
        return {"status":2,"Message":"Password cannot be less than 8 chracters "}
   

    if re.search('[0-9]',password) is None:
        return {"status":2,"Message":"Password must include at least one number!" }

    
    if  re.search("[a-zA-Z]",password)  is None:
        return  {"status":2,"Message":"Password must include at least one letter!" }
        

    if re.search('[A-Z]',password) is None:
        return  {"status":2,"Message":"Password must include at least one CAPITAL letter!" }

    return  {"status":1,"Message":"Password Ok" }

def check_password_strength(password):
    error=[]
    if  len(password) < 8:
        error.append("Password cannot be less than 8 chracters ")

    if re.search('[0-9]',password) is None:
       error.append("Password must include at least one number!" )
         

    if  re.search("[a-zA-Z]",password)  is None:
        error.append("Password must include at least one letter!" )
        

    if re.search('[A-Z]',password) is None:
        error.append("Password must include at least one CAPITAL letter!" )

    return  error

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True


def sanitizeHtml(value, base_url=None):
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = 'p i strong b u a h1 h2 h3 pre br img'.split()
    validAttrs = 'href src width height'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')
    
def cj(data):
    return data
    


def cleandata(data):
    if isinstance(data, str):
        
        return data.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace('\u20a6','N')
    if isinstance(data, list):
        return [cleandata(item) for item in data]
    if isinstance(data, dict):
        return {cleandata(key): cleandata(value) for (key, value) in data.items()}
    return data


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

def slug(text):
    return slugify(text)

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength)) 

def randomNumbs(numberLength=8):    
    my_date = datetime.now()
    tup = my_date.timetuple()
    myne = str(time.mktime(tup))

    numbers = myne[:10]
    return ''.join(random.choice(numbers) for i in range(numberLength))
    
def shorten_url(long_url):
    import requests
    import urllib.parse 
    url="{}{}".format("https://api-ssl.bitly.com/v3/shorten?access_token=285126563716a1a7a3d49f2bde1babf120c75eb1&longUrl=",urllib.parse.quote_plus(long_url))
    headers = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 6.0; MS Web Services Client Protocol 4.0.30319.239)"}
    response=requests.request('GET',url, headers=headers,timeout=60)
    jdata=json.loads(response.text)

    return jdata 

def get_date_from_datetime(datime):

        end=datetime.strptime(str(datime), "%Y-%m-%d %H:%M:%S.%f")
        #t=str(end.year)+"/"+str(end.month)+"/"+str(end.day)+" "+str(end.hour)+":"+str(end.minute)+":"+str(end.second)
        t={}
        t['date']=str(end.year)+"-"+str(end.month)+"-"+str(end.day)
        t['time']=str(end.hour)+":"+str(end.minute)+":"+str(end.second)
        return t  

def calc_skedule_time(start,end):

        s=str(start)
        s1=datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

        e=str(end)
        e1=datetime.strptime(e, "%Y-%m-%d %H:%M:%S.%f")
        t = e1 - s1
        mytime=divmod(t.total_seconds(), 60)
        tyme=int(mytime[0])
        
                
        return tyme

def calc_skedule_timeXY(start,end):

        s=str(start)
        s1=datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

        e=str(end)
        e1=datetime.strptime(e, "%Y-%m-%d %H:%M:%S")
        t = e1 - s1
        mytime=divmod(t.total_seconds(), 60)
        tyme=int(mytime[0])

def calc_skedule_timeXy(start,end):

        s=str(start)
        s1=datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

        e=str(end)
        e1=datetime.strptime(e, "%Y-%m-%d %H:%M:%S.%f")
        t = e1 - s1
        mytime=divmod(t.total_seconds(), 60)
        tyme=int(mytime[0])
        
                
        return tyme

def calc_skedule_timexY(start,end):

        s=str(start)
        s1=datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

        e=str(end)
        e1=datetime.strptime(e, "%Y-%m-%d %H:%M:%S")
        t = e1 - s1
        mytime=divmod(t.total_seconds(), 60)
        tyme=int(mytime[0])
        
                
        return tyme    

def get_uptime(sid,start_time,machine):
    
    stop=db.session.query(StopEvent).filter(StopEvent.machine==machine,StopEvent.end_time<=start_time).order_by(StopEvent.start_time.desc()).first()
    stop_time=str(stop.end_time)
    s=datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S.%f")
    up_time=start_time-s

    return up_time

def format_datetyme(datime):

        old=datetime.strptime(str(datime), "%Y-%m-%d, %H:%M:%S.%f")
        new=old.strftime("%Y-%m-%d %H:%M:%S.%f")
        
        return new
