import web
import os
import json
import random
import string
#import hashlib

import elements		
elmget = {
	'input': elements.elem_input,
	'select': elements.elem_select
}

urls = (
	
	'/', 'mash_call',
	'/config', 'config_call',
	'/upload/do', 'upload_do',
	'/upload', 'upload_call',
	
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

mpath = 'static/media/'
flatdata = 'flatdata/pimash.json'

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
	for media in data:
		fn = media['hash']+'.'+media['mime']
		if fn not in file_ary:
			del data[i]
		i += 1	
	
	obj_in['data'] = data
	res_json = json.dumps(obj_in, indent=4, sort_keys=True)
	
	print res_json
	
	with open(flatdata, 'w') as outfile:
		outfile.write(res_json)
	
	#print res_json

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
		mash_data = random.sample(data, 2)
		for mash in mash_data:
			idx = hash_ary.index(mash['hash'])
			mash_ary[str(idx)] = mash
		
		#print mash_ary
		
		htmres = render.mash(mash_ary, mpath)
		return htmres;

#-----------------------------------

class config_call:
	def GET(self):
		
		htmres = render.config('Config')
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

#----------------------------------------------------------	

if __name__ == "__main__":
    app.run()
	
#----------------------------------------------------------