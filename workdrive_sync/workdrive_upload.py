import os
import sys
import json

from requests import request

CREDS_FILE = "zoho-cred.txt"
TOKEN_FILE = "zoho-token.json"
BASE_URL = "https://www.zohoapis.in/workdrive/api/v1"

# Need this variables while running from pipeline.
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")


def get_creds(cred_file) -> tuple:
    with open(cred_file, "r") as cred:
        zid, secret = cred.readlines()
    zid = zid.strip()
    secret = secret.strip()
    return zid, secret


def get_refresh_token(token_file) -> str:
    with open(token_file, "r") as token:
        auth = json.load(token)
    return auth.get("refresh_token")


def generate_auth_header() -> dict:

    global TOKEN_FILE, CREDS_FILE
    global ZOHO_CLIENT_ID, ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_SECRET

    if not ZOHO_CLIENT_ID and not ZOHO_CLIENT_SECRET and not ZOHO_REFRESH_TOKEN:
        ZOHO_REFRESH_TOKEN = get_creds(CREDS_FILE)
        ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET = get_refresh_token(TOKEN_FILE)
    url = f"https://accounts.zoho.in/oauth/v2/token?refresh_token={ZOHO_REFRESH_TOKEN}&client_secret={ZOHO_CLIENT_SECRET}&grant_type=refresh_token&client_id={ZOHO_CLIENT_ID}"
    resp = request("POST", url, timeout=10)
    token = json.loads(resp.text)
    auth_token = token.get("access_token")
    header = {"Authorization": f"Bearer {auth_token}"}
    return header


def get_zuid(header):
    url = f"{BASE_URL}/users/me"
    resp = request("GET", url, headers=header)
    if resp.ok:
        resp = json.loads(resp.text)
        attr = resp["data"]["attributes"]
        email = attr["email_id"]
        zuid = attr["zuid"]
        return zuid
    else:
        return "GET_ZUID_FAILED"


def get_upload_folder_id(header, org_id, team_id, remote_path):

    dirs = list(filter(None,remote_path.split("/")))

    if not dirs:
        return team_id

    upload_folder_id = ""
    parent_id = team_id

    dirs_to_create = dirs.copy()

    for i in range(len(dirs)):

        if i != 0:
            upload_folder_id = get_sub_folders(org_id, parent_id, dirs[i], header)
        else:
            upload_folder_id = get_team_sub_folder(org_id, team_id, dirs[i], header)

        if not upload_folder_id:
            print("Creating Folder", dirs_to_create)
            upload_folder_id = create_subfolder(parent_id, dirs_to_create, header)
            break

        dirs_to_create.remove(dirs[i])
        parent_id = upload_folder_id

    return upload_folder_id


def get_org_id(zuid, header):
    url = f"{BASE_URL}/users/{zuid}/teams"
    resp = request("GET", url, headers=header)
    org_id = ''
    if resp.ok:
        org_data  = resp.json()
        if org_data.get("data"):
            org_id = org_data["data"][0]["id"]
    return org_id if org_id else "GET ORG ID Failed"



def upload_file(filename, folder_id, auth, override=None):
    fname = os.path.basename(filename)
    override = "true" if override else "false"
    data = {
        "filename": f"{fname}",
        "parent_id": folder_id,
        "override-name-exist": override,
    }
    url = f"{BASE_URL}/upload"
    files = {"content": open(filename, "rb")}
    req = request("POST", url=url, files=files, data=data, headers=auth)
    if req.ok:
        resp = json.loads(req.text)
        resp = resp["data"][0]["attributes"]
        return resp.get("Permalink")
    return ""


def get_team_id(team_name, org_id, header) -> str:
    url = f"{BASE_URL}/teams/{org_id}/teamfolders"
    resp = request("GET", url, headers=header)
    folders = resp.json()["data"]
    team_folders = {}
    for folder in folders:
        id = folder["id"]
        name = folder["attributes"]["display_html_name"]
        team_folders[name] = id
        is_present = team_folders.get("attributes", {})
        if is_present:
            team_folders["attributes"] = folder["attributes"]
    team_id = team_folders.get(team_name)
    return team_id if team_id else ""


def get_team_sub_folder(org_id, team_id, query, header):
    url = f"{BASE_URL}/teams/{org_id}/records?search[name]={query}&filter[teamFolder]={team_id}&filter[type]=folder"
    url += "&page%5Blimit%5D=1&page%5Boffset%5D=0"
    resp = request("GET", url, headers=header)
    dir_id = ""
    if resp.ok:
        dir_data = resp.json()["data"]
        if dir_data:
            dir_id = dir_data[0]['id']
    return dir_id


def get_sub_folders(org_id, parent_id, query, header):
    url = f'{BASE_URL}/teams/{org_id}/records?search[name]={query}&filter[parentId]={parent_id}&filter[type]=folder'
    url += "&page%5Blimit%5D=1&page%5Boffset%5D=0"
    resp = request("GET", url, headers=header)
    dir_id = ""
    if resp.ok:
        dir_data = resp.json()
        if dir_data.get("data"):
            dir_id = dir_data['data'][0]['id']
    return dir_id


def create_subfolder(parent_id, sub_dirs, header):
    url = f"{BASE_URL}/files"
    final_dir_id = ""

    for dir in sub_dirs:
        req_data = {
        "data": {
            "attributes": {"name": f"{dir}", "parent_id": f"{parent_id}"},
            "type": "files"}
        }
        print(f"Creating Directory {dir}")
        resp = request("POST", url=url, json=req_data, headers=header)
        parent_data = resp.json()
        if parent_data.get("data"):
            parent_id = parent_data["data"]['id']
        final_dir_id  = parent_id

    return final_dir_id


def main():

    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <team-name> <remote-path> <local-path>")
        return

    team = sys.argv[1]
    remote_path = sys.argv[2]
    local_file = sys.argv[3]

    try:
        print("Generating Access Token")
        auth_header = generate_auth_header()

        print("Getting ZUID")
        zuid = get_zuid(auth_header)

        print("Getting ORG ID")
        org_id = get_org_id(zuid,auth_header)

        print("Verifying Team ID")
        team_id = get_team_id(team, org_id, auth_header)
        if not team_id:
            print(f"Couldn't find the team : {team}")
            exit(2)

        print("Getting Folder ID to upload")
        folder_id = get_upload_folder_id(auth_header, org_id, team_id, remote_path)
        if not folder_id:
            print(f"Couldn't find folder ID : {remote_path}")
            exit(3)

        print("Uploading file...")
        override = True
        file_link = upload_file(local_file, folder_id, auth_header, override)
        if file_link:
            print("File upload succeed")
            print(f"Workdrive Link: {file_link}")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()