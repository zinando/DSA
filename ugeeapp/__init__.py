from flask import Blueprint,Flask,redirect,url_for,request,render_template,session,flash,abort,jsonify,Markup
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_login import LoginManager, current_user,login_user,logout_user,login_required





app = Flask(__name__)
app.config['SECRET_KEY'] = 'xysmbj3mdu34o84nmyjm3085m80mdhi24'
app.secret_key= 'xysmbj3mdu34o84nmyjm3085m80mdhi24'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stopsdatabase.db'
db = SQLAlchemy(app)
app.config['CSRF_ENABLED'] = True
app.config['CSRF_SESSION_KEY'] = "#@32ske32r42#qxxr3tredaer45e23er2d##232322$%%@"
app.config['UPLOAD_EXTENSIONS'] = ['.doc', '.ppt', '.pdf', '.txt']
migrate = Migrate(app, db)

import ugeeapp.myapp

from ugeeapp.models import User
from ugeeapp.appclasses.globalclass import GLOBALCLASS
from ugeeapp.appclasses.adminclass import AdminRoles

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = '/login'
#login_manager.login_message = ""
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


#@app.template_filter('from_json')
@app.template_filter('from_json')
def from_json(myString): 

        import json
        try:
            json_object = json.loads(myString)
        except ValueError as e:
            return myString
        return json_object

@app.template_filter('to_2dp')
def from_json(figur): 

        return "{:0.2f}".format(float(figur))

@app.template_filter('to_string')
def from_json(obj): 

        
        try:
            json_object = str(obj)
        except ValueError as e:
            return obj
        return json_object


@app.context_processor
def utility_processor():
    def  convert_tostring(obj):
        
        return str(obj)
    return  dict(convert_tostring=convert_tostring)

@app.context_processor
def utility_processor():
    def  calc_planned_dt(DT,UPDT):
        #subtract updt from dt

        result="{:0.2f}".format(float(DT) - float(UPDT))
        
        return result
    return  dict(calc_planned_dt=calc_planned_dt)

@app.context_processor
def utility_processor():
    def  get_user_role(roleid):
        new = AdminRoles()
        role = new.get_admin_roles(roleid)
        if role:
            result = Markup("<div style='font-size:11px' class='alert alert-success'>{}</div>".format(role.rname))
        else:
            result = Markup("<div style='font-size:11px' class='alert alert-danger'>{}</div>".format('None'))
        return result
    return  dict(get_user_role=get_user_role)

@app.context_processor
def utility_processor():
    def  calc_planned_dt_percent(DT,UPDT,skeduletime):
        #subtract updt from dt 
        #find the percentage of the difference to the skeduletime

        if float(skeduletime) == 0:
            result = 0
        else:
            xy = (float(DT) - float(UPDT)) * 100
            result="{:0.2f}".format(xy/float(skeduletime))
        
        return result
    return  dict(calc_planned_dt_percent=calc_planned_dt_percent)

@app.context_processor
def utility_processor():
    def  get_reporting_manager(role_id):
        from ugeeapp.appclasses.adminclass import AdminRoles
        new = AdminRoles()
        if role_id == 0:
            result = 'Top Management'
        else:
            resp = new.get_admin_roles(role_id) 
            result = 'None' if resp is None else resp.rname       
        return result
    return  dict(get_reporting_manager=get_reporting_manager)

@app.context_processor
def utility_processor():
    def  get_department(id):

        new = AdminRoles()
        get = new.get_departments(id)

        return get.abbr
        
    return  dict(get_department=get_department)

@app.context_processor
def utility_processor():
    def  get_user(userid):

        save=GLOBALCLASS()
        username=save.get_userinfo(userid)

        return username               

    return  dict(get_user=get_user)

@app.context_processor
def utility_processor():
    def  get_sku(productcode):
        
        save=GLOBALCLASS()
        sku=save.get_sku(productcode)

        return sku
        

    return  dict(get_sku=get_sku)



if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8024)


#if __name__ == '__main__':

    #app.run(debug=True, use_reloader=False)