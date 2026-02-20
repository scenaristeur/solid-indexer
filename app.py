from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from chat_loop import run_chat_loop

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')
    logger.info(f"Received input: {user_input}")

    if not user_input:
        logger.error("No input provided")
        return jsonify({'response': 'No input provided'}), 400

    # Call the run_chat_loop function to get the response
    response = run_chat_loop(user_input)
    logger.info(f"Response: {response}")
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)