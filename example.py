import blockchain

#layout of what a voting station would do

#sample machine ID
machine_id = 1234


block_to_add = None

#Machine will receive genesis_block from server so that all machines have the same genesis block
#In that case genesis_block = whatver server gives it 
genesis_block = blockchain.create_genesis_block()

#machine will then create its own local blockchain utilitzing the genesis block given
blockchain.create_new_chain(genesis_block)

print("Genesis Block")
print("Machine ID: ", blockchain.chain[0].machine_id)
print("Time: ", blockchain.chain[0].timestamp)
print("Ballot: ", blockchain.chain[0].data)
print("Current Hash: ", blockchain.chain[0].hash)
print("Previous Hash: ", blockchain.chain[0].previous_hash, "\n")


# Voter will vote and data will be packaged into proposed block
proposed_data = [("Voter ID", "000001"), ("President", "Eric Schweitzer"), ("Senate", "Eric Schweitzer"), ("Mayor", "Eric Schweitzer")]
block_to_add = blockchain.next_block(machine_id, proposed_data)

# Once proposed block (block_to_add) is set, this is where machine will broadcast block_to_add to other nodes. Otherwise machine is waiting to accept another node's block_to_add

#Broadcast and receive broadcast function goes here 

# Once consensus is reached, nodes append block
blockchain.append_block(block_to_add)
print("First Block")
print("Machine ID: ", blockchain.chain[1].machine_id)
print("Time: ", blockchain.chain[1].timestamp)
print("Ballot: ", blockchain.chain[1].data)
print("Current Hash: ", blockchain.chain[1].hash)
print("Previous Hash: ", blockchain.chain[1].previous_hash, "\n")





