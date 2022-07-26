import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import time

api_url = 'http://172.17.0.1:8000' #host_ip

ALLOWED_EXTENSIONS = set(['apk', 'zip', 'ipa', 'appx'])

filename = ''
filefullpath = ''
task_id = 0

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():

	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filefullpath = app.config['UPLOAD_FOLDER']+filename
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))		
		
		task_id = scan_file(filename, filefullpath)	
		resp = get_json(task_id)
		
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are apk, zip, ipa, appx'})
		resp.status_code = 400
		return resp




def scan_file(filename, filefullpath):
	multipart_data = MultipartEncoder(fields={'file': (
							filename,
							open(filefullpath,'rb'),
							'application/octet-stream')})

	header = {
		'Content-Type': multipart_data.content_type,
		'Authorization': '6fc5be6ee1d904476ba6c255173ad3f086a6f537' #insert your token here
		}
	
	response = requests.post(api_url+'/apiv2/tasks/create/file/',
			  headers=header,
			  data=multipart_data
			)
	task_id = response.json()["data"]["task_ids"][0]
	
	return(task_id)



def get_json(task_id):

	header = {
		
		'Authorization': '6fc5be6ee1d904476ba6c255173ad3f086a6f537' #insert your token here
		}
 										
	response = jsonify({ 'task_id' : task_id})
	return(response)
	

@app.route('/ready',methods = ['GET'])  	
def ready():	


	header = {
		
		'Authorization': '6fc5be6ee1d904476ba6c255173ad3f086a6f537' #insert your token here
		}
		
	task_id = request.args.get('task_id')
	
	response = requests.get(api_url+'/apiv2/tasks/get/report/'+str(task_id)+'/json/')
   	
	return(response.text)
	
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)  


 
''' 
curl -F file=@/path/to/file http://0.0.0.0:8001/file-upload

curl -L "http://0.0.0.0:8001/ready?task_id=<your_task_id>"


'''

