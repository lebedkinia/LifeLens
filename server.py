from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)
print("server start")
UPLOAD_FOLDER = r'C:\Users\lebed\PycharmProjects\AI glasses\photos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('image')

    if not file:
        if request.data:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'image_{timestamp}.jpg'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            print(filepath)

            with open(filepath, 'wb') as f:
                f.write(request.data)
            return jsonify({'status': 'success', 'message': 'File uploaded', 'filename': filename}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No file found'}), 400

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'image_{timestamp}.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'status': 'success', 'message': 'File uploaded', 'filename': filename}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threading=True)
