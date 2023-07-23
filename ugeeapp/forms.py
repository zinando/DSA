from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, RadioField, SelectField
from wtforms import  TextAreaField, PasswordField, validators,ValidationError,DateTimeField,StringField,FileField,BooleanField,HiddenField,IntegerField,RadioField,DateField,SelectField,DecimalField,SubmitField,SelectMultipleField
from wtforms.validators import InputRequired, Length, Email,NumberRange
from wtforms.widgets import html_params 
from wtforms.widgets import ListWidget, CheckboxInput,TextArea
from wtforms.fields.datetime import DateTimeField

 

class StopsForm(FlaskForm): 
    reason_one = SelectField('', coerce=int)
    reason_two= SelectField('', coerce=int)
    reason_three = SelectField('', coerce=int)
    reason_four = SelectField('', coerce=int)

class LoginForm(FlaskForm):
    username = StringField('User ID', validators=[InputRequired("UGEE CHEMICALS user ID is required."), Length(max=50)],render_kw={"placeholder":'User ID'})
    password = PasswordField('Password', validators=[InputRequired("Password is required")],render_kw={"placeholder":'Password'})
    remember = BooleanField('remember me')
    submit=SubmitField('Login') 


class AddUserForm(FlaskForm):
    acctype=SelectField("Account Type",coerce=str,choices=[("user","End_User"),("admin","Admin")],validators=[InputRequired("Account type is required.")])
    fname=StringField('First Name', validators=[InputRequired("First name is required.")])
    sname=StringField('Surname', validators=[InputRequired("Surname is required.")])
    email=StringField('UGEE Email', validators=[Email(message='Invalid email'), Length(max=50)])
    password=PasswordField('Temporary Password', validators=[InputRequired("Password is required")],render_kw={"placeholder":'password must be atleast 8 char long and contain  1 number, 1 uppercase letter, 1 lowercase letter'})
    phone=StringField('Mobile',validators=[InputRequired("Mobile phone is required."),Length(max=13)])
    role=SelectMultipleField("User Role",coerce=int,choices=[])
    department=SelectField("Department",choices=[],validators=[InputRequired("Department is required.")])
    adminlevel=SelectField("Admin Level",coerce=int,choices=[(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5")],validators=[InputRequired("Admin level is required.")])
    block_stat=SelectField("Blocked Status",coerce=int,choices=[(0,"0"),(1,"1")],validators=[InputRequired("Block Status is required.")])
    username=StringField('User ID', validators=[InputRequired("UGEE CHEMICALS user ID is required."), Length(max=50)],render_kw={"placeholder":'e.g samuel.n'})
    team=SelectField("Team",coerce=str,choices=[('','Select'),('A','A'),('B','B'),('C','C'),('SUPPORT','SUPPORT'),('NA','NA')])
    submit=SubmitField('Add User')   

class EditUserForm(FlaskForm):
    acctype=SelectField("Account Type",coerce=str,choices=[("user","End_User"),("admin","Admin")],validators=[InputRequired("Account type is required.")])
    fname=StringField('First Name', validators=[InputRequired("First name is required.")])
    sname=StringField('Surname', validators=[InputRequired("Surname is required.")])
    email=StringField('UGEE Email', validators=[Email(message='Invalid email'), Length(max=50)])
    phone=StringField('Mobile',validators=[InputRequired("Mobile phone is required."),Length(max=13)])
    role=SelectMultipleField("User Role",coerce=int,choices=[])
    department=SelectField("Department",coerce=int,choices=[],validators=[InputRequired("Department is required.")])
    adminlevel=SelectField("Admin Level",coerce=int,choices=[(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5")],validators=[InputRequired("Admin level is required.")])
    block_stat=SelectField("Blocked Status",coerce=int,choices=[(0,"0"),(1,"1")],validators=[InputRequired("Block Status is required.")])
    username=StringField('User ID', validators=[InputRequired("UGEE CHEMICALS user ID is required."), Length(max=50)],render_kw={"placeholder":'e.g samuel.n'})
    team=SelectField("Team",coerce=str,choices=[('','Select'),('A','A'),('B','B'),('C','C'),('SUPPORT','SUPPORT'),('NA','NA')])
    submit=SubmitField('Update User')


class forgotPasswordForm(FlaskForm):
    username = StringField('UGEE username', validators=[InputRequired("Username is required"), Length(max=50)],render_kw={"placeholder":'Username e.g samuel.n'})
    password = PasswordField('Password', validators=[InputRequired("Password is required")],render_kw={"placeholder":'new password'}) 
    submit=SubmitField('Send password reset link')

class PassResetForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired("Password is required")])
    password2 = PasswordField('Repeat Password', validators=[InputRequired("Password is required")])
    form_type=HiddenField('',default='2')

class ChangePasswordForm(FlaskForm):
    #old_password = PasswordField('Old Password', validators=[InputRequired("Old Password is required")])
    username = StringField('User ID')
    password = PasswordField('New Password')
    password1 = PasswordField('New Password', validators=[InputRequired("Password is required")])
    password2 = PasswordField('Repeat Password', validators=[InputRequired("Password is required")])
    submit=SubmitField('Change password')

class OGCBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("Line 1","Line 1"),("Line 2","Line 2"),("Line 3","Line 3"),("Line 4A","Line 4A"),("Line 4B","Line 4B")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    #bos_time = DateTimeLocalInput(input_type = "datetime-local")
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score', render_kw={"readonly":True})
    point1=  SelectField("Machine Heads",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})    
    point2=  SelectField("Spillage hoppers",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point3=  SelectField("Conveyor &hoods",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point4=  SelectField("Reject Cabinets (body & top)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point5=  SelectField("Hose in Reel & Positioned",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point6=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point7=  SelectField("CVC Pickup points (PUP)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point8=  SelectField("Oversize Bins",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point9=  SelectField("Sifter",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point10=  SelectField("Machine Top Perspex",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point11=  SelectField("CVC Pickup points (PUP)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point12=  SelectField("Extraction Belt",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point13=  SelectField("Scissors Lift",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point14=  SelectField("Sifter Hopper",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point15=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point16=  SelectField("Sifter Motors",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point17=  SelectField("Buggy Filling Station (Inside & Top)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point18=  SelectField("Density Station (body & top)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point19=  SelectField("Buggy tops",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point20=  SelectField("Buggy dumping spots",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point21=  SelectField("Buggy storage areas",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point22=  SelectField("DCS return lines",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point23=  SelectField("CVC Pickup points (PUP)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point24=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point25=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point26=  SelectField("DCS Fan exhausts",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point27=  SelectField("DCS hopper inspection window",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})
    point28=  SelectField("Diverter/Return chute inspection window",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibilit within and around the check point. Rate the point according to the guideline above."})    
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class SAFETYBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("Line 1","Line 1"),("Line 2","Line 2"),("Line 3","Line 3"),("Line 4A","Line 4A"),("Line 4B","Line 4B"),("NA","N/A")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    #bos_time = DateTimeLocalInput(input_type = "datetime-local") 
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')   
    percent = StringField('Score', render_kw={"readonly":True})
    point1=  SelectField("Use of Safety Lock",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees apply individual locks on local disconnects before working on machines and equipment. Locks have name & phone number."})    
    point2=  SelectField("Waste Bin Usage",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees and contractors dispose waste in the right bin. Only waste on the bin label is found inside the waste bin."})    
    point3=  SelectField("Use of PPE while attending to spills",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees and contractors wear 3M nose mask and Safety Gloves while attending to powder spills."})    
    point4=  SelectField("Use of Scissors Lift",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Daily and previous week Scissors Lift inspections are done, and ALL doors are closed and Locked during lifting operation."})    
    point5=  SelectField("Broken Pallets On The Floor",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Broken pallets with protruding nails are removed from the floor and dropped in the waste bin on production floor and staging area."})         
    comment = TextAreaField('General Comment',render_kw={"placeholder":"Observe and comment on the use of Lifting devices, 5S standard of the area and powder spills. Also, check for the use of Jeweries on the production floor."})
    submit=SubmitField('Submit')

class QABOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("Line 1","Line 1"),("Line 2","Line 2"),("Line 3","Line 3"),("Line 4A","Line 4A"),("Line 4B","Line 4B")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    point1=  SelectField("Line Clearance",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Line clearance, Quality checks & Process audit check are done as at when due and Proper Error correction standards are followed. (The LQC for weight sampe and Operator for Process audit, Line Clearance & TAMU check"})    
    point2=  SelectField("2D Camera",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"2D Camera on all running machine working. (Observe this by putting your hand in front of the camera for 5 seconds and HMI should display NO READ ERROR. If this does not happen then the camera is not working. Inform the operator to shut down the machine and fill a qualit alert)."})    
    point3=  SelectField("FP Weighing",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"ICSL contractors weigh finished products in the polywoven case at EOL and the Daily calibration sheets for all the scaes are updated."})    
    point4=  SelectField("Pack Material Storage",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Packing materials (Films and Polywoven) are stored at assigned location with material GCAS matching GCAS on storage location?"})    
    point5=  SelectField("Stacked Pallets",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Stacked Pallets are stable, wel-stretchwrapped/bound by nets, and good pallets used for palletising."})
    point6=  SelectField("Wash Room",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"The washroom is clean with the forming sets properly arranged."})
    point7=  SelectField("Coding Structure",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Coding Structure are legible and correct on the product, and polywoven: e.g (Product - BN y jjj pppp m tt, MFD mm yy EXP mm yy) and (Polywoven - BN y jjj pppp ln tt MFD dd mm yy EXP dd mm yy). Legend: y-year,j-julian date,p-plant code,m-machine,t-time,m-month,d-date,ln-line number."})                      
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class ViewBOSForm(FlaskForm):

    start =  DateField('Start Date', format="%Y-%m-%d", description = 'Date that you did the BOS')
    end =  DateField('End Date', format="%Y-%m-%d", description = 'Date that you did the BOS')
    bos_type = SelectField("Type of BOS",coerce=str,choices=[("","Select"),("SAFETY","SAFETY"),("QUALITY","QUALITY"),("OGC","OGC")],validators=[InputRequired("type of BOS is required.")])
    submit=SubmitField('View Entries')

class MSG_OGCBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("MSG","MSG"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score', render_kw={"readonly":True})
    point1=  SelectField("Material area",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})    
    point2=  SelectField("Hoist gate",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point3=  SelectField("Airlift feeding belt hood",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point4=  SelectField("Heavies collection spot",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point5=  SelectField("Tower cone",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point6=  SelectField("Cyclone big bag",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point7=  SelectField("Tower cone inspection window",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point8=  SelectField("Airlift inspection window",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point9=  SelectField("Density Station (body & top)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point10=  SelectField("Crutcher dumping spot",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point11=  SelectField("STPP & Sulphate conveyor screw platform",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point12=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point13=  SelectField("Remelt Tank/Storage",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point14=  SelectField("STPP & Sulphate dumping spots",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point15=  SelectField("Airlift fines big bag return",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point16=  SelectField("Mix drum (body, door, entrance)",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point17=  SelectField("IVAC/PVC",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point18=  SelectField("Admix conveyor, hood & platform",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point19=  SelectField("Base powder conveyor, hood & platform",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point20=  SelectField("Base powder weight belt",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point21=  SelectField("Dry scrap dump spot",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point22=  SelectField("CVC return chute",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point23=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point24=  SelectField("Admix weight belt",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point25=  SelectField("IVAC/PVC",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point26=  SelectField("Base powder bins",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point27=  SelectField("Base powder extraction belts",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point28=  SelectField("Enzyme weighing room",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point29=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point30=  SelectField("Airlift screw/rotary valve",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point31=  SelectField("Fans exhausts",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point32=  SelectField("PWS/Extraction belt",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point33=  SelectField("CVC filter rotary valve",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point34=  SelectField("Admix filter rotary valve",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point35=  SelectField("A100 Room",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point36=  SelectField("Minors dump spot",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point37=  SelectField("Gravity separator inspection door",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})
    point38=  SelectField("Floor",coerce=int,choices=[(0,"Select"),(4,"4"),(3,"3"),(2,"2"),(1,"1")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Check for product visibility within and around the check point. Rate the point according to the guideline above."})                                                                                    
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')    
    
class MSG_SAFETYBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("MSG","MSG"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    #bos_time = DateTimeLocalInput(input_type = "datetime-local") 
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')   
    percent = StringField('Score', render_kw={"readonly":True})
    point1=  SelectField("Use of Safety Lock",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees apply personal locks containing his/her name & phone number to lock-out local disconnects (Pneumatic & Electrical) before performing tasks on equipment."})    
    point2=  SelectField("QRP For Non-routine tasks",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employee uses detailed QRP for non-routine/non-procedure tasks. Employee performing a maintenance task uses document procedure (SIMTWW/JSP/Job Aid etc)."})    
    point3=  SelectField("Use of Appropriate PPE",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employee performing maintenance task wears appropriate PPE (stipulated by procedure) to execute the task."})    
    point4=  SelectField("Use of Ear Muffs at level 18",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees and contractors wear ear muffs or ear plugs when vibrator is ON at level 18"})    
    point5=  SelectField("Replacement of Flange Covers",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employee replaced flange covers for high pressure slurry lines & corrosive liquid lines after intervention."})         
    comment = TextAreaField('General Comment',render_kw={"placeholder":"Observe and comment on the use of Lifting devices, 5S standard of the area and powder spills. Also, check for the use of Jeweries on the production floor."})
    submit=SubmitField('Submit') 


class MSG_QABOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("MSG","MSG"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("TEAM","Team BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    #bos_time = DateTimeLocalInput(input_type = "datetime-local")
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    point1=  SelectField("Operating Area Doors",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are the doors in the operating area across all floors working and net doors always closed?"})    
    point2=  SelectField("Insecticutor Bulbs",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all insecticutor bulbs ON? (specify which floor insecticutor bulb is defective)."})    
    point3=  SelectField("Reblend Hopper",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Is reblend hopper at level 24 covered when not in use?"})    
    point4=  SelectField("Material Storage",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all raw materials stored at assigned storage location with material GCAS matching GCAS on storage location? (Check that material GCAS matches the GCAS on labels). Are all release labels removed from used EW basse cubitainer & bulk solids bags before reuse?"})    
    point5=  SelectField("Bar Code Scanner on Hoists",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Bar Code Scanner on all active hoists (dumpspots) working (Level 12&24). (Observe this by using the bar code scanner to scan the bar code on the specifc material label, check if the hoist is activated by the scanning, if not, inform the Team and QA leaders immediately and log quality alert)."})
    point6=  SelectField("Calibration Checks on Scales",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are calibration checks timely conducted for all weighing scales: Satellite laboratory? (Ask for calibration records)."})
    point7=  SelectField("Other Quality Outages",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"There are no other observable quality outages on the operating floor? (If NO, please specify in the comment section). "})                      
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')               

class LeadershipBOSForm(FlaskForm):
    department = SelectField("Department to Observe",coerce=str,choices=[("MSG","MSG"),("PSG","PSG"),("QA","Lab Q-BOS"),("WHSE","WHSE")])
    bos_type = SelectField("Observation Type",coerce=str,choices=[("0","Select"),("SAFETY","SAFETY"),("QUALITY","QUALITY"),("OGC","OGC")])
    submit=SubmitField('Submit')

class WHSE_QABOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("WHSE","WHSE"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("WHSE","WHSE BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    point1=  SelectField("Tops of Finished Products",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are the tops of finished products in their location  covered with tie sheets?  {if less than 5 pallets are seen without tie sheets, add as comment}"})    
    point2=  SelectField("Finished Products Storage",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are finished products stored in-line with  their assigned stock  locators? (Check that different finished product SKU's are not  co-stored, except extended staging area,picking location and shipping areas)"})    
    point3=  SelectField("RSDs",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are  RSDs closed when not in use and warehouse is not exposed? Is there   daylight entry from under when RSD is shut?  (Check that back-up tarpaulin curtain  are used when docks  are faulty)"})    
    point4=  SelectField("Finished Products Palletising",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are finished products  stored on good pallets ?  (Check  that products are not stored on broken or infested Pallets {Minimum of 5 pallets must be seen})"})    
    point5=  SelectField("Insecticutor Bulbs",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all the insecticutors powered and working,  {if less than 5 pallets are seen without tie sheets, add as comment}"})
    point6=  SelectField("Shipment Trucks",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are the interior of the shipment trucks lined with polythene before FP cases are dead piled."})
    point7=  SelectField("FPs Pallet Storage",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are the FP pallets stored in line with 5S. (Add as a comment if  less than 6  pallets seen)"})
    point8=  SelectField("FPs Pallet Load Standards",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are the FP pallets loads at s tandard? Checked that there is no fallen pallet loads, no leaking or burst /crushed cases"})
    point9=  SelectField("Finished Products Shipment",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are  Finished products shipped in line with FIFO?(Check that there is no batch on SAP NG02 location which is older  than the one being shipped. The shift shipment technician will share SAP snapshot with you)"})
    point10=  SelectField("Evacuated Finished Products",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are evacuated Finished products from production line stored at the designated place? (Check  that finished product evacuated from the lines are not stored at the shipment area, shipment activities are clearly segregated from FP received into warehouse activity)"})                                              
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class WHSE_SAFETYBOSForm(FlaskForm): #SNO FP BOS
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("WHSE","WHSE"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("WHSE FP","WHSE FP BOS"),("LEADERSHIP FP","Leadership FP BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    point1=  SelectField("Forklift Operators",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Contractors operating forklift in the warehouse wear seat belt"})    
    point2=  SelectField("Trucks",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Trucks are chocked  with a pair of chock at the wheel."})    
    point3=  SelectField("Motor Boys",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Motor Boys wears reflective vest while directing a driver reversing truck"})    
    point4=  SelectField("Forklift Tyres",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Forklift tyres are not worn and no critical safety defect  found on forklift ( e.g burnt lamp or horn)."})
    point5=  SelectField("Pallets Outside 5S",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Pallets are not stored outside of 5's and not on walkways or motorways at the pallet shed. (Check that pallets are storeed within 5's and not  outside the pallet shed , either on  walkway or motorway)"})                                              
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class WHSE_RPMBOSForm(FlaskForm): #SNO RPM BOS
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("WHSE","WHSE"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("WHSE RPM","WHSE RPM BOS"),("LEADERSHIP RPM","Leadership RPM BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    point1=  SelectField("Trucks",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Trucks are chocked  with a pair of chock at the wheel."})    
    point2=  SelectField("Forklift Operators",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Contractors operating forklift in the warehouse wear seat belt"})    
    point3=  SelectField("Spills",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Employees and contractors clean powder and liquid spills immediately they occur."})                                              
    point4=  SelectField("Pallets Outside 5S",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Pallets are not stored outside of 5's and not on walkways or motorways at the pallet shed. (Check that pallets are storeed within 5's and not  outside the pallet shed , either on  walkway or motorway)"})    
    point5=  SelectField("Forklift Tyres",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Forklift tyres are not worn and no critical safety defect  found on forklift ( e.g burnt lamp or horn)."})
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class WHSE_OGCBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("WHSE","WHSE"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("WHSE","WHSE BOS"),("LEADERSHIP","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})

class LAB_SAFETYBOSForm(FlaskForm): 
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("LAB","LAB"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("LAB BOS","LAB BOS"),("LEADERSHIP BOS","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    
    point1=  SelectField("WorkBench",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Work Bench is free of any glassware , chemicals, reagent bottles used for analysis and only lablelled DI beaker is on work bench when no analysis is in progress."})    
    point2=  SelectField("Desicator",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Exposed chemicals are not left in the Desicator after usage."})    
    point3=  SelectField("Analyst",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Analyst used rubber handglove while carrying acid and all other corrosive and fuming chemicals."})    
    point4=  SelectField("Area 5S Standard",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"All chemicals are found in the area allotted to them. Expired chemicals are found in the allotted space ONLY. The entire place is clean, tidy and free of dust."})
    point5=  SelectField("Balances and Dusthood",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"All balances (Top and Analytical balances ) and dusthood area are free from powder spill after all analysis is completed."})                                              
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class LAB_QABOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("LAB","LAB"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("LAB BOS","LAB BOS"),("LEADERSHIP BOS","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    
    point1=  SelectField("Analysis Records",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all records of analysis entered into the lab note books directly and are the lab notebooks (RPM, Regulatory, etc)  completely filled and quality issues are fully documented and tracked? (Checked that they filled to  date, peer reviewed and error correction are done, check if there are pieces of paper with analysis record in the lab) Are BPRs, RM  & PM COA stored in the designated area."})    
    point2=  SelectField("Lab Equipment",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all the  equipment labeled, cleaned and well calibrated, and calibration tracking sheet updated? (Look at calibration records on each equipment and ask for calibration certificates for external calibration, check the equipment serial number and model number versus Tracking sheet for correctness)"})    
    point3=  SelectField("Lab Area Cleanliness",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Is the sample retention area and  lab area clean and tidy, table cleared after each analysis and are used samples discarded. (Check entire cleanliness of area and adherence to 5S standards, check that RM, PM and FP samples not more than one day is kept on the bench)? "})    
    point4=  SelectField("Lab Excell Worksheets",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all Laboratory excell worksheet  (FP Analytical Sheet, BH Base sheet, DDS worksheets, RM Calculationn sheet, Concentration Calc. software, e.t.c) passworded?,(open any laboratory worksheet and check for password protecton on calculation columns on the worksheet)"})    
    point5=  SelectField("Storage of Chemicals & Reagents",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all chemicals and reagents stored in designated places, labelled and laboratory solutions unexpired? (Pick a bottle of any reagent, check its label, trace it to the chemical used in its preparation, When was it opened? Does it match with what you have on the Chemical consumption sheet?)"})
    point6=  SelectField("Lab PCs",coerce=int,choices=[(0,"Select"),(1,"YES"),(0,"NO")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Are all Laboratory PC set to auto-lock after Three (3) minutes (Excuding Gallery PC set to Twenty (20) minutes)?, (Pick any Lab PC including SATLAB, open the PC and check after Three (3) for the set auto-lock setting)"})
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class UTILITY_SAFETYBOSForm(FlaskForm):
     
    observer = StringField('Full Name', validators=[InputRequired("Full name is required.")])
    department = SelectField("Observer's Department",coerce=int,choices=[(1,"PSG"),(2,"MSG"),(3,"QA"),(4,"WHSE"),(6,"HR")],validators=[InputRequired("Department is required.")])
    line = SelectField("Line",coerce=str,choices=[("UTILITY","UTILITY"),("LEADERSHIP","Leadership")],validators=[InputRequired("Line is required.")])
    shift = SelectField("Shift",coerce=str,choices=[("N/A","N/A"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    bos_type = SelectField("BOS Type",coerce=str,choices=[("UTILITY BOS","UTILITY BOS"),("LEADERSHIP BOS","Leadership BOS")],validators=[InputRequired(" BOS Type is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("N/A","N/A")])    
    bos_time =  DateField('BOS Date', format="%Y-%m-%d", description = 'Date that you did the BOS')    
    percent = StringField('Score',render_kw={"readonly":True})
    
    point1=  SelectField("Use of Earmuffs",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"Ear muffs is worn inside the Generator yard."})    
    point2=  SelectField("Spills Handling",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"No Oil/Water/Diesel spillage on the floor inside the Generator yard."})    
    point3=  SelectField("Drainage",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"No oil / Diesel contamination inside drainage behind the Generator yard."})    
    point4=  SelectField("Generator Doors",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"All the Generator Canopy door and the mesh door are closed properly while nobody inside the Generator yard."})
    point5=  SelectField("Work Areas",coerce=int,choices=[(0,"Select"),(1,"SAFE"),(0,"AT RISK")],validators=[InputRequired("This is required.")],
            render_kw={"title":"No spare parts/Tools are not littering the work areas."})                                              
    comment = TextAreaField('General Comment')
    submit=SubmitField('Submit')

class PSGProductionForm(FlaskForm):
    pdate = DateField('Production Date', format="%Y-%m-%d", description = 'Date that you did the BOS')
    line = SelectField("Production Line",coerce=int,choices=[(0,"Select"),(1,"Line 1"),(2,"Line 2"),(4,"Line 4")],validators=[InputRequired("Line is required.")])
    machine = SelectMultipleField("Select Machines",coerce=str,choices=[],validators=[InputRequired("Line is required.")],render_kw={'data-value': 'select2',"multiple" : "multiple"})
    productcode = SelectField("Product",coerce=int,choices=[],validators=[InputRequired("Product code is required")])
    start = StringField('Start Time', validators=[InputRequired("Start time is required.")])
    end = StringField('End Time', validators=[InputRequired("End time is required.")])
    team = SelectField("Team on Duty",coerce=str,choices=[("0","Select"),("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    shift = SelectField("Shift",coerce=str,choices=[("0","Select"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    cases = IntegerField('Cases Produced', validators=[InputRequired("Cases is required.")])
    #operator = StringField('Operator', validators=[InputRequired("Operator name time is required.")])
    #upst & updt are added as optional fields with html input

class SKUEntryForm(FlaskForm):
    productcode =  StringField('Product Code', validators=[InputRequired("Product Code is required.")])
    #gcas =  StringField('GCAS Number', validators=[InputRequired("GCAS Number is required.")])    
    weight = IntegerField('Reference Weight', validators=[InputRequired("Cases is required.")],render_kw={'placeholder': 'e.g 22 for 22g'})
    description = StringField('Description', validators=[InputRequired("Description is required.")],render_kw={'placeholder': 'e.g 22g ARIEL kali NG'})
    submit=SubmitField('Submit')

class EquipmentEntryForm(FlaskForm):
    name=StringField('Machine Name', validators=[InputRequired("Machine name is required.")],render_kw={'placeholder': 'e.g ML U, UVA A'})
    line_number = SelectField("Line Number",coerce=int,choices=[(4,"Line 4"),(3,"Line 3"),(2,"Line 2"),(1,"Line 1")],validators=[InputRequired("Line Number is required.")])
    lane=SelectField("Lane",coerce=str,choices=[("ML","MULTILANE"),("UVA","UVA")],validators=[InputRequired("Lane is required.")])
    mcode=StringField('Machine CODE', validators=[InputRequired("Machine code is required.")],render_kw={'placeholder': 'e.g U, A'})
    #sku=SelectField("SKU",coerce=int,choices=[],validators=[InputRequired("SKU is required.")])
    #line_speed = IntegerField('Machine Speed')
    #bps = IntegerField('Bags Per String')
    #spc = IntegerField('Strings Per Case')
    #cpp = IntegerField('Cases Per Pallet')        
    submit=SubmitField('Submit')

class ViewPSGResultForm(FlaskForm):
    start =  DateField('Start Date', format="%Y-%m-%d", description = 'Date of production start')
    end =  DateField('End Date', format="%Y-%m-%d", description = 'Date of production end')
    machine = SelectMultipleField("Select Machines",coerce=str,choices=[],validators=[InputRequired("Machine is required.")],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    shift = SelectField("Shift",coerce=str,choices=[("0","Select"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    team = SelectField("Team",coerce=str,choices=[("0","Select"),("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    submit=SubmitField('View Result')

class PSGProductionEntryForm(FlaskForm):
    start =  DateField('Start Date', format="%Y-%m-%d", description = 'Date of production start')
    end =  DateField('End Date', format="%Y-%m-%d", description = 'Date of production end')
    machine = SelectMultipleField("Select Machines",coerce=str,choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    shift = SelectField("Shift",coerce=str,choices=[("0","Select"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    #team = SelectField("Team",coerce=str,choices=[("0","Select"),("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    submit=SubmitField('View Entries')

class AddRoles(FlaskForm):
    name = StringField('Title', validators=[InputRequired("Role title is required.")])
    description = StringField('Description of Role')
    skills = SelectMultipleField("Skill Set",choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})
    rnr = TextAreaField('Roles & Responsibilities: separate each line by a semi-colon')
    report_to = SelectField("Reports To",coerce=int,choices=[(0,'None')],render_kw={'title':'Which higher role will this role report to?'})
    submit=SubmitField('Create')

class PSGProductionReportForm(FlaskForm):
    start =  DateField('Start Date', format="%Y-%m-%d", description = 'Date of production start')
    end =  DateField('End Date', format="%Y-%m-%d", description = 'Date of production end')
    machine = SelectMultipleField("Select Machines",coerce=str,choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    #shift = SelectField("Shift",coerce=str,choices=[("0","Select"),("Morning","Morning"),("Afternoon","Afternoon"),("Night","Night")],validators=[InputRequired("Shift is required.")])
    #team = SelectField("Team",coerce=str,choices=[("0","Select"),("TEAM A","TEAM A"),("TEAM B","TEAM B"),("TEAM C","TEAM C")])
    include_downtime = SelectMultipleField("Include Downtime",coerce=int,choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    exclude_downtime = SelectMultipleField("Exclude Downtime",coerce=int,choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    transformation = SelectMultipleField("Transformation",coerce=int,choices=[],render_kw={'data-value': 'select2',"multiple" : "multiple"})        
    submit=SubmitField('Run Report')    