from Crypto.PublicKey import RSA
import os.path

def KeyGeneration():
    print ("Checking if both keys exist")
    if os.path.exists("private.pem") and os.path.exists("public.pem"):
        print ("Files already exist!")
    else:
        key = RSA.generate(2048)
        pv_key_string = key.exportKey()
        with open ("private.pem", "w") as prv_file:
            print("{}".format(pv_key_string.decode()), file=prv_file)
            print ("Private Key created!")
        pb_key_string = key.publickey().exportKey()
        with open ("public.pem", "w") as pub_file:
            print("{}".format(pb_key_string.decode()), file=pub_file)
            print ("Public Key created!")





