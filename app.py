from main import app, db
from flask_cors import CORS

cors = CORS(app, resources={
    r"/crawler/*": {"origins": ["http://192.168.6.*:5000", "http://127.0.0.1:5000", "http://localhost:5000"]},
    r"/data/*": {"origins": ["http://192.168.6.*:5000", "http://127.0.0.1:5000", "http://localhost:5000"]}
})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=4000, debug=True)