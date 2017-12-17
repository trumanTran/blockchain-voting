import socket
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import pickle

from Crypto import Random


#Generate private and public keys
def Generate_Private_Key():
    random_generator = Random.new().read
    private_key = RSA.generate(1024, random_generator)
    return private_key

    
def Sign_Block(block_to_add, private_key):
    print(private_key)    
    try:
        b = pickle.dumps(block_to_add)
        h = SHA256.new(b)
        #print(h)
    except:
        print("SHA256 is dumb")
    try:
        Signed_Block = pkcs1_15.new(private_key).sign(h)
    except:
        print("Signing failed")
    return Signed_Block

def Verify_Block(block_to_add, Signed_Block, public_key):
    print(public_key)
    try:
        b = pickle.dumps(block_to_add)
        h = SHA256.new(b)
    except:
        print("There is a problem here")
    try:
        pkcs1_15.new(public_key).verify(h, Signed_Block)
        print("Valid")
    except:
        print("I totally messed up somewhere")
    #b = pickle.loads(Signed_Block)
