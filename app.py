import json
import random
from flask import Flask, jsonify, redirect, render_template, request, url_for
import blockchain2
from m import PubSub
import wallet
import threading

 # Create a Flask application
app = Flask(__name__)
 # Create a Blockchain instance
blockchain = blockchain2.Blockchain()
 # Create an ImageHandling instance
ihandle = blockchain2.imageHandeling()
 # Create a PubSub instance
pubsub = PubSub(blockchain)
 # Create a thread to receive messages
mythread = threading.Thread(target=pubsub.recieve)
mythread.start()


 # Create a cuser class
class cuser:
    def __init__(self):
        self.responce = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
        self.logsts = ''
        self.pubk = ''
        self.up = None
     # Get the content of the user.json file
    def get_content(self):
        with open('templates/user.json','r') as f:
            content = f.read()
        content = json.loads(content)
        self.up = content
        return content
     # Sign in a user
    def sing_in(self, public_key, private_key):
        content = self.get_content()
        k = 'wrong'
        for cont in content['users']:
            if str(cont['public_key']) == public_key and str(cont['private_key']) == private_key:
                k = 'logged in'
                self.pubk = public_key
                break
            else:
                k = 'wrong'
        self.logsts = k
        return k
     # Sign up a user
    def sing_up(self):
        content = self.get_content()
        lresponce = list(content['users'])
        k = wallet.gen_key()
        lresponce.append(k)
        responce = {"users":lresponce}
        with open('templates/user.json','w') as fw:
            fw.write(json.dumps(responce, indent=3))
        return k
     # Set the response
    def local(self, responce):
        if responce is not None:
            self.responce = responce
     # Save the response to a file
    def save_file(self):
        with open('templates/response.json','w') as f:
            f.write(json.dumps(self.responce, indent=3))

 # Create an instance of the cuser class
user = cuser()


 # Route for the feed page
@app.route('/feed')
def feed():
    user.save_file()
    read = blockchain2.readData()
    data = read.retrive()
    return render_template("feed.html", data=data)
 # Route for the homepage
@app.route('/')
def homepage():
    return render_template("index.html")
 # Route for the about page
@app.route('/about')
def about():
    return render_template('login.html', data={'public_key':'','private_key':'','lg':''})
 # Route for signing up
@app.route('/sing_up/')
def singup():
    return render_template("login.html" , data=user.sing_up())
 # Route for signing in
@app.route('/sing_in/', methods=['GET','POST'])
def singin():
    if request.method == 'POST':
        public_key = request.form['public-key']
        private_key = request.form['private-key']
    data = user.sing_in(public_key, private_key)
    if data == 'wrong':
        return data
    return redirect(url_for('homepage'))
 # Route for displaying an image
@app.route('/', methods=['GET', 'POST'])
def display():
    if request.method == 'POST':
        result = request.files['newimg']
        result.save('/img.jpg')
        return redirect(url_for('homepage'))
 # Route for mining a block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    if user.logsts == 'logged in':
        content = user.up
        lresponce = list(content['users'])
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)
        imgres = ihandle.encode_string()
        block = blockchain.create_blockchain(proof, previous_hash, imgres)
        pubsub.broadcastChain(blockchain.chain)
        response = {'message': 'Block mined!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'image' : block['image'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash']}
        for cont in lresponce:
            if str(cont['public_key']) == user.pubk:
                cont['posts'].append(response)
        fresponce = {"users":lresponce}
        with open('templates/user.json','w') as fw:
            fw.write(json.dumps(fresponce, indent=3))
        return jsonify(response), 200
    else:
        return render_template('login.html', data={'public_key':'','private_key':'','lg':'Need to Sign in'})
 # Route for getting the chain
@app.route('/get_chain', methods=['GET'])
def get_chain():
   response = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
   user.local(response)
   return redirect(url_for('homepage'))
 # Generate a random port
port = random.randrange(5000, 5666)
 # Run the application
app.run(host='0.0.0.0', port=port , debug=True)
 # Join the thread
mythread.join()