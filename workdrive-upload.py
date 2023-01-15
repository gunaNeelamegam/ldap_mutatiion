from sys import argv
from requests import request, get, post

import os.path
import json

CREDS_FILE = "zoho-cred.txt"
TOKEN_FILE = "zoho-token.json"
BASE_URL = "https://www.zohoapis.in/workdrive"


def get_creds(cred_file) -> list:
    with open(cred_file, 'r') as cred:
        id, secret = cred.readlines()
    id = id.strip()
    secret = secret.strip()
    return id,secret


def get_refresh_token(token_file) -> str:
    with open(token_file, 'r') as token:
        auth = json.load(token)
    return auth.get("refresh_token")


def generate_auth_header(refresh_token, creds) -> str:
    url = f"https://accounts.zoho.in/oauth/v2/token?refresh_token={refresh_token}&client_secret={creds[1]}&grant_type=refresh_token&client_id={creds[0]}"
    resp = request("POST", url)
    token = json.loads(resp.text)
    auth_token = token.get("access_token")
    header = { "Authorization" : f"Bearer {auth_token}" }
    return header


def get_api_data(response) -> list:
    json_data = json.loads(response.text)
    json_data = json_data["data"]
    return json_data


def get_zuid(header):
    url = f"{BASE_URL}/api/v1/users/me"
    resp = request("GET", url, headers=header)
    if resp.ok:
        resp = json.loads(resp.text)
        attr = resp["data"]["attributes"]
        email = attr["email_id"]
        zuid = attr["zuid"]
        return zuid
    else: 
        return "GET_ZUID_FAILED"


def get_org_id(zuid, header):
    url = f"{BASE_URL}/api/v1/users/{zuid}/teams"
    resp = request("GET", url, headers=header)
    team_data = json.loads(resp.text)
    return team_data["data"][0]["id"]


def upload_file(fname, folder_id, auth):
    filename = os.path.basename(fname)
    data = {"filename" : f"{fname}",
            "parent_id" : folder_id
            }
    url = f"{BASE_URL}/api/v1/upload"
    files = { 'content' : open(filename, 'rb') }
    req = request("POST", url=url, files=files ,data=data, headers=auth)
    if req.ok:
        resp = json.loads(req.text)
        resp = resp["data"][0]["attributes"]
        return resp.get("Permalink")
    return None


def list_team_folders(team_id, header):
    url = f"{BASE_URL}/api/v1/teams/{team_id}/teamfolders"
    resp = request("GET", url, headers=header)
    folders = json.loads(resp.text)['data']
    team_folders = {}
    for dir in folders:
        id = dir['id'] 
        name = dir['attributes']['display_html_name']
        team_folders[name] = id
    return team_folders

def search_team_folder(team_id, query, header):
    search_type = ["all", "name", "content"]
    url = f"{BASE_URL}/api/v1/teams/{team_id}/records?search[{search_type[1]}]={query}"
    resp = request("GET", url, headers=header)
    if resp.ok:
        print(resp.text)
        return resp.text
    else:
        print(resp.text)


def list_sub_folders(team_id, auth):
    url = f"{BASE_URL}/api/v1/teamfolders/{team_id}/folders"
    resp = request("GET", url,headers=auth)
    data = get_api_data(resp)
    sub_folders = {}
    for i in data:
        id = i['id']
        name = i['attributes']['display_html_name']
        has_folder = i['attributes']['has_folders']
        sub_folders[name] = [id, has_folder]
    return sub_folders


def create_subfolder(id, name, auth):
    url = f"{BASE_URL}/api/v1/files"
    req_data = {  "data": {
        "attributes": {
         "name": f"{name}",
         "parent_id": f"{id}" }, 
          "type": "files" } }
    resp = request("POST", url=url, json=req_data, headers=auth)
    resp_data = json.loads(resp.text)
    id = resp_data['data']['id']
    return id


def rename_resource(id, name, auth):
    url = f"{BASE_URL}/api/v1/files/{id}"
    req_data = { 
        "data": {
        "attributes": {
        "name": f"{name}" },
        "type": "files"}
        }
    resp = request("PATCH",url=url, json=req_data, headers=auth)
    if resp.ok:
        print("File Renamed")


if __name__ == "__main__":

    if len(argv) != 4:
        exit(1)

    team_folder = argv[1]
    remote_folder = argv[2]
    filename = argv[3]
 
    creds = get_creds(CREDS_FILE)
    refresh_token = get_refresh_token(TOKEN_FILE)
    auth_header = generate_auth_header(refresh_token, creds)
    
    print(" Getting ZUID ".center(40, "#"))
    zuid = get_zuid(auth_header)

    print(" Getting ORG ID ".center(40, "#"))
    org_id = get_org_id(zuid, auth_header)
    print(f"ORG ID : {org_id}")
    
    print(" Searching Team id ".center(40, "#"))
    team_folders = list_team_folders(org_id, auth_header)
    team_id = team_folders.get(team_folder)
    print(f"Found : {team_id}")

    # print(" Uploading file ".center(40, "#"))
    # link = upload_file(filename, team_id, auth_header)
    # print(f"Link : {link}")

    # print("Listing Subfolders".center(40, '#'))
    # subfolders = list_sub_folders(team_id, auth_header)
    # print(subfolders)

    # print("creating sub folder")
    # folder_id = create_subfolder(team_id, "thisisit", auth_header)
    # print(f"Folder ID : {folder_id}")

    print("searching folder")
    search_resp = search_team_folder(team_id,"test",auth_header)
    print(f"Folder ID : {search_resp}")