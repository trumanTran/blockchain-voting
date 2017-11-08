import hashlib as hasher
import datetime as date


# Define what a voting block
class Block:
    def __init__(self, machine_id, timestamp, data, previous_hash):
        self.machine_id = machine_id
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    # Function to create hash of proposed block
    # Will replace this function once we know how to create digital signature with machine private key
    def hash_block(self):
        sha = hasher.sha256()
        sha.update((str(self.machine_id) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode("utf-8"))
        return sha.hexdigest()


# Generate genesis block
def create_genesis_block():
    # Admin will create create genesis block so that's where all machines will start
    # Manually construct a block with
    # arbitrary machhine_id and arbitrary previous hash
    return Block(0, date.datetime.now(), "Genesis Block", "0")


# Generate proposed block
def next_block(current_id, current_data, last_block):
    this_id = current_id
    this_timestamp = date.datetime.now()
    this_data = current_data
    this_hash = last_block.hash
    return Block(this_id, this_timestamp, this_data, this_hash)

# Open sample ballot txt file to parse and create list of races in order to create blockchain for each race
races = []
raceFile = open('test.txt','r')
lines = fhand.readlines()[2:]
raceFile.close
for line in lines:
    line = line.rstrip()
    words = line.split(':')
    races.append(words[0])

# Create the blockchain and add the genesis block
blockchain = [create_genesis_block()]
previous_block = blockchain[0]

# Add blocks to the chain

proposing_id = 1
proposed_data = [("banana", "queso"), ("red", "rojo"), ("school", "escuela")]

block_to_add = next_block(proposing_id, proposed_data, previous_block)
blockchain.append(block_to_add)
previous_block = block_to_add

print(blockchain[0].machine_id)
print(blockchain[0].hash)
print(blockchain[0].data)
print(blockchain[1].machine_id)
print(blockchain[1].data)
print(blockchain[1].hash)
print(blockchain[1].previous_hash)
