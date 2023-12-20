from io import BytesIO
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify

app = Flask(__name__)

model = keras.models.load_model("model.h5")
class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic']

@app.route('/', methods=['GET'])
def home():
    return "API is running!"

@app.route('/sendpicture', methods=['POST'])
def sendpicture():
    file = request.files.get('image')
    if file is None or file.filename == "":
        return jsonify({"error": "no file"})

    try:
        image = file.read()
        img = Image.open(BytesIO(image))

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
                "probability": float(output[0][prediction])
                }

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
