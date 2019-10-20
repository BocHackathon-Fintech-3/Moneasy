# $ curl -XPOST -F "file=@filename.jpg" http://127.0.0.1:5001
import os, sys
import face_recognition
from flask import Flask, jsonify, request, redirect
from knn import predict
from knn import train
import json
import requests
from datetime import datetime
import smtplib
import ssl
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
sys.path.insert("email_templates",0)
from build_email import buildEmail
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

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



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
# ---------------------------- RECOGNITION -------------------------------------------
		if 'amount' in request.form.keys() and 'pos' in request.form.keys():
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
						send_email(account["email"], "receipt", "Your Eaze Receipt", additional={randomString(),account["email"],pos_id,"Nicosia, Cyprus",datetime.now().strftime("%B %d, %Y"), amount})
						print("Transaction complete") #send request to raspberry pi to make lights green
						return "True"
					print("Transaction failed") #send request to raspberry pi
			return "False"
# ----------------------------- REGISTRATION ----------------------------------------
		elif 'imagecnt' in request.form:
			email = request.form['email']
			username = randomString()
			data = json.load(open('userdata/secretdata.json'))
			while username in data:
				username = randomString()
			boc_acc_id = request.form['boc_acc_id']
			boc_sub_id = request.form['boc_sub_id']
			imagecnt = int(request.form['imagecnt'])
			os.mkdir('knn/train/'+username)
			data[username] = {
				"email": email,
				"boc_acc_id": boc_acc_id,
				"boc_sub_id": boc_sub_id,
				"location": "Mitsero, Cyprus"
			}
			json.dump(data, open('userdata/secretdata.json', 'w', encoding='utf-8'))
			for image_id in range(imagecnt):
				# Save Image File in the training directory
				(request.files["image"+str(image_id)]).save('knn/train/'+username+'/'+str(image_id)+'.jpg')
			sendEmail(email, "registration", "Registration complete.")
			train('knn/train/', model_save_path='hi')

			return "complete!"

		return "true"



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

def send_email(email, emailType, subjectline, additional={}):
	content = buildEmail(emailType,additional)
	port = 465
	my_email = "eazepay@gmail.com"
	password = "fintech!"
	context = ssl.create_default_context()
	message = MIMEMultipart("alternative")
	message["Subject"] = subjectline
	message["From"] = my_email
	message["To"] = email
	part1 = MIMEText(content,"html")
	message.attach(part1)
	with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
		server.login(email, password)
		server.sendmail(my_email, email, message.as_string())
	return True

def disable_account():
	raise NotImplementedError

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5001, debug=True)
