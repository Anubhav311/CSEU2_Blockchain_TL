# Paste your version of blockchain.py from the client_mining_p
# folder here
# Paste your version of blockchain.py from the basic_block_gp
# folder here
import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1, # length of the chain plus 1
            'timestamp': time(), # use the time function
            'transactions': self.current_transactions, # ref to the current transactions of the blockchain
            'proof': proof, # the proof provided to the function
            'previous_hash': previous_hash or self.hash(self.chain[-1]), # the hash supplied to the function or the one derived from previous block
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def new_transactions(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block

        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the block that will hold this transaction
        """
        # append the sender, recipient and amount to the current transactions
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        # return last block's index + 1
        return self.last_block['index'] + 1

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        string_object = json.dumps(block, sort_keys=True)

        # TODO: Create the block_string
        block_string = string_object.encode()

        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(block_string)

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand
        hex_hash = raw_hash.hexdigest()

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """
        # create a block string from the encoded dump
        block_string = json.dumps(self.last_block, sort_keys=True).encode()

        # set initial proof values
        proof = 0

        # loop over the proofs and check if valid
        while self.valid_proof(block_string) is False:
            # increment proof
            proof += 1

        # return proof
        return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # encode blockstring and proof to generate a guess
        guess = f"{block_string}{proof}".encode()

        # hash the guess
        guess_hash = hashlib.sha256(guess).hexdigest()

        # return True or False
        return guess_hash[:3] == "000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    # check that proof and id are present in the data
    print(data)
    if not data.get("id") or not data.get("proof"):
        # if not return a 400 with a message
        return jsonify({
            "message": "Request body must have id and proof"
        }), 400
    # find the string of the last block
    last_block_string = json.dumps(blockchain.last_block, sort_keys=True).encode()
    # verify if proof is valid
    is_valid = blockchain.valid_proof(last_block_string, data["proof"])

    # return a message indicating success or failure
    if is_valid:
        # create a new block and add it to the chain
        block = blockchain.new_block(data["proof"])

        return jsonify({
            "message": "New Block Forged.",
            'block': block
        }), 201
    else:
        return jsonify({
            "message": "Unable to forge block!"
        }), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # Return the chain and its current length
        'length': len(blockchain.chain), # length
        'chain': blockchain.chain # chain
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
