# app/resources/utils_resources.py

from flask_restful import Resource
from flask import jsonify
from app.utils import delete_expired_entries

class ExpiredEntriesResource(Resource):
    def delete(self):
        # Call the function to delete expired entries
        delete_expired_entries()

        # Return a JSON response indicating success
        return {'message': 'Expired entries deleted successfully'}, 200
