from flask import Flask, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Flask instance
app = Flask(__name__)

# Define the root endpoint
@app.route('/')
def hello():
    logging.info("Root endpoint accessed.")
    return jsonify({"message": "Bot is running! by Mz"})

# Define the health check endpoint
@app.route('/health')
def health_check():
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
