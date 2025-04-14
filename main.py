try:
    from app import app
except FileNotFoundError as e:
    # Create a simple Flask app to show the error
    from flask import Flask, render_template
    import os
    
    app = Flask(__name__)
    
    # Create the models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    @app.route('/')
    def error_page():
        return """
        <h1>Medical Diagnosis System</h1>
        <p>The application could not start because the ML model is missing.</p>
        <p>Please make sure to upload the SVC model file to the models/svc.pkl path.</p>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)