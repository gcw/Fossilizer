# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.table_user=db.define_table('auth_user',
    Field('first_name', length=128, default='',),
    Field('last_name', length=128, default='',),
    Field('user_handle', length=32, default='', label='Handle',
            writable=True,
            readable=True,
            requires=[IS_NOT_EMPTY(),
                        IS_NOT_IN_DB(db, 'auth_user.user_handle',
                            error_message = 'Handle already in use'),
                        IS_MATCH('^[\w.-]{3,32}$',
                            error_message = 'Invalid characters')]),
    Field('web', length=128, default='',
            writable=True,
            readable=True),
    Field('email', length=128, default='',
            requires = [ IS_EMAIL(), IS_NOT_IN_DB(db, 'auth_user.email')]),
    Field('password', 'password', readable=False,
            label='Password',
            requires=CRYPT(auth.settings.hmac_key)),
    Field('registration_key', length=512,
            writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,
            writable=False, readable=False, default=''),)


auth.settings.hmac_key = 'sha512:SkF9nm7nCbuCKSDgIwjK8U5rU'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL(r=request,c='default',f='user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None       # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
import os.path

db.define_table('fossil', 
    Field('project_name', 'string', 
        requires=IS_MATCH('^[\w.-]{2,32}$',
            error_message = 'Invalid characters')),
    Field('owner', db.auth_user, default=auth.user_id,
        readable=False, writable=False,),
    Field('visibility', 'boolean', label='List publicly', default=True),
    Field('description', 'text'),
    Field('created_on', 'datetime', readable=True, writable=False,),
    Field('tags', 'string'),
    Field('clone_url', 'string', requires=IS_EMPTY_OR(IS_URL()),),
    Field('file', 'upload', uploadseparate=True),
    Field('repo_url', 
        compute = lambda fossil: URL( 'u',
                                        db.auth_user[auth.user_id].user_handle,
                                        fossil['project_name'])   ),
    Field('link_path',
        compute = lambda fossil: os.path.join(FOSSIL_PATH, 'userdirs', 
                                        db.auth_user[auth.user_id].user_handle,
                                        fossil.project_name + '.fossil')),
    Field('user_index',
        compute = lambda fossil: os.path.join(FOSSIL_PATH, 'cgi',
                                        db.auth_user[auth.user_id].user_handle)),
    )

