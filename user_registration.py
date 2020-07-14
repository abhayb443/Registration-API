from Registration_API.models import Base, User
from flask import Flask, jsonify, request, url_for, abort
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

engine = create_engine('sqlite:///users.db', connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/api/user', methods=['POST'])
def new_user():
    # URL query parameters
    username = request.args.get('username')
    password = request.args.get('password')

    # posted form input
    # username = request.form.get('username')
    # password = request.form.get('password')

    # posted as raw - type as json
    # username = request.json.get('username')
    # password = request.json.get('password')

    if username is None or password is None:
        abort(400)      # Missing Argument
    if session.query(User).filter_by(username = username).first() is not None:
        abort(400)      # Existing User
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username' : user.username}), 201, {'Location': url_for('get_user', id = user.id, _external=True)}


@app.route('/api/users', methods = ['GET'])
def all_users():
    if request.method == 'GET':
        # Return all restaurants from the db
        Users = session.query(User).all()
        return jsonify(User = [i.serialize for i in Users])


@app.route('/api/users/<int:id>', methods = ['GET', 'PUT', 'DELETE'])
def get_user(id):
    user = session.query(User).filter_by(id=id).one_or_none()
    if request.method == 'GET':
        if not user:
            abort(400)
        return jsonify({'username': user.username})

    elif request.method == 'DELETE':
        # Delete a specific Restaurant
        session.delete(user)
        session.commit()
        return "User Deleted"

    elif request.method == 'PUT':
        # Update a specific restaurant
        username = request.args.get('username')

        if username:
            user.username = username
        session.commit()
        return "User record updated"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
