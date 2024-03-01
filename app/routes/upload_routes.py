import os 
from flask import Flask, request,jsonify
from flask_restful import Api, Resource


class ImageUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'No file part in the request'}, 400

        file = request.files['file']

        if file.filename == '':
            return {'message': 'No selected file'}, 400

        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return {'message': 'File uploaded successfully'}, 200

api.add_resource(ImageUpload, '/upload')
