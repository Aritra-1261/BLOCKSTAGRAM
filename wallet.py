from Crypto.PublicKey import RSA

def gen_key():
    key_pair = RSA.generate(1024)

    public_key = key_pair.publickey().exportKey()
    private_key = key_pair.exportKey()

    responce={
        'public_key':(public_key.decode('utf-8')).replace('\n',''),
        'private_key':(private_key.decode('utf-8')).replace('\n',''),
        'posts':[],
        'lg':''
    }
    return responce



    


            


