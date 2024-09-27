from main import create_app
from flask_cors import CORS

app = create_app()
cors = CORS(app, resources={
    r"/crawler/*": {"origins": ["http://192.168.6.*:5000", "http://127.0.0.1:5000", "http://localhost:5000"]},
    r"/data/*": {"origins": ["http://192.168.6.*:5000", "http://127.0.0.1:5000", "http://localhost:5000"]}
})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)