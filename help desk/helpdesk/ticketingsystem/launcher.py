"""
This module will be used to check and provide the data
"""
import pandas as pd
from werkzeug.exceptions import BadRequest
from flask import request
from helpdesk.ticketingsystem.ticketingsystem import all_drop_down
from helpdesk.ticketingsystem.ticketingsystem import add_edit_ticket
from helpdesk.ticketingsystem.dash_baords import user_dashboard
from helpdesk.ticketingsystem.ticketingsystem import ticket_conversation

class SystemLauncher():

    def __init__(self,config_path,config_name,storage_path=None):
        self.storage_path = storage_path
        self.config_path = config_path
        self.config_name = config_name

    def check_page(self,page_name=None):

        if page_name is not None:
            if page_name == "form_details":
                data = all_drop_down.All_dropdown(storage_path=self.storage_path).form_details()
            elif page_name == "add_ticket":
                request_data = request.get_json()
                if request_data is None:
                    request_data = request.form
                ticket_data = request_data['ticket_data']
                user_data=request_data['user_details']
                data = add_edit_ticket.NewTickets(storage_path=self.storage_path).raise_concern(user_data=user_data,ticket_data=ticket_data)
            elif page_name == "edit_ticket":
                request_data = request.get_json()
                if request_data is None:
                    request_data = request.form
                ticket_data = request_data['ticket_data']
                user_data=request_data['user_details']
                data = add_edit_ticket.NewTickets(storage_path=self.storage_path).raise_concern(edit="YES",user_data=user_data,ticket_data=ticket_data)
            elif page_name == "user_dashboard":
                data = user_dashboard.UserDashboard(storage_path=self.storage_path).user_dashboard()
            elif page_name == "ticket_conversation":
                data = ticket_conversation.Conversation(storage_path=self.storage_path).capture_user_conversation()
            else:
                data = {
                    "Message":"Page not found"
                }
        else:
            data = {
                "Message":"Please provide the page name"
            }
        return data

    def execute(self):

        try:
            request_data = request.get_json()
            if request_data is None:
                request_data = request.form
            page_name = request_data['page_name']
        except BadRequest as baderr:
            print("Bad request : ",str(baderr))
            request_data = request.get_json(force=True)
            if request_data is None:
                request_data = request.form
            page_name = request_data['page_name']
        data = self.check_page(page_name=page_name)
        return data

        

    def checkaccess(self,mail_id):
        try:
            user_data_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_details.csv")
            user_class_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_type.csv")
            user_data_df = pd.merge(left=user_data_df,right=user_class_df,how='inner',on='USER_CLASS_ID')
            user_data_df['ACCESS_TYPE'] = user_data_df["ACCESS_TYPE"].apply(lambda x:x.split(","))
            if not user_data_df.empty:
                specific_user_data = user_data_df[(user_data_df['EMAIL_ID']==mail_id)]
                if len(specific_user_data) > 0:
                    access_data = {'Access':'Granted'}
                    access_data.update(specific_user_data.to_dict(orient="records")[0])
                else:
                    access_data = {'Access':'Denied'}
            else:
                access_data = {'Access':'Denied'}
            final_data = [access_data]
            return final_data
        except Exception as err:
            return "Error : "+str(err)