from main import app
from flask_cors import CORS

cors = CORS(app, resources={
    r"/crawler/*": {"origins": "*"},
    r"/data/*": {"origins": "*"}
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)