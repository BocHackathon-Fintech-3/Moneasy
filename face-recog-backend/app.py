# $ curl -XPOST -F "file=@filename.jpg" http://127.0.0.1:5001

import face_recognition
from flask import Flask, jsonify, request, redirect
from knn import predict
import json
import requests
from datetime import datetime
import smtplib
import ssl

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'knn/temp'
USERDATA_PATH = 'userdata/secretdata.json'
CREDITOR_DETAILS = {
	"boc_acc_id": "210334",
	"boc_sub_id": "Sub0001-002"
}
DIST_THRESHOLD = 0.5 #the lower the distance threshold, the more strict the algorithm will be

app = Flask(__name__)


def allowed_file(filename):
    if "." in filename:
        return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS
    return False


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    '''
    Possible:
    request.amount = amount traded
    request.pos = pos location
    request.file = pos ids
    '''
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        print(request.form)
        #if request.
        amount = request.form['amount']
        pos_id = request.form['pos']

        try:
            amount = float(amount)
        except:
            raise Exception("Invalid amount (not number/non existent?)")

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1.filename == '' or file2.filename == '':
            return redirect(request.url)

        files = [file1,file2]
        for file in files:
            if file and allowed_file(file.filename):
                # The image file seems valid! Detect faces and return the result.
                # file.save(os.path.join(UPLOAD_FOLDER, file.filename))
                face = detect_faces_in_image(file)
                print("Detected face")
                print(face)
                if face == False:
                    print("Too many faces")
                    continue #try the next file.
                account = match_face_to_account_details(face)
                if account == None:
                    print("User not registered properly.")
                    return "False"
                transactionSuccessful = make_transaction(account, CREDITOR_DETAILS, amount, pos_id)
                if transactionSuccessful:
                    send_email(account["email"], "invoice")
                    print("Transaction complete") #send request to raspberry pi to make lights green
                    return "True"
                print("Transaction failed") #send request to raspberry pi
        return "False"
        # If no valid image file was uploaded, show the file upload form:

def detect_faces_in_image(file_stream):
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    faces = predict(img,model_path="hi",distance_threshold=DIST_THRESHOLD)
    known_faces = 0
    print(faces)
    for face in faces:
        if face[0] != 'unknown':
            known_faces += 1
    if known_faces != 1:
        return False # either 0 or more than 1 face detected
    return faces[0][0]

def match_face_to_account_details(face):
    with open(USERDATA_PATH) as json_file:
        data = json.load(json_file)
        try:
            if data[face]["enabled"] == "true":
                return data[face] #{boc_acc_id: XX, boc_sub_id: XX}
            else:
                send_email(data[face]["email"], "fraud")
        except:
            return None

def make_transaction(debtor_details, creditor_details, amount, pos_id):
    response = requests.get(url = f"http://192.168.10.140:3000/payFace?creditorIban={creditor_details['boc_acc_id']}&debtorIban={debtor_details['boc_acc_id']}&amount={float(amount)}&subId={creditor_details['boc_sub_id']}")._content
    if response == "Complete":
        return True
    elif response == "wrong" or response == "missing info":
        return False
    else:
        print(response)


def send_to_raspberry(request):
    raise NotImplementedError

def buildEmail(emailType,additional):
    ACCEPTABLE_TYPES = ["fraud", "registration", "invoice"]
    current_time = datetime.now()
    timestampStr = current_time.strftime("%H:%M %A, %B %d, %Y")
    if type in ACCEPTABLE_TYPES:
        if type == "fraud":
            content = f"At We have detected suspicious activity on your Eaze account, at {timestampStr}. As such, we blocked the transaction and temporarily disabled your account. To re-enable your account, "
        elif type == "registration":
            content = f"Succesfully registered on Eaze at {timestampStr}. If this was done in error, or you wish to opt out of the service, please click here: http://www.optout.com"
        elif type == "invoice":
            content = f"Transaction complete: paid {str(additional[0])} at {str(additional[1])}.\n Time of transaction: {timestampStr}\n If this was not you, please click here to temporarily lock your Eaze account."
    return content

def send_email(email, emailType, additional=[]):
    content = buildEmail(emailType,additional)
    port = 465
    email = "eazepay@gmail.com"
    password = "fintech!"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
        server.login(email, password)
        server.sendmail(content)
    return True

def disable_account():
    raise NotImplementedError

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
