import hashlib as hasher
import datetime as date

# Variables for chain and previous block
chain = None
previous_block = None

# Define what a voting block is
class Block:
    def __init__(self, machine_id, timestamp, data, previous_hash):
        self.machine_id = machine_id
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    # Function to create hash of proposed block
    def hash_block(self):
        sha = hasher.sha256()
        sha.update((str(self.machine_id) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode("utf-8"))
        return sha.hexdigest()

# Generate genesis block
def create_genesis_block():
    # Admin will create create genesis block so that's where all machines will start
    # Manually construct a block with
    # arbitrary machhine_id and hash of 'NULL'
    return Block(0, date.datetime.now(), "Genesis Block", "NULL")
    
    # Create the blockchain and add the genesis block
def create_new_chain(genesis):
    global chain
    global previous_block
    chain = []
    chain.append(genesis)
    previous_block = chain[0]

# Generate proposed block
def next_block(current_id, current_data):
    global previous_block
    this_id = current_id
    this_timestamp = date.datetime.now()
    this_data = current_data
    this_hash = previous_block.hash
    return Block(this_id, this_timestamp, this_data, this_hash)
    
# Append block to blockchain
def append_block(proposed_block):
    global chain
    global previous_block
    chain.append(proposed_block)
    previous_block = proposed_block
    
