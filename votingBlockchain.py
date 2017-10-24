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
        sha.update(str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash))
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


# Create the blockchain and add the genesis block
blockchain = [create_genesis_block()]
previous_block = blockchain[0]


# Add blocks to the chain

block_to_add = next_block(proposing_id, proposed_data, previous_block)
blockchain.append(block_to_add)
previous_block = block_to_add