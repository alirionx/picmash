import web
import os
import json
import random
#import hashlib

urls = (
	
	'/', 'mash_call',
	'/config', 'config_call',
)

#---Sys Config---------------------------------------------


app = web.application(urls, locals())

if not web.config.get('session'):
	session = web.session.Session(app, 
		web.session.DiskStore('./sessions'),
		#initializer={ 'usr':0, 'role':0 }
	)
	web.config.session = session
else:
	session = web.config.session

#----------------------------------------------------------

render = web.template.render('templates/', base='frame')
render_plain = web.template.render('templates/')

#----------------------------------------------------------




class mash_call:
	def GET(self):
		
		htmres = render.mash('Mash')
		return htmres;


class config_call:
	def GET(self):
		
		htmres = render.mash('Config')
		return htmres;
		

#----------------------------------------------------------	

if __name__ == "__main__":
    app.run()
	
#----------------------------------------------------------