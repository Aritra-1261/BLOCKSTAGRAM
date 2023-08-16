import pickle
import time
import redis
CHANNELS = {
  "TEST": "TEST",
  "BLOCKCHAIN": "BLOCKCHAIN"
}

class PubSub:
    
    def __init__(self, blockchain):
        """
        Initialize the PubSub class.
        :param blockchain: The blockchain object.
        """
        self.blockchain = blockchain
        self.publisher = redis.Redis()
        self.subscriber = redis.Redis().pubsub()
        self.subscriber.subscribe(CHANNELS["BLOCKCHAIN"])

    def recieve(self):
        #Receive messages from the subscribed channel.
        for message in self.subscriber.listen():
            time.sleep(3)
            self.handleMessage(message)
        

    def handleMessage(self, message):
        #Handle the received message. :param message: The received message.
        channel = message["channel"].decode("utf-8")
        if message['type'] == 'message':
            message = pickle.loads(message['data'])
            print(f"Message received. Channel: {channel}. Message: {message}")

            parseMessage = message

            if channel == CHANNELS["BLOCKCHAIN"]:
                self.blockchain.replacechain(parseMessage)

    def kublish(self, channel, message):
        """
        Publish a message to the specified channel.
        :param channel: The channel to publish to.
        :param message: The message to publish.
        """
        self.publisher.publish(channel, message)

    def broadcastChain(self,chain):
        """
        Broadcast the chain to the blockchain channel.
        :param chain: The chain to broadcast.
        """
        self.kublish(
            channel=CHANNELS["BLOCKCHAIN"],
            message=pickle.dumps(chain)
        )
