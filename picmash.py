import web
import os
import json
import random
import string
#import hashlib
import time


import elements		
elmget = {
	'input': elements.elem_input,
	'select': elements.elem_select
}

urls = (
	
	'/', 'mash_call',
	'/login/do', 'login_do',
	'/login', 'login_call',
	'/config', 'config_call',
	'/upload/do', 'upload_do',
	'/upload', 'upload_call',
	'/vote/(.*)/(.*)/(.*)', 'vote_do',
	'/ranking', 'ranking_call',
	'/pic/delete/(.*)', 'pic_delete',
	'/ranking/reset', 'ranking_reset',
	'/app/reset', 'app_reset',
	
)


#---Sys Config---------------------------------------------

# docker run -itd -p81:80 --name picmash1 alirionx/picmash:v01

adminpw = 'Oviss1234!'

mroot = 'static/media/'
mpath = mroot+'files/'
flatdata = mroot+'pimash.json'

#-------------------------------

app = web.application(urls, locals())

if not web.config.get('session'):
	session = web.session.Session(app, 
		web.session.DiskStore('./sessions'),
		initializer={ 'admin':0 }
	)
	web.config.session = session
else:
	session = web.config.session

#-------------------------------

render = web.template.render('templates/', base='frame')
render_plain = web.template.render('templates/')

#----------------------------------------------------------

def img_scan():
	
	with open(flatdata) as jsonfile:
		data = jsonfile.read()
		obj_in = json.loads(data)
	
	data = obj_in['data'];
	media_ary = []
	file_ary  = []
	for media in data:
		media_ary.append(media['hash']+'.'+media['mime'])
	
	for fn in os.listdir(mpath):
		file_ary.append(fn)
		if fn not in media_ary:
			splt = fn.split('.')
			newf = {}
			newf['hash'] = splt[0]
			newf['mime'] = splt[1]
			newf['win']  = 0
			newf['loss'] = 0
			
			data.append(newf)
		
	i = 0
	todel = []
	for media in data:
		fn = media['hash']+'.'+media['mime']
		if fn not in file_ary:
			todel.append(media)
		i += 1	
	
	newdata = []
	for media in data:
		if media not in todel:
			newdata.append(media)
	
	obj_in['data'] = newdata
	res_json = json.dumps(obj_in, indent=4, sort_keys=True)
	
	print res_json
	
	with open(flatdata, 'w') as outfile:
		outfile.write(res_json)
	
	#print res_json

#-----App Init---------------------------------------------

if not os.path.isdir(mroot):
	os.makedirs(mroot)
	
if not os.path.isdir(mroot+'/files/'):
	os.makedirs(mroot+'/files/')
	
if not os.path.isfile(flatdata):
	os.system('cp init/pimash.json ' + flatdata)  

#----------------------------------------------------------


class mash_call:
	def GET(self):
		
		with open(flatdata) as jsonfile:
			data = jsonfile.read()
			obj_in = json.loads(data)
		
		data = obj_in['data'];
		hash_ary = [] 
		for media in data:
			hash_ary.append(media['hash'])
		
		mash_ary = {}
		
		try:
			mash_data = random.sample(data, 2)
			for mash in mash_data:
				idx = hash_ary.index(mash['hash'])
				mash_ary[str(idx)] = mash
		except:
			raise web.seeother('/login')
			return 'no media available'
		
		#print mash_ary
		
		vhash = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
		session.vhash = vhash
		
		htmres = render.mash(mash_ary, mpath, vhash)
		return htmres;

#-----------------------------------

class login_call:
	def GET(self):
	
		htmres = render.login()
		return htmres;


class login_do:
	def POST(self):
		
		pwd = web.input().pwd
		if pwd == adminpw:
			session.admin = 1
			raise web.seeother('/config')
		else:
			raise web.seeother('/login')
		
		

