import json
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/", methods=['GET'])
def main():

    return "hello"

@app.route("/api/whisper", methods=['GET'])
@cross_origin()
def whisper():

    file = open("transcription.txt", "r")
    content = file.readlines() if file.readable() != "" else "No transcription available"
    file.close()

    return jsonify(content)





# if __name__ == '__main__':
#    app.run(port=5000)

