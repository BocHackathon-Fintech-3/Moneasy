import random
from toolkit import *
import string
from Crypto.PublicKey.RSA import importKey
POS_ID_FILE = "posid.txt"

def extract_key(fname):
        key_f = open(fname, "rb")
        key = key_f.read()
        key_f.close()
        returnKey = importKey(key)
        return returnKey

def get_keys():
        public = extract_key("public.pem")
        private = extract_key("private.pem")
        return private,public

def send_data(data):
	def generate_transaction_id(length=64):
		lettersAndDigits = string.ascii_letters + string.digits
		return ''.join(random.choice(lettersAndDigits) for i in range(length))

	def get_pos_id():
		f=open(POS_ID_FILE,"r")
		pos_id = f.read().split("=")[-1].strip("\n")
		f.close()
		return pos_id

	transaction_id = generate_transaction_id()
	pos_id = get_pos_id()
	privatekey, publickey = get_keys()
	fullstr = '///'.join([transaction_id,data])
	signature = sign(privatekey, fullstr)
	#print(signature)
	#print(fullstr)
	#print(pos_id)
	return (signature, fullstr, pos_id)
        # package = transaction id//encrypted hash + pos id + data
