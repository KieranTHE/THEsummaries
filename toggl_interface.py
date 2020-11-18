import requests
import json
import logging
import base64
import sys
import pandas as pd

#set logging
logging.basicConfig(level=logging.DEBUG)

#read secrets
with open('secrets.json') as secrets_file:
  secrets = json.load(secrets_file)
logging.debug(secrets['toggl_api_key'])

#header and param details for api requests
string_api = secrets['toggl_api_key'] + ':' + "api_token"

headers = {
    'Authorization' : 'Basic '+ base64.b64encode(string_api.encode('ascii')).decode("utf-8"),
}

params={'user_agent':secrets['email'],'workspace_id':secrets['workspace_id']}


#me details
url='https://www.toggl.com/api/v8/me'
response=requests.get(url,headers=headers)
if response.status_code!=200:
    logging.error(response.text)
    quit()

response=response.json()
logging.debug(response)
email=response['data']['email']
logging.debug(email)

#reports
url='https://toggl.com/reports/api/v2/details'

response=requests.get(url,headers=headers,params=params)
if response.status_code!=200:
    logging.error(response.text)
    quit()

response=response.json()
response_df = pd.json_normalize(response['data'])
#logging.debug(response_df['project'])
response_df.rename(
    columns={
        'client':'CLIENT',
        'project':'PROJECT',
        'dur':'HOURS'
        }, 
    inplace=True)
grouped_df = response_df.groupby(['CLIENT','PROJECT'])['HOURS'].sum()
result_df = grouped_df.div(3600000).round(decimals=2)
logging.debug(result_df)
result_df.to_csv('result.csv')