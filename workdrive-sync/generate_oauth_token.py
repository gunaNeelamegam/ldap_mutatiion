"""Generate offline Token for Workdrive API"""
import os
import requests

from flask import Flask, request


TOKEN_FILE = "zoho-token.json" # output file

CRED_FILE = "zoho-cred.txt"
REDIRECT_URI = "http://localhost:8000/callback/"
SCOPES = "ZohoSearch.securesearch.READ,WorkDrive.team.CREATE,WorkDrive.team.READ,WorkDrive.team.UPDATE,WorkDrive.team.DELETE,WorkDrive.members.READ,WorkDrive.members.CREATE,WorkDrive.members.UPDATE,WorkDrive.members.DELETE,WorkDrive.teamfolders.CREATE,WorkDrive.teamfolders.READ,WorkDrive.teamfolders.UPDATE,WorkDrive.teamfolders.DELETE,WorkDrive.teamfolders.sharing.CREATE,WorkDrive.teamfolders.sharing.READ,WorkDrive.teamfolders.sharing.UPDATE,WorkDrive.teamfolders.sharing.DELETE,WorkDrive.teamfolders.admin.READ,WorkDrive.groups.CREATE,WorkDrive.groups.READ,WorkDrive.groups.UPDATE,WorkDrive.groups.DELETE,WorkDrive.files.CREATE,WorkDrive.files.READ,WorkDrive.files.UPDATE,WorkDrive.files.DELETE,WorkDrive.links.CREATE,WorkDrive.links.READ,WorkDrive.links.UPDATE,WorkDrive.links.DELETE,WorkDrive.comments.CREATE,WorkDrive.comments.READ,WorkDrive.comments.UPDATE,WorkDrive.comments.DELETE,WorkDrive.collection.CREATE,WorkDrive.collection.READ,WorkDrive.collection.UPDATE,WorkDrive.collection.DELETE,WorkDrive.datatemplates.CREATE,WorkDrive.datatemplates.READ,WorkDrive.datatemplates.UPDATE,WorkDrive.datatemplates.DELETE,WorkDrive.labels.CREATE,WorkDrive.labels.READ,WorkDrive.labels.UPDATE,WorkDrive.labels.DELETE,WorkDrive.libraries.CREATE,WorkDrive.libraries.READ,WorkDrive.libraries.UPDATE,WorkDrive.libraries.sharing.READ,WorkDrive.libraries.categories.CREATE,WorkDrive.libraries.categories.READ,WorkDrive.libraries.categories.UPDATE"

app = Flask(__name__)

def get_creds() -> tuple:
    """Getting zoho user id and client secret"""
    if not os.path.exists(CRED_FILE):
        zid = os.getenv("ZOHO_CLIENT_ID")
        secret = os.getenv("ZOHO_CLIENT_SECRET")
    else:
        with open(CRED_FILE, 'r',encoding="UTF-8") as cred:
            zid, secret = cred.readlines()
        zid = zid.strip()
        secret = secret.strip()
    return zid, secret


def save_to_file(txt):
    """Saving token json into TOKEN FILE"""
    with open(TOKEN_FILE, 'w', encoding="UTF-8") as token:
        token.write(txt)
    return True


def generate_token(code, redirect_uri):
    """Generating token json using code, zid and secret"""
    client_id, client_secret = get_creds()
    auth_token_url = f"https://accounts.zoho.in/oauth/v2/token?code={code}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code&client_id={client_id}"
    resp = requests.request("POST", auth_token_url, timeout=10)
    save_to_file(resp.text)
    return True


def generate_code(redirect_uri):
    """Generating offline code"""
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
    """Mock callback uri"""
    code_resp = request.args
    code_resp = code_resp.to_dict(flat=False)
    if code_resp.get('code'):
        code = code_resp['code'][0]
        if generate_token(code, REDIRECT_URI):
            return f"{all_routes}: Token saved"
    return "NOT GENERATED"


@app.route('/')
def index():
    """Index Page for Mock URI"""
    code = generate_code(REDIRECT_URI)
    if code:
        msg = "Trick oAuth Done"
    else:
        msg = "Code Generated"
    return msg

if __name__ == "__main__":
    # os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run("0.0.0.0", port=8000)
