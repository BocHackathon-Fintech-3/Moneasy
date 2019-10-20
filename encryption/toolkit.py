import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64

def rsakeys():
	length = 1024
	privatekey = RSA.generate(length, Random.new().read)
	publickey = privatekey.publickey()
	return privatekey, publickey

def encrypt(publickey, plaintext):
	ciphertext = publickey.encrypt(plaintext.encode(),32)[0]
	b64cipher = base64.b64encode(ciphertext)
	return b64cipher

def decrypt(privatekey, b64cipher):
	decoded_ciphertext = base64.b64decode(b64cipher)
	plaintext = privatekey.decrypt(decoded_ciphertext).decode()
	return plaintext

def sign(privatekey, data):
	return base64.b64encode(str((privatekey.sign(data.encode(),''))[0]).encode())

def verify(publickey, data, sign):
	return publickey.verify(data.encode(), (int(base64.b64decode(sign)),))


