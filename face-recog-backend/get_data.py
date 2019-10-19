# handles digitally signed requests from POS's, checks if the requests
# coming from legitimate POS's as opposed to malicious/fraudulent ones

from Crypto.PublicKey.RSA import importKey
import sys
sys.path.insert(1, '../encryption')
from toolkit import verify

def get_data(incoming):
    def extract_key(fname):
        try:
            key_f = open(fname, "rb")
            key = key_f.read()
            key_f.close()
            returnKey = importKey(key)
            return returnKey
        except:
            return None

    FOLDER = "pos_keys/"

    def find_public_key(pos_id):
        fname = path+pos_id+".pem"
        return extract_key(fname)

    #incoming: (signature, fullstr, pos_id)
    signature = incoming[0]
    data = incoming[1]
    pos_id = incoming[2]
    publickey = find_public_key(pos_id)
    if publickey == None:
        return False #POS is not registered, malicious actor
    if verify(publickey, data, signature):
        return True
    return False #man in the middle attack
