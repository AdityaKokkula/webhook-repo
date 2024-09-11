from flask import Flask, request, jsonify
import pymongo
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["webhook_data"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    # Process push events
    if 'pusher' in data:
        event_type = "Push"
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        timestamp = datetime.now().isoformat()
        event_data = {
            "author": author,
            "action": event_type,
            "to_branch": branch,
            "timestamp": timestamp
        }
    # Process pull request events
    elif 'pull_request' in data:
        event_type = "Pull Request"
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.now().isoformat()
        event_data = {
            "author": author,
            "action": event_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    else:
        return jsonify({"message": "Event type not supported"}), 400

    # Insert event data into MongoDB
    collection.insert_one(event_data)
    return jsonify({"message": "Webhook received!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
