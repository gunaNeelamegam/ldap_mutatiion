# Workdrive Sync

## Generating Token Files

### `zoho-cred.txt`

* goto https://api-console.zoho.in/

* create server-based application.
    - Client name - `Workdrive API`
    - Homepage URL - `https://workdrive.zoho.in`
    - Authorized Redirect URIs - `http://localhost:8000/callback/`

* save `Client ID` and `Client Secret` into file like below.

   - zoho-cred.txt file

    ```
    1000.YOURxCLIENTxIDxxxxxxxxxxxxxxxxxxxxxxxx
    YourClientSecretxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

### `zoho-token.json`

* run generate_oauth_token.py

* open the link on browser and accept to the zoho OAuth prompt.

* your file will be token into `zoho-token.json`

## Description
Python Wrapper for Zoho Workdrive API.

## Usage
```
workdrive-upload <team> <remote-path> <local-file>
```
* Currently, Able to upload a file to team root folder.