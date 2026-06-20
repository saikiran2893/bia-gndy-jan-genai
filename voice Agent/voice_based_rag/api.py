import os
import uuid
from flask import Flask,request,jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from livekit.api import VideoGrants,AccessToken

load_dotenv()


app = Flask(__name__)


CORS(app, resources={r"/*": {"origins":"*"}})

def generate_room():
    return "room-" +str(uuid.uuid4())[:8]

@app.route("/getToken")
def get_token():
    """
    GET /getToken?name=sai&room=room-abc123
    """
    name = request.args.get("name","guest")
    room = request.args.get("room", generate_room())

    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]

    grants = VideoGrants(room_join=True, room=room)
    token = ( AccessToken(api_key,api_secret).with_identity(name).with_grants(grants))

    return jsonify({
        "token": token.to_jwt(),
        "room":room,
        "identity": name})


if __name__ == "__main__":
    app.run(host="0.0.0.0",port = 5001, debug = True)


    

    




