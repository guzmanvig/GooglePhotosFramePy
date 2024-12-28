from flask import Flask, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store the state
server_state = {
    'toggle_black_screen_requested': False,
    'skip_to_next_requested': False,
    'current_photo': None,
    'photo_urls': {}  # Map to store photo name -> URL
}

@app.route('/black-screen', methods=['PUT'])
def toggle_black_screen():
    server_state['toggle_black_screen_requested'] = True
    return jsonify({'message': 'Black screen toggle requested'}), 200

@app.route('/next-photo', methods=['PUT'])
def skip_to_next():
    server_state['skip_to_next_requested'] = True
    return jsonify({'message': 'Skip to next photo requested'}), 200

@app.route('/current-photo-url', methods=['GET'])
def get_current_photo_url():
    current_photo = server_state['current_photo']
    if current_photo and current_photo in server_state['photo_urls']:
        return jsonify({
            'photo_name': current_photo,
            'url': server_state['photo_urls'][current_photo]
        }), 200
    return jsonify({'error': 'No photo URL available'}), 404

def run_server():
    app.run(host='0.0.0.0', port=5000)

def start_server():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_state 