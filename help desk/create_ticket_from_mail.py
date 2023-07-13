import email
import smtplib
import time
import imaplib
import email
import traceback 
import nltk
from nltk.stem import WordNetLemmatizer
import warnings
warnings.filterwarnings("ignore")
lemmatizer = WordNetLemmatizer()
import pandas as pd
from helpdesk.ticketingsystem import launcher
from helpdesk.ticketingsystem.ticketingsystem import add_edit_ticket
ORG_EMAIL = "@factspan.com" 
FROM_EMAIL = "shiva.chandrakanti" + ORG_EMAIL 
FROM_PWD = "Shiva@1710" 
SMTP_SERVER = "imap.gmail.com" 
SMTP_PORT = 993

employee_lst = ['EMPLOYEE NAME','EMPLOYEE ID','EMPLOYEE','NAME','EMPLOYEE DATA']

tech_lst = ['LAPTOP','PC','KEYBOARD','DISPLAY','SCREEN','MOUSE','NOT WORKING','UPDATE','SOFTWARE','INSTALLATION','INSTALL','DATA TRANSFER']

finance_lst = ['SALARY','MONEY','CLAIM','FINANCE','REIMBURSEMENT']

query = "My employee name is incorrect and my laptop is having some issue"
CONFIG_FILE_PATH = "D:/help desk/helpdesk/config/"
CSV_FILE_PATH = "D:/help desk/helpdesk/storage/"
CONFIG_FILE_NAME = ''
CON_ENVIRONMENT = ''
myapi = launcher.SystemLauncher(storage_path=CSV_FILE_PATH,config_name=CONFIG_FILE_NAME,config_path=CONFIG_FILE_PATH)

def prepare_ticket(query):

    try:
        sentence_words = nltk.word_tokenize(query)
        sentence_words = [lemmatizer.lemmatize(word.upper()) for word in sentence_words]


        words = []

        for pattern in sentence_words:

            # take each word and tokenize it
            if pattern in employee_lst:
                ticket_id = '2002'
            elif pattern in tech_lst:
                ticket_id = '2001'
            elif pattern in finance_lst:
                ticket_id ='2003'
            else:
                ticket_id = '2001'
            words.append(ticket_id)

        words = list(filter(None,words))

        if len(words)>0:
            df = pd.DataFrame(columns=['ticket_id'],data=words)
            df['COUNT'] =1
            df = df.groupby('ticket_id')['COUNT'].sum()
            df = df.to_frame()
            df['TICKET_ID'] = df.index
            df = df.sort_values(by='COUNT',ascending=False)
            df= df.reset_index(drop=True)
            df['PROBLEM_DESCRIPTION'] = query
            df = df.drop(columns=['COUNT'])
            final_df = df.head(1)
        else:
            final_df = pd.DataFrame()
        return final_df.to_dict(orient='records')
    except Exception as err:
        return "Error while preparing ticket from mail : "+str(err)


def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()   

        
        latest_email_id = int(id_list[-1])

        # for i in range(latest_email_id,latest_email_id-1, -1):
        data = mail.fetch(str(latest_email_id), '(RFC822)' )
        for response_part in data:
            arr = response_part[0]
            if isinstance(arr, tuple):
                msg = email.message_from_string(str(arr[1],'utf-8'))
                email_subject = msg['subject']
                email_from = msg['from']
                return email_subject,email_from

    except Exception as e:
        traceback.print_exc() 
        print(str(e))

def create_tickets():
    try:
        email_subject,email_from =read_email_from_gmail()
        idx1 = email_from.index("<")
        idx2 = email_from.index(">")
        
        # length of substring 1 is added to
        # get string from next character
        email_from = email_from[idx1 + len("<"): idx2]
        
        ticket_data =prepare_ticket(query=email_subject)
        print(ticket_data)
        user_data =myapi.checkaccess(mail_id=email_from)
        
        access_status = user_data[0]['Access']
        if access_status == 'Granted':
            if len(ticket_data)>0:
                requested_data =  add_edit_ticket.NewTickets(
                    storage_path=CSV_FILE_PATH).raise_concern(
                        user_data=user_data,ticket_data=ticket_data)
    except Exception as err:
        print("error while creating ticket from mail :",err)
        return "error while creating ticket from mail :"+str(err)
    
create_tickets()