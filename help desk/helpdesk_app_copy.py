
"""
This is an Flask app which will be used to request info.
"""

try:
    import sys
    sys.dont_write_bytecode = True
    from api_services import api
    import warnings
    from flask_caching import Cache
    from datetime import datetime,date
    warnings.filterwarnings('ignore')
    from helpdesk.ticketingsystem import launcher
    import warnings
    warnings.filterwarnings("ignore")
except ImportError as importerr:
    print("Error while importing the modules : ",str(importerr))


# chat initialization
# model = load_model("D:/help_desk_git/HelpDesk_Backend/help desk/chatbot_model.h5")
# intents = json.loads(open("D:/help_desk_git/HelpDesk_Backend/help desk/helpdesk/ticketingsystem/helpbot/intents.json").read())
# words = pickle.load(open("D:/help_desk_git/HelpDesk_Backend/help desk/words.pkl", "rb"))
# classes = pickle.load(open("D:/help_desk_git/HelpDesk_Backend/help desk/classes.pkl", "rb"))



CONFIG_FILE_PATH = "C:/Users/chandrakanti.shiva/Documents/GitHub/HelpDesk_Backend/help desk/helpdesk/config/"
CSV_FILE_PATH = "C:/Users/chandrakanti.shiva/Documents/GitHub/HelpDesk_Backend/help desk/helpdesk/storage/"
CONFIG_FILE_NAME = ''
CON_ENVIRONMENT = ''
my_launcher = launcher.SystemLauncher(storage_path=CSV_FILE_PATH,config_name=CONFIG_FILE_NAME,config_path=CONFIG_FILE_PATH)

my_api = api.FlaskApp(app_name='help desk',port_number=5004,allowed_origin='*')
my_app = my_api.app

@my_app.route("/check_access",methods=['POST'])
def check_access():
    try:
        print("check check")
        requested_data=  my_api.request_maker(method='POST')
        
        data = my_launcher.checkaccess(payload=requested_data)
        api_response=my_api.json_response(data=data)
        return api_response
    except Exception as err:
        print("error while calling api to check user access :",err)
        return "error while calling api to check user access :"+str(err)

if __name__ == '__main__':
    my_api.flash_server_start(debug=True)
    # http_server.serve_forever()
    