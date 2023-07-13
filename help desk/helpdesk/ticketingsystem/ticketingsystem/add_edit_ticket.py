"""
This module will be used to add/edit a ticket.
"""
import pandas as pd
import numpy as np
from datetime import date, datetime
from flask import request
from helpdesk.ticketingsystem.ticketingsystem import mail_sender
current_date =datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class NewTickets():

    def __init__(self,storage_path):
        self.storage_path = storage_path
        
    def notify_admin(self, edit=None,raised_by_name=None,raised_date=None,
                     ticket_number=None,problem_description=None,assigned_to=None):
        try:
            if assigned_to is None:
                assigned_to="Not Assigned"
            if edit is None:
                subject = f"""New concern - New concern raised by {raised_by_name} (Ticket number: {ticket_number})"""
                message = "Hi Shiva,"
                message = message+"\n\n"+f"""New concern raised by {raised_by_name} on {raised_date}"""
                message = message+"\n"+f"Below are the details:"

                html_tag = f'''
                        <html>
                            <body>
                                Hi Shiva<br>
                                Concern raised by {raised_by_name} on {raised_date}<br><br>
                                <b>Below are the details:</b><br>
                                <b>Ticket number</b>: {ticket_number}<br>
                                <b>Raised By</b>: {raised_by_name}<br>
                                <b>Problem description</b>: {problem_description}<br><br>
                                <b>Assigned To</b>: {assigned_to}<br>
                                For more details please visit the tool
                            </body>
                        </html>'''
            else:
                subject = f"""Ticket Modify - Ticket modified by {raised_by_name} (Ticket number: {ticket_number})"""
                html_tag = f'''
                        <html>
                            <body>
                                Hi Shiva<br>
                                Ticket modified by {raised_by_name} on {raised_date}<br><br>
                                <b>Below are the details:</b><br>
                                <b>Ticket number</b>: {ticket_number}<br>
                                <b>Modified By</b>: {raised_by_name}<br>
                                <b>Problem description</b>: {problem_description}<br><br>
                                <b>Assigned To</b>: {assigned_to}<br>
                                For more details please visit the tool<br><br>
                                <i>Note: This as an auto generated mail, please don't reply</i>.
                            </body>
                        </html>'''
                        
            mail_launch = mail_sender.SendMail(body=html_tag,recipients="shiva.chandrakanti@factspan.com",subject=subject)
            mail_prepared = mail_launch.send_message()
        except Exception as err:
            print("error while preparing mail sructure :",err)
            return "error while preparing mail sructure :"+str(err)
        
    def ticket_assignment(self,ticket_id):
        try:
            ticket_data_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_data.csv")
            ticket_data_df=ticket_data_df.fillna('')
            ticket_data_df['UPDATED_ON']=pd.to_datetime(ticket_data_df['UPDATED_ON'])
            ticket_data_df=ticket_data_df.sort_values(by=['UPDATED_ON'],ascending=False)
            ticket_data_df=ticket_data_df.drop_duplicates(subset=['TICKET_NUMBER'],keep='first')
            ticket_data_df['UPDATED_ON']=ticket_data_df['UPDATED_ON'].dt.strftime("%Y-%m-%d")
            ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY','TICKET_ID']]=ticket_data_df[['USER_ID','RAISED_BY','ASSIGNED_TO','ASSIGNED_BY','TICKET_ID']].replace('','0')
            # ticket_data_df=ticket_data_df[ticket_data_df['TICKET_NUMBER']=='T2']

            ticket_type_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_types.csv")
            ticket_type_df=ticket_type_df.fillna('')
            ticket_type_df['TICKET_ID']=ticket_type_df['TICKET_ID'].replace('','0')
            ticket_data_df[['TICKET_ID','ASSIGNED_TO']]=ticket_data_df[["TICKET_ID",'ASSIGNED_TO']].astype(int)
            ticket_data_df[['TICKET_ID','ASSIGNED_TO']]=ticket_data_df[['TICKET_ID','ASSIGNED_TO']].astype(str)
            # print(1)
            ticket_type_df[['TICKET_ID']]=ticket_type_df[['TICKET_ID']].astype(int)
            ticket_type_df[['TICKET_ID']]=ticket_type_df[['TICKET_ID']].astype(str)
            # print(1)
            ticket_data_df=pd.merge(ticket_data_df,ticket_type_df,how='left',on='TICKET_ID')

            ticket_type =ticket_data_df.loc[ticket_data_df['TICKET_ID']==ticket_id,'TICKET_TYPE'].iloc[0]

            if ticket_type.upper() =='TECHNICAL':
                user_class_id='1003'
            elif ticket_type.upper() =='HR':
                user_class_id='1004'
            elif ticket_type.upper() =='FINANCE':
                user_class_id='1005'


            user_data_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_details.csv")
            user_data_df=user_data_df.fillna('')
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].replace('','0')
            user_type_df=pd.read_csv(filepath_or_buffer=self.storage_path+"user_type.csv")
            user_type_df=user_type_df.fillna('')
            user_type_df['USER_CLASS_ID']=user_type_df['USER_CLASS_ID'].replace('','0')

            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(int)
            user_data_df[['USER_ID','USER_CLASS_ID']]=user_data_df[['USER_ID','USER_CLASS_ID']].astype(str)

            user_type_df[['USER_CLASS_ID']]=user_type_df[['USER_CLASS_ID']].astype(int)
            user_type_df[['USER_CLASS_ID']]=user_type_df[['USER_CLASS_ID']].astype(str)
            # print(1)
            user_data_df =pd.merge(user_data_df,user_type_df,how='left',on='USER_CLASS_ID')
            user_data_df=user_data_df.drop_duplicates()

            user_type_data_df=user_data_df[user_data_df['USER_CLASS_ID']==user_class_id]

            assigned_df = pd.merge(ticket_data_df[['ASSIGNED_TO']],
                                    user_type_data_df[['USER_ID']],how='right',
                                    left_on=['ASSIGNED_TO'],right_on=['USER_ID'])

            assigned_df=assigned_df.fillna('0')
            assigned_df['ASSIGNED_FLAG']=np.where(assigned_df['ASSIGNED_TO']==assigned_df['USER_ID'],1,0)
            assigned_df=assigned_df.groupby('USER_ID')['ASSIGNED_FLAG'].sum()
            assigned_df=assigned_df.to_frame()
            assigned_df['USER_ID']=assigned_df.index
            assigned_df=assigned_df.reset_index(drop=True)
            assigned_df=assigned_df.sort_values(by=['ASSIGNED_FLAG'],ascending=True)

            assigned_to =assigned_df['USER_ID'].iloc[0]
            
            return assigned_to
                        
                        
                        
        except Exception as err:
            print("error while assigning ticket :",err)
            return "error while assigning ticket :"+str(err)

    def raise_concern(self,edit=None,ticket_data=None,user_data=None):
        """
        This function will be used to raise or edit a ticket.
        """
        try:
            if isinstance(ticket_data,str):
                ticket_data=eval(ticket_data)
                
            ticket_id =str(ticket_data[0]['TICKET_ID'])
                
            problem_description =ticket_data[0]['PROBLEM_DESCRIPTION']
            if isinstance(user_data,str):
                user_data=eval(user_data)
                
            user_id=user_data['USER_ID']
            user_name=user_data['USER_NAME']        
        
            ticket_data_df = pd.DataFrame.from_dict(ticket_data)
            user_tickets_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_data.csv")
            total_ticket_data_cols=list(user_tickets_df)
            if edit is None:
                # new tickets
                user_tickets_df['T_NO'] = user_tickets_df['TICKET_NUMBER'].apply(lambda x:x[1:])
                max_ticket_no = user_tickets_df['T_NO'].astype(int).max()
                user_tickets_df=user_tickets_df.drop(['T_NO'],axis=1)
                # print(max_ticket_no)
                new_ticket_no = int(max_ticket_no)+1
                # print(new_ticket_no)
                ticket_data_df['TICKET_NUMBER'] = "T"+str(new_ticket_no)
                ticket_data_df['USER_ID'] = user_id
                ticket_data_df['RAISED_ON'] = current_date
                ticket_data_df['RAISED_BY']=user_id
                ticket_data_df['UPDATED_ON']=current_date
                ticket_data_df['UPDATED_BY']=user_id
                ticket_data_df['TICKET_STATUS']='Pending'
                ticket_data_df['ASSIGNED_TO']=self.ticket_assignment(ticket_id=ticket_id)
                ticket_data_df['ASSIGNED_ON']=current_date
                ticket_data_df['ASSIGNED_BY']='1001'
                ticket_no="T"+str(new_ticket_no)
                assigned_to='Not Assigned'
            else:
                # existing ticket
                ticket_no = ticket_data_df.iloc[0]['TICKET_NUMBER']
                assigned_to=ticket_data_df.iloc[0]['ASSIGNED_TO']
                prev_assigned_to=user_tickets_df.loc[user_tickets_df['TICKET_NUMBER']==ticket_no,'ASSIGNED_TO'].iloc[0]
                
                if assigned_to in ('',' ') or assigned_to is None:
                    assigned_to='Not Assigned'
                if assigned_to!=prev_assigned_to:
                    ticket_data_df['ASSIGNED_ON']=current_date
                    ticket_data_df['ASSIGNED_BY']=user_id
                    ticket_data_df['TICKET_STATUS']='Active'
                ticket_data_df['UPDATED_ON']=current_date
                ticket_data_df['UPDATED_BY']=user_id
                
                
                # user_tickets_df_modified = user_tickets_df[(user_tickets_df['TICKET_NUMBER']==ticket_no)]
                # user_tickets_df_modified['TICKET_STATUS'] = ticket_data[0]['TICKET_STATUS']
                # user_tickets_df_modified['FINAL_COMMENT'] = ticket_data[0]['FINAL_COMMENT']
                # user_tickets_df_modified['HR_COMMENT'] = ticket_data[0]['HR_COMMENT']
                # user_tickets_df_modified['TECHNICAL_COMMENT'] = ticket_data[0]['TECHNICAL_COMMENT']
                # user_tickets_df_modified['FINANCE_COMMENT'] = ticket_data[0]['FINANCE_COMMENT']

                # user_tickets_df_unmodified = user_tickets_df[~(user_tickets_df['TICKET_NUMBER']==ticket_no)]

                # prepared_tickets_df = pd.concat(user_tickets_df_unmodified,user_tickets_df_modified)
                
            ticket_data_cols=list(ticket_data_df)
            common_cols=list(set(ticket_data_cols).intersection(set(total_ticket_data_cols)))
            ticket_data_df=ticket_data_df[common_cols]
            prepared_tickets_df = pd.concat([user_tickets_df,ticket_data_df])
            prepared_tickets_df.to_csv(self.storage_path+"ticket_data.csv",index=False)
            send_mail = self.notify_admin(edit=edit,raised_by_name=user_name,raised_date=current_date,
                     ticket_number=ticket_no,problem_description=problem_description,assigned_to=assigned_to)
            return ticket_data
        except Exception as err:
            return "Error while adding/editing a ticket : "+str(err)
        