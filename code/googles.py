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

def read_google_doc(secrets_file):
    return secrets_file


if __name__ == '__main__':
    df = read_google_sheet('secrets.json')
    print(df)
