from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from gemini import generate_rizz, update_description
from google import genai

app = Flask(__name__)
CORS(app)
# Function that recieves data from the front end
@app.route('/rizzify', methods=['POST'])
def rizzify():
    data = request.get_json()

    relationship = data.get('relationship')
    if relationship is None:
        relationship = "acquaintance"
    print(f"Relationship: {relationship}")
    
    current_message = data.get('current_message')
    if current_message is None:
        current_message = ""
    print("Cur msg: " + current_message)

    chat_history_json = data.get('chat_history')[-10:]
    if chat_history_json is None:
        chat_history_json = []

    chat_history = []
    for msg in chat_history_json:
        if msg.get('imageSrc') is not None and msg.get('imageSrc') != '':
            chat_history.append({"type": "image", "sender": msg.get('username'), "content": msg.get('imageSrc')})
        elif msg.get('message') is not None and msg.get('message') != '':
            chat_history.append({"type": "text", "sender": msg.get('username'), "content": msg.get('message')})

    print(chat_history)

    other_user = data.get('other_username')
    for message in chat_history:
        if message['sender'] != other_user:
            my_user = message['sender']

    print("Me: " + my_user)
    print("Other: " + other_user)

    update_description(chat_history, my_user, other_user)
    
    return_msg = generate_rizz(relationship, chat_history, my_user, current_message)
    print("return: " + return_msg)
    if return_msg is None:
        return jsonify({"status": "error", "msg": "Failed to generate a message."})
    else:
        return jsonify({"status": "success", "msg": return_msg})

if __name__ == '__main__':
    app.run(port=8000, host="0.0.0.0", debug=True)
