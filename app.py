from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User
import bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'dingiswayo_calendar_schedular'  
api = Api(app)
jwt = JWTManager(app)