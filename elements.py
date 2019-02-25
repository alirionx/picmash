import web
import os
import json




def elem_input(defi='', data=''):
	
	elm_tmplt = web.template.frender('templates/input.html')
	elm_html = elm_tmplt(defi, data)
	
	return elm_html
	
	
def elem_select(defi='', data=''):
		
	elm_tmplt = web.template.frender('templates/select.html')
	elm_html = elm_tmplt(defi, data)
	
	return elm_html