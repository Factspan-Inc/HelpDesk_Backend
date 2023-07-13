
"""
This is an Flask app which will be used to request info.
"""

try:
    from flask_restful import Resource, Api
    from flask import Flask, jsonify,request,make_response
    from werkzeug.exceptions import BadRequest
    import json
    import gzip
    import sys,os
    from gevent.pywsgi import WSGIServer
    import random
    import numpy as np
    # import pickle
    # from flask_ngrok import run_with_ngrok
    # import nltk
    # from keras.models import load_model
    # from nltk.stem import WordNetLemmatizer
    # lemmatizer = WordNetLemmatizer()
    from helpdesk.ticketingsystem import launcher
    import warnings
    warnings.filterwarnings("ignore")
except ImportError as importerr:
    print("Error while importing the modules : ",str(importerr))


# chat initialization
# model = load_model("D:/help desk/chatbot_model.h5")
# intents = json.loads(open("D:/help desk/helpdesk/ticketingsystem/helpbot/intents.json").read())
# words = pickle.load(open("D:/help desk/words.pkl", "rb"))
# classes = pickle.load(open("D:/help desk/classes.pkl", "rb"))



CONFIG_FILE_PATH = "D:/help desk/helpdesk/config/"
CSV_FILE_PATH = "D:/help desk/helpdesk/storage/"
CONFIG_FILE_NAME = ''
CON_ENVIRONMENT = ''
myapi = launcher.SystemLauncher(storage_path=CSV_FILE_PATH,config_name=CONFIG_FILE_NAME,config_path=CONFIG_FILE_PATH)

# flask app object
app = Flask("Help Desk")
api = Api(app)
http_server = WSGIServer(('0.0.0.0', 5004), app)

@app.after_request
def after_request(response):
    # need to change the origin.
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response



# chat functionalities
# def clean_up_sentence(sentence):
#     sentence_words = nltk.word_tokenize(sentence)
#     sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
#     return sentence_words


# # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
# def bow(sentence, words, show_details=True):
#     # tokenize the pattern
#     sentence_words = clean_up_sentence(sentence)
#     # bag of words - matrix of N words, vocabulary matrix
#     bag = [0] * len(words)
#     for s in sentence_words:
#         for i, w in enumerate(words):
#             if w == s:
#                 # assign 1 if current word is in the vocabulary position
#                 bag[i] = 1
#                 if show_details:
#                     print("found in bag: %s" % w)
#     return np.array(bag)


# def predict_class(sentence, model):
#     # filter out predictions below a threshold
#     p = bow(sentence, words, show_details=False)
#     res = model.predict(np.array([p]))[0]
#     ERROR_THRESHOLD = 0.25
#     results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
#     # sort by strength of probability
#     results.sort(key=lambda x: x[1], reverse=True)
#     return_list = []
#     for r in results:
#         return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
#     return return_list


# def getResponse(ints, intents_json):
#     tag = ints[0]["intent"]
#     list_of_intents = intents_json["intents"]
#     for i in list_of_intents:
#         if i["tag"] == tag:
#             result = random.choice(i["responses"])
#             break
#     return result

def compress_response(requested_data):

    """
    This function will be used to compress the response.
    """
    try:
        content = gzip.compress(json.dumps(requested_data,default=str).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    except Exception as err:
        return "Error while compressing the response: "+str(err)
    

def blockPrinting(func):
    def func_wrapper(*args, **kwargs):
        # block all printing to the console
        sys.stdout = open(os.devnull, 'w')
        # call the method in question
        value = func(*args, **kwargs)
        # enable all printing to the console
        sys.stdout = sys.__stdout__
        # pass the return value of the method back
        return value

    return func_wrapper

def login_is_required():
    try:
        try:
            request_data = request.get_json()
            if request_data is None:
                request_data = request.form
            mail_id = request_data['mail_id']
        except BadRequest as baderr:
            request_data = request.get_json(force=True)
            if request_data is None:
                request_data = request.form
            mail_id = request_data['mail_id']
        if mail_id is None:
            # access denied
            response_data = {"Access": "Denied"}
        else:

            domain_name = mail_id[mail_id.find("@")+1:]
            if domain_name in ("factspan.com"):
                response_data = myapi.checkaccess(mail_id=mail_id)
            else:
                # access denied
                response_data = {"Access": "Denied"}
        return response_data
    except KeyError as keyerr:
        return jsonify(message="Error : " + str(keyerr), category="error", status=404)
    except Exception as err:
        return jsonify(message="Error : " + str(err), category="error", status=404)

# class Helpbot(Resource):
#     def post(self):
#         request_data = request.get_json()
#         if request_data is None:
#             request_data = request.form
#         msg = request_data["msg"]
#         #checks is a user has given a name, in order to give a personalized feedback
#         if msg.startswith('my name is'):
#             name = msg[11:]
#             ints = predict_class(sentence=msg, model=model)
#             res1 = getResponse(ints=ints, intents_json=intents)
#             res = res1.replace("{n}",name)
#         elif msg.startswith('hi my name is'):
#             name = msg[14:]
#             ints = predict_class(sentence=msg, model=model)
#             res1 = getResponse(ints=ints, intents_json=intents)
#             res =res1.replace("{n}",name)
#         #if no name is passed execute normally
#         else:
#             ints = predict_class(sentence=msg, model=model)
#             res = getResponse(ints=ints, intents_json=intents)
#         bot_response = {
#             "Response":res
#         }
#         return bot_response

class Checkaccess(Resource):
    def post(self):
        """
        This function will take email or id token as input 
        and allow the access according to it
        """

        try:
            user_access = login_is_required()
            if type(user_access) == str:
                return jsonify(message="Error : " + str(user_access), category="error", status=404)
            else:
                response = compress_response(requested_data=user_access)
                return response
        except Exception as valerr:
            return jsonify(message="Error : " + str(valerr), category="error", status=404)

class Helpdesk(Resource):
    def post(self):
        """
        This function will be used to provide the requested data.
        """
        try:
            user_access = login_is_required()
            if type(user_access) == str:
                return jsonify(message="Error : " + str(user_access), category="error", status=404)
            else:
                access_status = user_access[0]['Access']
                if access_status == 'Granted':
                    requested_data = myapi.execute()
                    if type(requested_data) == str:
                        return jsonify(message="Error : " + str(requested_data), category="error", status=404)
                    else:
                        response = compress_response(requested_data=requested_data)
                        return response
                else:
                    return {"Access": "Denied"}

        except Exception as err:
            return jsonify(message="Error : " + str(err), category="error", status=404)

api.add_resource(Helpdesk,'/helpdesk')
api.add_resource(Checkaccess,'/checkaccess')
# api.add_resource(Helpbot,'/helpbot')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5004,debug=True)
    # http_server.serve_forever()
    