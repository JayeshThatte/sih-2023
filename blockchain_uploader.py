# Create a webhook in python
# On creation of roll number -> upload to blockchain (aadhaar number , roll number) -> get cid
# Update biometrics_data -> set cid , where aadhaar number = given

from flask import Flask, request, abort
import subprocess
import requests
import os
import re
import json

headers = {"Authorization": "Bearer HT-DA847CTUgK9jhg0QbN87Ivo15DTWu"}

app = Flask(__name__)

def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

@app.route('/upload_blockchain', methods=['POST'])
def get_webhook():
    if request.method == 'POST':
        data = request.json
        aadhaar_no = data.get('aadhaar_number','')
        roll_no = data.get('roll_no','')
        data = {"roll_no":roll_no,"aadhaar_no":aadhaar_no}
        with open('bc_data.txt','w',encoding='utf-8',errors='ignore') as f:
            json.dump(data,f)

        p = execCmd('w3 up bc_data.txt')
        url = re.findall(r'https://w3s\.link/ipfs/[a-zA-Z0-9]+',p)[0]+'/bc_data.txt'
        # url = 'tester/bc_data.txt'
        print("Location := ",url)
        r = requests.request('PATCH',f'http://localhost:8055/items/biometric_data/{aadhaar_no}',json={"blockchain_link":url},headers=headers)
        print(r.text)
        return {"path":url}
    else:
        abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0')