""" Module to send mail using email and password"""

import smtplib
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication



class SendMail():
    """
    This class will be used to send mails to anyone.
    
    """

    def __init__(self,mail_cc=None,body=None,recipients=None,subject=None):
        self.sender = "shiva.chandrakanti@factspan.com"
        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.mail_cc =mail_cc

    def create_message(self):
        """
        This function will be used to prepare the message which user want to send.
        """

        try:
            print(self.recipients)
            emaillist = [elem.strip() for elem in self.recipients.split(',')]
            print(emaillist)
        except:
            emaillist = [self.recipients.strip()]

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.subject
            msg['From'] = self.sender
            msg['To'] = ",".join(x for x in emaillist)
            msg['Reply-to'] = 'N/A'
            if self.mail_cc is not None:
                print(self.mail_cc)
                msg['CC']=",".join(x.strip() for x in self.mail_cc)
            msg.preamble = 'Multipart massage.\n'

            if self.body is not None:
                part_body = MIMEText(self.body,'html')
                msg.attach(part_body)
                # print("#########")
                # if self.html_tag is not None:
                #     print("html_____________tag")
                #     msgText = MIMEText(self.html_tag, 'html')
                #     msg.attach(msgText)
                # msgText = MIMEText('\n\n')
                # msg.attach(msgText)               
                # if self.regards is None:
                #     regards_by = '''
                #                 <html>
                #                     <body>
                #                         Thanks & Regards<br>
                #                         RRE Team
                #                     </body>
                #                 </html>'''
                # else:
                #     regards_by = self.regards
                # part_regard = MIMEText(regards_by,'html')
                # msg.attach(part_regard)
                # part_space = MIMEText('\n\n')
                # msg.attach(part_space)
                # if self.footer is None:
                #     footer = '''<html>
                #                     <body>
                #                          <i>Note: This as an auto generated mail, please don't reply</i>.
                #                     </body>
                #                 </html>'''
                # else:
                #     footer = self.footer
                # part_footer = MIMEText(footer,'html')    
                # msg.attach(part_footer)      
                         
                                
                print(msg)
                return msg
            else:
                return "Please provide the content"
            
        except Exception as err:
            print("Error while preparing message : ",err)
            return "Error while preparing message : "+str(err)

    def send_message(self,password=None):
        
        try:
            password='Shiva@1710'
            emaillist = [elem.strip() for elem in self.recipients.split(',')]
        except:
            emaillist = [self.recipients.strip()]
            
        if self.mail_cc is not None:
            emaillist=emaillist+self.mail_cc

        msg = self.create_message()
        
        try:
            server = smtplib.SMTP("smtp.gmail.com:587")
            server.ehlo()
            server.starttls()
            print("1")
            server.login(self.sender, password)
            print("2")
            
            server.sendmail(msg['From'], emaillist, msg.as_string())
            print("Email Sent")
            return "Email Sent"
        except Exception as err:
            print("Error while sending mail : ",err)
            return "Error while sending mail : "+str(err)
       

