"""module create admin dashboard"""
import pandas as pd
import pandasql as ps
from flask import request
from helpdesk.ticketingsystem.ticketingsystem import ticket_conversation

class UserDashboard():
    
    def __init__(self,storage_path):
        self.storage_path = storage_path
        
    def prepare_ticket_data(self, ticket_data_df,user_data_df):
        try:
            ticket_df_cols =list(ticket_data_df)
            user_df_cols =list(user_data_df)
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(int)
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(str)
            
            ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY']]=ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY']].astype(int)
            ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY']]=ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY']].astype(str)
            
            ticket_data_df=ticket_data_df.drop(['USER_ID'],axis=1)
            ticket_data_df = pd.merge(ticket_data_df,user_data_df[['USER_ID','USER_NAME']],
                                      how='left',left_on='RAISED_BY',right_on='USER_ID')
            
            ticket_data_df=ticket_data_df.drop(['USER_ID'],axis=1)
            
            ticket_data_df.rename(columns={'USER_NAME':'RAISED_BY_NAME'},inplace = True)
            
            ticket_data_df = pd.merge(ticket_data_df,user_data_df[['USER_ID','USER_NAME']],
                                      how='left',left_on='ASSIGNED_TO',right_on='USER_ID')
            
            
            ticket_data_df=ticket_data_df.drop(['USER_ID'],axis=1)
            ticket_data_df.rename(columns={'USER_NAME':'ASSIGNED_TO_NAME'},inplace = True)
            
            ticket_data_df = pd.merge(ticket_data_df,user_data_df[['USER_ID','USER_NAME']],
                                      how='left',left_on='ASSIGNED_BY',right_on='USER_ID')
            
            ticket_data_df=ticket_data_df.drop(['USER_ID'],axis=1)
            ticket_data_df.rename(columns={'USER_NAME':'ASSIGNED_BY_NAME'},inplace = True)
            
           
            return ticket_data_df
            
        except Exception as err:
            print("error while preparing ticket data : ",err)
            return "error while preparing ticket data : "+str(err)
        
    def user_drop_down(self,user_data_df=None):
        try:
            it_team_df =user_data_df[user_data_df['USER_CLASS_ID']=='1003']
            hr_team_df =user_data_df[user_data_df['USER_CLASS_ID']=='1004']
            finance_team_df =user_data_df[user_data_df['USER_CLASS_ID']=='1005']
            
            user_drop_down ={}
            user_drop_down['TECHNICAL_DROP_DOWN']=it_team_df[['USER_ID','USER_NAME']].to_dict(orient='records')
            user_drop_down['HR_DROP_DOWN']=hr_team_df[['USER_ID','USER_NAME']].to_dict(orient='records')
            user_drop_down['FINANCE_DROP_DOWN']=finance_team_df[['USER_ID','USER_NAME']].to_dict(orient='records')
            return user_drop_down
        except Exception as err:
            print("error while preparing user drop down :",err)
            return "error while preparing user drop down :"+str(err)
    
    def user_dashboard(self):
        
        try:
            
            request_data = request.get_json()
            if request_data is None:
                request_data = request.form
            user_data = request_data['user_details']
            if isinstance(user_data,str):
                user_data=eval(user_data)
            user_id=user_data['USER_ID']
            user_class =user_data['USER_CLASS']
            print(1)
            ticket_data_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_data.csv")
            ticket_data_df=ticket_data_df.fillna('')
            ticket_data_df['UPDATED_ON']=pd.to_datetime(ticket_data_df['UPDATED_ON'])
            ticket_data_df=ticket_data_df.sort_values(by=['UPDATED_ON'],ascending=False)
            ticket_data_df=ticket_data_df.drop_duplicates(subset=['TICKET_NUMBER'],keep='first')
            ticket_data_df['UPDATED_ON']=ticket_data_df['UPDATED_ON'].dt.strftime("%Y-%m-%d")
            ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY','TICKET_ID']]=ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY','TICKET_ID']].replace('','0')
            # ticket_data_df=ticket_data_df[ticket_data_df['TICKET_NUMBER']=='T2']
            print(1)
            ticket_type_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_types.csv")
            ticket_type_df=ticket_type_df.fillna('')
            ticket_type_df['TICKET_ID']=ticket_type_df['TICKET_ID'].replace('','0')
            print(1)
            user_data_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_details.csv")
            user_data_df=user_data_df.fillna('')
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].replace('','0')
            user_type_df=pd.read_csv(filepath_or_buffer=self.storage_path+"user_type.csv")
            user_type_df=user_type_df.fillna('')
            user_type_df['USER_CLASS_ID']=user_type_df['USER_CLASS_ID'].replace('','0')
            print(1)
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(int)
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(str)
            print(1)
            user_type_df[['USER_CLASS_ID']]=user_type_df[['USER_CLASS_ID']].astype(int)
            user_type_df[['USER_CLASS_ID']]=user_type_df[['USER_CLASS_ID']].astype(str)
            # print(1)
            user_data_df =pd.merge(user_data_df,user_type_df,how='left',on='USER_CLASS_ID')
            user_data_df=user_data_df.drop_duplicates()
            # user_data_df=user_data_df[user_data_df['USER_ID']==user_id]
            # print(ticket_data_df)
            ticket_data_df[['TICKET_ID']]=ticket_data_df[["TICKET_ID"]].astype(int)
            ticket_data_df[['TICKET_ID']]=ticket_data_df[['TICKET_ID']].astype(str)
            # print(1)
            ticket_type_df[['TICKET_ID']]=ticket_type_df[['TICKET_ID']].astype(int)
            ticket_type_df[['TICKET_ID']]=ticket_type_df[['TICKET_ID']].astype(str)
            # print(1)
            ticket_data_df=pd.merge(ticket_data_df,ticket_type_df,how='left',on='TICKET_ID')
            print(1)
            ticket_data_df =self.prepare_ticket_data(ticket_data_df=ticket_data_df,user_data_df=user_data_df)
            
            ticket_data_df =ticket_data_df.apply(lambda ticket_data_df :ticket_conversation.Conversation(
                                                        storage_path=self.storage_path).view_conversation(
                                                            each_ticket_df=ticket_data_df),axis=1)
            
            ticket_data_df=ticket_data_df.fillna('')
            # ticket_data_df=ticket_data_df.replace('0','')
            print(1)
            raised_tickets_df=ticket_data_df[ticket_data_df['RAISED_BY']==user_id]
            assigned_tickets_df=ticket_data_df[ticket_data_df['ASSIGNED_TO']==user_id]
            
            assigned_by_user_df=ticket_data_df[ticket_data_df['ASSIGNED_BY']==user_id]
            unassigned_tickets=ticket_data_df[(ticket_data_df['ASSIGNED_TO'].isnull()) | (ticket_data_df['ASSIGNED_TO'].isin(['',' ','0',0]))]
            # print(ticket_data_df['ASSIGNED_TO'])
            user_data_df=user_data_df.fillna('')
            each_user_data_df=user_data_df[user_data_df['USER_ID']==user_id]
            user_dashboard_data=each_user_data_df.to_dict(orient='records')
            if len(user_dashboard_data)==0:
                message = {"Response":"Fail",
                        "Message":"User not found"}
            else:
                user_dashboard_data[0]['TICKETS_RAISED_BY_USER']=raised_tickets_df.to_dict(orient='records')
                user_dashboard_data[0]['TICKETS_ASSIGNED_TO_USER']=assigned_tickets_df.to_dict(orient='records')
                user_dashboard_data[0]['TICKETS_ASSIGNED_BY_USER']=assigned_by_user_df.to_dict(orient='records')

                if user_class.upper() =='ADMIN':
                    user_dashboard_data[0]['UNASSIGNED_TICKETS']=ticket_data_df.to_dict(orient='records')
                else:
                    user_dashboard_data[0]['UNASSIGNED_TICKETS']=[]
                    
                user_drop_down = self.user_drop_down(user_data_df=user_data_df)
                
                

                message = {"Response":"Success",
                        "Message":"User details found"}
                 
                message['USER_DATA']=user_dashboard_data
                message['USER_DROP_DOWN']=user_drop_down
            return message
        except Exception as err:
            print("error while making user dashboard data :",err)
            return "error while making user dashboard data :"+str(err)         
        