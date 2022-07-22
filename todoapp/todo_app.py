from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sam:sampostgres@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), nullable = False)
    todos = db.relationship('Todo', backref = 'list', lazy = True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable = False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        if name.strip() == '':
            raise Exception("You Have to Name the List")
        newlist = TodoList(name = name)
        db.session.add(newlist)
        db.session.commit()
        body['name'] = newlist.name 
    except: 
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        # fetches the json body that was sent to it, which in case here is a dictionary with key description
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        if description.strip() == '':
            raise Exception("The input description value is NULL!!")
        todo = Todo(description = description, list_id = list_id)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description 
    except: 
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        # returns a useful JSON object including that description
        return jsonify(body)

@app.route('/lists/<listId>/set-completed', methods=['POST'])
def set_list_completed(listId):
    try:
        completed = request.get_json()['completed']
        selected_list = TodoList.query.get(listId)
        todos = selected_list.todos
        for i in range(len(todos)):
            todos[i].completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todoId>/set-completed', methods=['POST'])
def set_completed(todoId):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todoId)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todoId>/delete', methods=['DELETE'])
def delete_todo(todoId):
    try:
        todo=Todo.query.get(todoId)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/lists/<listId>/delete', methods=['DELETE'])
def delete_list(listId):
    try:
        list=TodoList.query.get(listId)
        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    todos= Todo.query.filter_by(list_id = list_id).order_by('id')
    # for todo in todos:
    #     if todo.completed == False:
    #         all_completed = False
    #         break
    #     else:
    #         all_completed = True
    # specifies an HTML file to render to the user whenever a user visits this route
    # and tells the model to do select all the available data in the database
    return render_template('index.html', 
    lists = TodoList.query.all(),
    active_list = TodoList.query.get(list_id),
    todos = todos
    #all_completed = all_completed
    )

# homepage route
@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))