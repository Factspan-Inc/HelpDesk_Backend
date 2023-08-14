"""
This module will be used to capture the user conversation.
"""

import pandas as pd
from datetime import date, datetime
from flask import request
current_date =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
class Conversation():

    def __init__(self,storage_path=None):
        self.storage_path = storage_path

    def capture_user_conversation(self,conversation_data=None,user_data=None):

        """
        This function will be used to capture the conversation
        """
        try:

            
            if isinstance(conversation_data,str):
                conversation_data=eval(conversation_data)
                
            if isinstance(user_data,str):
                user_data=eval(user_data)
                
            user_id=user_data['USER_ID']
            
            conversation_data_df = pd.DataFrame.from_dict(conversation_data)
            conversation_data_df['USER_ID']=user_id
            conversation_data_df['COMMENTED_ON']=current_date
            
            user_conversation_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_conversation.csv")
            total_conversation_data_cols=list(user_conversation_df)
            conversation_data_cols=list(conversation_data_df)
            common_cols=list(set(conversation_data_cols).intersection(set(total_conversation_data_cols)))
            conversation_data_df=conversation_data_df[common_cols]
            
            prepared_conversation_df = pd.concat([user_conversation_df,conversation_data_df])
            prepared_conversation_df.to_csv(self.storage_path+"user_conversation.csv",index=False)
            
            message ={"response":"Success"}
            return message
            
        except Exception as err:
            print("error while capturing conersation for ticket :",err)
            return "error while capturing conersation for ticket :"+str(err)
        

    def view_conversation(self,each_ticket_df=None):
        """
        This function is used to view the conversation of particular user
        """
        try:
            each_ticket_df=each_ticket_df.to_frame().transpose()
            ticket_number = each_ticket_df.iloc[0]['TICKET_NUMBER']
            print(ticket_number)
            user_conversation_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_conversation.csv")
            ticket_conversation_df =user_conversation_df[user_conversation_df['TICKET_NUMBER']==ticket_number]
            each_conversation_df =pd.DataFrame()
            if ticket_conversation_df.empty :
                each_ticket_df['TICKET_CONVERSATION']=[[]]
  
            else:
                ticket_conversation_df=ticket_conversation_df.drop(['TICKET_NUMBER'],axis=1)
                ticket_conversation_df['USER_ID']=ticket_conversation_df['USER_ID'].astype(int)
                ticket_conversation_df['USER_ID']=ticket_conversation_df['USER_ID'].astype(str)
                ticket_conversation_df['COMMENTED_ON']=pd.to_datetime(ticket_conversation_df['COMMENTED_ON'],errors='coerce')
                raised_conversation_df = pd.merge(ticket_conversation_df,each_ticket_df[['RAISED_BY','RAISED_BY_NAME']],
                                      how='inner',left_on='USER_ID',right_on='RAISED_BY')
                if not raised_conversation_df.empty:
                    raised_conversation_df['USER_NAME']=raised_conversation_df['RAISED_BY_NAME'] + "(raised by)"
                    raised_conversation_df=raised_conversation_df.drop(['USER_ID','RAISED_BY','RAISED_BY_NAME'],axis=1)
                    
                assigned_conversation_df = pd.merge(ticket_conversation_df,each_ticket_df[['ASSIGNED_TO','ASSIGNED_TO_NAME']],
                                      how='inner',left_on='USER_ID',right_on='ASSIGNED_TO')
                if not assigned_conversation_df.empty:
                    assigned_conversation_df['USER_NAME']=assigned_conversation_df['ASSIGNED_TO_NAME'] + "(assigned to)"
                    assigned_conversation_df=assigned_conversation_df.drop(['USER_ID','ASSIGNED_TO','ASSIGNED_TO_NAME'],axis=1)
                
                assignee_conversation_df = pd.merge(ticket_conversation_df,each_ticket_df[['ASSIGNED_BY','ASSIGNED_BY_NAME']],
                                      how='inner',left_on='USER_ID',right_on='ASSIGNED_BY')
                if not assignee_conversation_df.empty:
                    assignee_conversation_df['USER_NAME']=assignee_conversation_df['ASSIGNED_BY_NAME'] + "(assigned by)"
                    assignee_conversation_df=assignee_conversation_df.drop(['USER_ID','ASSIGNED_BY','ASSIGNED_BY_NAME'],axis=1)
                
                each_conversation_df = pd.concat([raised_conversation_df,assigned_conversation_df,assignee_conversation_df])
                if not each_conversation_df.empty:
                    each_conversation_df=each_conversation_df.sort_values(by=['COMMENTED_ON'],ascending=False)
                    # print(each_conversation_df)
                    each_ticket_df['TICKET_CONVERSATION']=[each_conversation_df.to_dict(orient='records')]
                else:
                    each_ticket_df['TICKET_CONVERSATION']=[[]]
                
                
            return each_ticket_df.iloc[0]
                
            
        except Exception as err:
            print("Error while fetching the ticket conversation : ",err)
            return "Error while fetching the ticket conversation : "+str(err)