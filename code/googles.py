# a collection of functions that allows to read/write google drive files 
import requests
import json
import pandas as pd
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request


def load_json(file):
    with open(file, 'r') as _file:
        output = json.load(_file)
    return output

def read_google_sheet(secrets_file, sheet_name='Sheet1'):
    # read secrets json
    secrets = load_json(secrets_file)
    api_key = secrets['api_key']
    sheet = secrets['authors_sheet_id']
    # construct url and request
    range = sheet_name
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet}/values/{range}?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        values = json_data.get('values', [])
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}. Reason: {response.text}")

    # values is an array where each item is a row, we can turn that to a pandas dataframe
    names = values[0]
    rows = values[1:]
    # sometimes some rows have missing values at the end so let's pad them
    max_len = len(names)
    rows2 = [a_row + [None]*(max_len - len(a_row)) for a_row in rows]
    df = pd.DataFrame(rows2, columns=names)
    return df

def list_google_docs(secrets_file):
    # read secrets json
    secrets = load_json(secrets_file)
    api_key = secrets['api_key']
    drive = secrets['corpora_drive_id']
    # build the endpoint url
    url = f"https://www.googleapis.com/drive/v3/files?q='{drive}'+in+parents&key={api_key}"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        files = response.json().get('files', [])
    else:
        print(f"Failed to retrieve files. Status code: {response.status_code}")
        print(f"Debug text: {response.text}")
        return None, None

    # stack file ids and names for each entry
    ids = []
    names = []
    for a_file in files:
        if a_file['kind'] == 'drive#file':
            ids.append(a_file['id'])
            names.append(a_file['name'])
    return ids, names

def authenticate(scopes=['https://www.googleapis.com/auth/documents.readonly',], secrets='secrets_oauth2.json'):
   # authenticate with Google OAuth2.0 and return the service
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # if there are no (valid) credentials available, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets, scopes)
            creds = flow.run_local_server(port=0)
            # save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    return build('docs', 'v1', credentials=creds)

def get_google_doc(file_id):

    # create an authenticated service
    service = authenticate()
    print(service.documents().get(documentId=file_id).body())

    # get the document content using the Docs API
    try:
        doc = service.documents().get(documentId=file_id).execute()
        # doc = requests.get(f"https://docs.googleapis.com/v1/documents/{file_id}")
        print(f"request done! {doc}")
        print(doc.text)
        return doc
    except HttpError as error:
        print(f"An error occurred: {error}")
        print(f"An error occurred: {error.resp.status}")
        print(error.resp.reason)
        print(error.content.decode())
    return

if __name__ == '__main__':
    # we test stuff here
    # '13Nu_jv8T21YsU25uUlZ8jhfFeYxzER1l' -> fileid test
    # get_google_doc('13Nu_jv8T21YsU25uUlZ8jhfFeYxzER1l', './secrets.json')
    # response = authenticate()
    file_id = "13Nu_jv8T21YsU25uUlZ8jhfFeYxzER1l"
    doc = get_google_doc(file_id)
    print(f"doc = {doc}")