class config_call:
	def GET(self):
		
		if session.admin == 0:
			raise web.seeother('/login')
		
		with open(flatdata) as jsonfile:
			data = jsonfile.read()
			obj_in = json.loads(data)
			
		defi = obj_in['defi'];
		data = obj_in['data'];
		i = 0
		for row in data:
			try:
				rate = float(row['win']) / ( row['win'] + row['loss'] )
				perc = round(rate*100, 1)
				data[i]['rate'] = str(perc) + '%'
			except:
				data[i]['rate'] = '50.0%'
			i += 1
		
		data = sorted(data, key = lambda dct:dct['rate'], reverse = True )
		
		htmres = render.config(defi, data, mpath )
		return htmres;
		
#-----------------------------------

class upload_call:
	def GET(self):
	
		htmres = render.upload()
		return htmres;
		
class upload_do:
	def POST(self):
		
		files = web.webapi.rawinput().get('file_ipt')
		if not isinstance(files, list):
			files = [files]
			
		for f in files:
			
			fn = f.filename.lower()
			splt = fn.split('.')
			num = len(splt);
			mime = splt[num-1]
			rand = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
			target = mpath + rand + '.'+mime
				
			print rand + '.'+mime
			content = f.file.read()
			with open(target, 'w') as f:
				f.write(content)
		
		img_scan()
		
		raise web.seeother('/config')
		return 'ok';
		
#-----------------------------------

class vote_do:
	def GET(self, vhash, winner, loser):
		
		stat = 'fail'
		if session.vhash == vhash:
			stat = 'passed'
			session.vhash = ''
			
			with open(flatdata) as jsonfile:
				data = jsonfile.read()
				obj_in = json.loads(data)
			
			data = obj_in['data'];
			
			wint = int(winner)
			lint = int(loser)
			
			data[wint]['win']  = data[wint]['win'] + 1
			data[lint]['loss'] = data[lint]['loss'] + 1
			
			obj_in['data'] = data
			res_json = json.dumps(obj_in, indent=4, sort_keys=True)
			
			print res_json
			
			with open(flatdata, 'w') as outfile:
				outfile.write(res_json)
		
		raise web.seeother('/')
		return stat;

#----------------------------------------------------------	

class ranking_call:
	def GET(self):
		
		with open(flatdata) as jsonfile:
			data = jsonfile.read()
			obj_in = json.loads(data)
			
		defi = obj_in['defi'];
		data = obj_in['data'];
		i = 0
		for row in data:
			try:
				rate = float(row['win']) / ( row['win'] + row['loss'] )
				perc = round(rate*100, 1)
				#data[i]['rate'] = str(perc) + '%'
				data[i]['rate'] = perc
			except:
				data[i]['rate'] = 50.0
				
			i += 1
		
		data = sorted(data, key = lambda dct:dct['rate'], reverse = True )
		i = 0
		for row in data:
			data[i]['rate'] = str(row['rate']) + '%'
			i += 1
		
		htmres = render.ranking(defi, data, mpath )
		return htmres;

#----------------------------------------------------------	

class pic_delete:
	def GET(self, fn):
		
		try:
			os.remove(mpath+fn)
			img_scan()
		except:
			print 'can not delete file'
		
		raise web.seeother('/config')
		return 'ok'


class ranking_reset:
	def GET(self):
		
		with open(flatdata) as jsonfile:
			data = jsonfile.read()
			obj_in = json.loads(data)
			
		data = obj_in['data'];
		
		i = 0
		for row in data:
			data[i]['win'] = 0
			data[i]['loss'] = 0
			i += 1
			
		obj_in['data'] = data
		res_json = json.dumps(obj_in, indent=4, sort_keys=True)
			
		with open(flatdata, 'w') as outfile:
			outfile.write(res_json)
			
		raise web.seeother('/config')
		return 'ok'


class app_reset:
	def GET(self):
		
		for fn in os.listdir(mpath):
			os.remove(mpath+fn)
		
		img_scan()
		
		raise web.seeother('/config')
		return 'ok'
			
#----------------------------------------------------------	

if __name__ == "__main__":
    app.run()
	
#----------------------------------------------------------