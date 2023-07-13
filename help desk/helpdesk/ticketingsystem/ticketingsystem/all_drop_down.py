"""
This module will be used to view all the config details.
"""
import pandas as pd

class All_dropdown():

    def __init__(self,storage_path):
        self.storage_path = storage_path

    def form_details(self):


        try:
            ticket_types_df = pd.read_csv(filepath_or_buffer=self.storage_path+"ticket_types.csv")
            user_class_df = pd.read_csv(filepath_or_buffer=self.storage_path+"user_type.csv")
            ticket_types_df['TICKET_DESCRIPTION'] = ticket_types_df['TICKET_DESCRIPTION'].apply(lambda x:x.split(","))
            user_class_df['ACCESS_TYPE'] = user_class_df['ACCESS_TYPE'].apply(lambda x:x.split(","))

            prepared_data = {
                "USER_CLASS":user_class_df.to_dict(orient="records"),
                "TICKET_CLASS":ticket_types_df.to_dict(orient="records")
            }
            return prepared_data
        except Exception as err:
            return "Error in form details : "+str(err)