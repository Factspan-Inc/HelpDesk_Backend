import sys
sys.dont_write_bytecode = True
from flask_restful import Api
from flask import Flask, jsonify,make_response,request
import json
import gzip
import sys,os
from gevent.pywsgi import WSGIServer
from werkzeug.exceptions import BadRequest
from gevent import monkey
import subprocess
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


class FlaskApp():
    """
    This flask app is an app which is parameterized with only one endpoint which user can define.
    input - app name,portnumber, certificate file path, keyfile path (for https),method and endpoint, function ( to get the data )
    output - response from the app
    
    """

    def __init__(self,app_name=None,port_number=None,allowed_origin=None,fast_app=None):
        self.app_name = app_name
        self.port_number = port_number
        self.host = '0.0.0.0'
        # if fast_app is not None:
        #     self.host='52.15.175.145'
        self.allowed_origin = allowed_origin
        if self.allowed_origin is None:
            self.allowed_origin = '*'
        
        if self.app_name is None:
            self.app_name = 'app'
        self.app = Flask(app_name)
        self.api = Api(self.app)
        if fast_app is not None:
            self.app1 = FastAPI(title=self.app_name)
            self.app1.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"] )
        
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', self.allowed_origin)
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response
        

        
    def is_json(self,myjson):
        try:
            json.dumps(obj=myjson,allow_nan=False,default=str)
        except ValueError as err:
            return False
        except Exception as errr:
            return False
        return True
    
    def request_maker(self,method):
        if method is None:
            methods = 'POST'
        else:
            methods = str(method).upper()
            if methods == 'POST':
                try:
                    # request_data = eval(request.get_data(as_text=True))
                    request_data = eval(request.get_data(as_text=True))
                except BadRequest as err:
                    print("bad request occurs -- ",err)
                    request_data = request.get_json(force=True)
                if isinstance(request_data,str):
                    request_data = eval(request_data)
                return request_data
            elif methods == 'GET':
                request_data = request.args
                if isinstance(request_data,str):
                    request_data = eval(request_data)
                return request_data.to_dict()
            else:
                request_data = {}
                return request_data
            
    def getform_data(self):
        try:
            data = request.form.to_dict()
            final_dict = {}
            # for key,values in data.items():
            #     if isinstance(values,str):
            #         values = eval(values)
            #     final_dict[key]=values
            return data
        except Exception as err:
            return "Error while getting form data : "+str(err)
    def getter(self,data):
        try:
            if self.is_json(myjson=data) is True:
                content = gzip.compress(json.dumps(data,default=str).encode('utf8'), 5)
                response = make_response(content)
                response.headers['Content-length'] = len(content)
                response.headers['Content-Encoding'] = 'gzip'
                return response
            else:
                response = "Not a json"
                return response
        except Exception as err:
            return "error in getter :-"+str(err)
    
    def getter1(self,data):
        try:
            if self.is_json(myjson=data) is True:
                json_data = json.dumps(data, default=str)
                compressed_data = gzip.compress(json_data.encode("utf-8"))
                response = Response(content=compressed_data, media_type="application/json")
                response.headers["Content-Length"] = str(len(compressed_data))
                response.headers["Content-Encoding"] = "gzip"
                return response
            else:
                response = "Not a json"
                return response
        except Exception as err:
            return "error in getter :-"+str(err)
        
    def getfile(self,base_path=None):
        """
        This function will be used to get the file from API 
        and storage in the system.
        """
        try:
            if base_path is None:
                base_path = '/home/ubuntu/'
            file = request.files.to_dict()
            if len(file)>0:
                file_name_list = list(file.keys())
            else:
                file_name_list = []     
            response = {
                "basepath":base_path,
                "list_of_filename":file_name_list,
                "all_files":file
            }
            return response
        except Exception as err:
            return "Error while getting the file : "+str(err)
    def json_response(self,data):
        try:
            app_response = self.getter(data=data)
            if type(app_response) == str:
                app_response = jsonify(message=str(app_response), category="Error", status=404)
            return app_response
        except Exception as err:
            return jsonify(message="Exception occured : " + str(err), category="Error", status=404)  
          
    def json_response1(self,data):
        try:
            app_response = self.getter1(data=data)
            if type(app_response) == str:
                return JSONResponse(content=app_response,status_code=404)
            return app_response
        except Exception as err:
            return jsonify(message="Exception occured : " + str(err), category="Error", status=404)
    
    def gevent_server_start(self,certificate_file_path=None,key_file_path=None):
        # monkey.patch_all()
        if key_file_path is None:
            # http_server = WSGIServer((self.host, self.port_number), self.app,environ={'wsgi.multithread': True,'wsgi.multiprocess': True})
            http_server = WSGIServer((self.host, self.port_number), self.app)
        else:
            # http_server = WSGIServer((self.host, self.port_number), self.app,keyfile=key_file_path, certfile=certificate_file_path,environ={'wsgi.multithread': True,'wsgi.multiprocess': True})
            http_server = WSGIServer((self.host, self.port_number), self.app,keyfile=key_file_path, certfile=certificate_file_path)
        return http_server.serve_forever()
    
    def flash_server_start(self,debug=False,certificate_file_path=None,key_file_path=None):
        if key_file_path is None:
            context = None
        else:
            import ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=certificate_file_path,keyfile=key_file_path)
        return self.app.run(host=self.host,debug=debug,port=self.port_number,ssl_context=context)
    
    def uvicorn_server_start(self,certificate_file_path=None,key_file_path=None):
        if key_file_path is None:
            context = None
            return uvicorn.run(self.app1,port=self.port_number,host=self.host)
        else:
            # import ssl
            # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            # ssl_context.load_cert_chain(certfile=certificate_file_path, keyfile=key_file_path)
            return uvicorn.run(self.app1,port=self.port_number,ssl_keyfile=key_file_path,ssl_certfile=certificate_file_path,host=self.host)
    
    def gunicorn_server(self,module_name,app_variable,workers=4,worker_class="gevent",certificate_file_path=None,key_file_path=None):
        try:
            # Run a shell command
            if key_file_path is None:
                final_command = f"""sudo gunicorn --worker-class={worker_class} --worker-connections=1000 -w {workers} -b {self.host}:{self.port_number} {module_name}:{app_variable}"""
            else:
                final_command = f"""sudo gunicorn --certfile={certificate_file_path} --keyfile={key_file_path} --worker-class={worker_class} --worker-connections=1000 -w {workers} -b {self.host}:{self.port_number} {module_name}:{app_variable}"""
            result = subprocess.run([final_command], capture_output=True, text=True,shell=True)
            print(result)

            # Check the command output
            if result.returncode == 0:
                print("Command executed successfully!")
                print("Command output :-")
                print(result.stdout)
            else:
                print("Command failed!")
                print("Error message :-")
                print(result.stderr)
        except Exception as err:
            print("Error while running gunicorn server : ",err)
            return "Error while running gunicorn server : "+str(err)
    



    

    


