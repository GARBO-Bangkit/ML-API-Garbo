import io
import numpy as np

from database import *
from functions import *

from tensorflow import keras
from PIL import Image
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from datetime import timedelta
from google.cloud import storage
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

# config JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

#inlitialize google cloud storage bucket
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key/garbage-classification-408613-0f1ae06ae751.json"

client = storage.Client()
bucket_name = os.getenv('BUCKET_NAME')

#inlitialize model
model = keras.models.load_model("model.h5")
class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic']

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not all(key in data for key in ['username', 'password', 'name', 'email']):
        return jsonify({'message': 'Missing data'}), 400

    if user_exists(data['username']) | user_exists(data['email']):
        return jsonify({'message': 'Username or Email already exists'}), 409

    add_user(data)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({'message': 'Missing data'}), 400

    if login_user(data):
        access_token = create_access_token(identity=data['username'])
        profile = get_point(data['username'])
        profile['access_token'] = access_token
        return jsonify(profile), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/sendpicture', methods=['POST'])
@jwt_required()
def sendpicture():
    current_user = get_jwt_identity()
    file = request.files.get('image')

    if file is None or file.filename == "":
        return jsonify({"error": "no file"})

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"})

    try:
        filename = secure_filename(file.filename)
        object_name = f"{current_user}/{filename}"

        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        in_memory_file.seek(0)

        # Access the bucket
        bucket = client.bucket(bucket_name)

        # Get the blob
        blob = bucket.blob(object_name)

        blob.upload_from_file(in_memory_file, content_type=file.content_type)

        # Process the image as needed
        in_memory_file.seek(0)  # Reset file pointer
        img = Image.open(in_memory_file)
        input_shape = (256, 256)
        img = img.resize(input_shape)
        img_array = np.array(img) / 255.0
        input_data = np.expand_dims(img_array, axis=0)

        output = model.predict(input_data)
        prediction = np.argmax(output[0])

        print(output)
        print(prediction)
        print("Predicted: ", class_names[prediction])
        print("Probability: ", output[0][prediction])

        data = {
            "prediction": class_names[prediction],
            "accuracy": float(output[0][prediction]),
            "image_url": blob.public_url
        }

        add_history(current_user, blob.public_url, class_names[prediction])

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/result', methods=['GET'])
@jwt_required()
def gethistory():
    try:
        current_user = get_jwt_identity()
        history_list = get_history_user(current_user)
        return jsonify(history_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/point', methods=['GET'])
@jwt_required()
def getpoint():
    try:
        current_user = get_jwt_identity()
        point = get_point(current_user)
        return jsonify(point)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/result/<jenis_sampah>', methods=['GET'])
@jwt_required()
def get_filtered_history(jenis_sampah):
    try:
        current_user = get_jwt_identity()
        history_list = get_history_user_and_jenis_sampah(current_user, jenis_sampah)
        return jsonify(history_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
