# a collection of functions that allows to read/write google drive files 
import requests
import json
import pandas as pd


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

def get_google_doc(file_id, secrets_file):
    # read secrets json
    secrets = load_json(secrets_file)
    api_key = secrets['api_key']

    # Define the endpoint URL
    url = f"https://docs.googleapis.com/v1/documents/{file_id}?key={api_key}"
    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        print(f"data = {data}")
        # Extract the document title and content
        title = data['title']

        # Extract the text from the document
        text_content = ''
        for element in data.get('body').get('content'):
            if 'paragraph' in element:
                for text_element in element.get('paragraph').get('elements'):
                    text_run = text_element.get('textRun')
                    if text_run:
                        text_content += text_run.get('content')
        
        print(f"Title: {title}\n\n{text_content}")

    else:
        print(f"Failed to retrieve document. Status code: {response.status_code}")
        print(response.text)

    return

if __name__ == '__main__':
    # we test stuff here
    # '13Nu_jv8T21YsU25uUlZ8jhfFeYxzER1l' -> fileid test
    get_google_doc('13Nu_jv8T21YsU25uUlZ8jhfFeYxzER1l', './secrets.json')
