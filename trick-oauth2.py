"""Generate offline Token for Workdrive API"""

from flask import Flask, request

import os
import sys
import requests


TOKEN_FILE = "zoho-token.json" # output file

CRED_FILE = "zoho-cred.txt"
REDIRECT_URI = "http://localhost:8000/callback/"
SCOPES = "WorkDrive.team.CREATE,WorkDrive.team.READ,WorkDrive.team.UPDATE,WorkDrive.team.DELETE,WorkDrive.members.READ,WorkDrive.members.CREATE,WorkDrive.members.UPDATE,WorkDrive.members.DELETE,WorkDrive.teamfolders.CREATE,WorkDrive.teamfolders.READ,WorkDrive.teamfolders.UPDATE,WorkDrive.teamfolders.DELETE,WorkDrive.teamfolders.sharing.CREATE,WorkDrive.teamfolders.sharing.READ,WorkDrive.teamfolders.sharing.UPDATE,WorkDrive.teamfolders.sharing.DELETE,WorkDrive.teamfolders.admin.READ,WorkDrive.groups.CREATE,WorkDrive.groups.READ,WorkDrive.groups.UPDATE,WorkDrive.groups.DELETE,WorkDrive.files.CREATE,WorkDrive.files.READ,WorkDrive.files.UPDATE,WorkDrive.files.DELETE,WorkDrive.links.CREATE,WorkDrive.links.READ,WorkDrive.links.UPDATE,WorkDrive.links.DELETE,WorkDrive.comments.CREATE,WorkDrive.comments.READ,WorkDrive.comments.UPDATE,WorkDrive.comments.DELETE,WorkDrive.collection.CREATE,WorkDrive.collection.READ,WorkDrive.collection.UPDATE,WorkDrive.collection.DELETE,WorkDrive.datatemplates.CREATE,WorkDrive.datatemplates.READ,WorkDrive.datatemplates.UPDATE,WorkDrive.datatemplates.DELETE,WorkDrive.labels.CREATE,WorkDrive.labels.READ,WorkDrive.labels.UPDATE,WorkDrive.labels.DELETE,WorkDrive.libraries.CREATE,WorkDrive.libraries.READ,WorkDrive.libraries.UPDATE,WorkDrive.libraries.sharing.READ,WorkDrive.libraries.categories.CREATE,WorkDrive.libraries.categories.READ,WorkDrive.libraries.categories.UPDATE"

app = Flask(__name__)

def get_creds() -> list:
    if not os.path.exists("zoho-cred.txt"):
        id = os.getenv("ZOHO_CLIENT_ID")
        secret = os.getenv("ZOHO_CLIENT_SECRET")
    else:
        with open(CRED_FILE, 'r') as cred:
            id, secret = cred.readlines()
        id = id.strip()
        secret = secret.strip()
    return id, secret


def save_to_file(txt):
    with open(TOKEN_FILE, 'w') as token:
        token.write(txt)
    return True


def generate_token(code, redirect_uri):
    client_id, client_secret = get_creds()
    auth_token_url = f"https://accounts.zoho.in/oauth/v2/token?code={code}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code&client_id={client_id}"
    resp = requests.request("POST", auth_token_url)
    # print(resp.text)
    save_to_file(resp.text)
    return True


def generate_code(redirect_uri):
    client_id = get_creds()[0]
    access_type = "offline"
    code_url = f"https://accounts.zoho.in/oauth/v2/auth?scope={SCOPES}&client_id={client_id}&response_type=code&access_type={access_type}&redirect_uri={redirect_uri}&state=register"
    print('#'* 20)
    print(code_url)
    print('#'* 40)
    print("Navigate to the above link and accept")
    print('#'* 40)
    enter = ""
    while not enter:
        enter = input("Press Enter to continue !")
    return enter


@app.route("/<all_routes>/", methods=["GET", "POST"])
def callback(all_routes):
    code_resp = request.args
    code_resp = code_resp.to_dict(flat=False)
    if code_resp.get('code'):
        code = code_resp['code'][0]
        # print(code)
        if generate_token(code, REDIRECT_URI):
            return "File saved "
    return "NOT GENERATED"
    

@app.route('/')
def index():
    code = generate_code(REDIRECT_URI)
    if code:
        return "Trick oAuth Done"
    else:
        return "Code Generated"
    

if __name__ == "__main__":
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run("0.0.0.0", port=8000)