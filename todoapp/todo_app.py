from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sam:sampostgres@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable = False, default = False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

@app.route('/todos/create', methods=['POST'])
def create_todo():
    # fetches the json body that was sent to it, which in case here is a dictionary with key description
    description = request.get_json()['description']
    todo = Todo(description = description)
    db.session.add(todo)
    db.session.commit()
    # returns a useful JSON object including that description
    return jsonify({
        'description':todo.description
    })

@app.route('/')
def index():
    # specifies an HTML file to render to the user whenever a user visits this route
    # and tells the model to do select all the available data in the database
    return render_template('index.html', data= Todo.query.all()
    ) # matches the name of our route handler