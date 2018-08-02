from flask import Flask, request, redirect, render_template, session, flash
import datetime
import re
import md5
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'thewallisfun'
mysql = MySQLConnector(app,'thewall')

# Home
@app.route('/')
def index():
    return render_template('index.html')

# The Wall

@app.route('/wall')
def wall():
    query = "SELECT users.id, users.first_name, users.last_name, message, messages.created_at FROM messages JOIN users ON users.id = messages.users_id ORDER BY messages.created_at DESC;"
    query_com ="SELECT users.id, users.first_name, users.last_name, comments.comment, comments.messages_id, comments.created_at FROM comments JOIN users ON users.id = comments.users_id ORDER BY comments.created_at ASC;"
    messages = mysql.query_db(query)
    comments = mysql.query_db(query_com)

    return render_template('wall.html', all_msg=messages, all_comments=comments)

# Registration

@app.route('/registration', methods=['POST'])
def registration():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['regemail']
    hashed_password = md5.new(request.form['regpassword']).hexdigest()
    password2 = request.form['regpassword2']
    session['firstName'] = firstName

    # Write query as a string.
    # we want to insert into our Db.
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:firstName, :lastName, :regemail, :hashed_password, NOW(), NOW());"
    # query data for email validation
    query_val = "SELECT email FROM users WHERE email = :regemail;"

    query_id = "SELECT id FROM users WHERE email = :regemail;"
 
   #create a dictionary of data from the POST data received.
    data = {
            'firstName': request.form['firstName'],
            'lastName':  request.form['lastName'],
            'regemail': request.form['regemail'],
            'hashed_password': hashed_password
           }
    check = mysql.query_db(query_val, data)
    
    data_id = {
            'regemail': request.form['regemail'],
            }
    # Check name fields
    if len(firstName) < 2 or len(lastName) < 2:
        flash("Name must be longer.")
        return redirect('/')
    elif not str(firstName).isalpha():
        flash("First Name can only be letters.")
        return redirect('/')       
    elif not str(lastName).isalpha():
        flash("Last Name can only be letters.")
        return redirect('/')
    
    # Validates email address for proper format.
    if len(email) < 1:
        flash("Email cannot be blank!")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!")
        return redirect('/')
    elif len(check) != 0:
        flash("Duplicate address, enter another one!")
        return redirect('/')
    
    # Check password length and confirmation
    if len(request.form['regpassword']) < 8:
        flash("Password is not long enough!")
        return redirect('/')
    elif request.form['regpassword'] != password2:
        flash("Passwords do not match!")
        return redirect('/')

    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    session['from'] = 0
    get_id = mysql.query_db(query_id, data_id)
    session['logged_id'] = get_id[0]['id']
    return redirect('/wall')

# login

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT email FROM users WHERE email = :logemail;"
    query_pw = "SELECT password FROM users WHERE email = :logemail;"
    query_id = "SELECT id, first_name FROM users WHERE email = :logemail;"
    hashed_password = md5.new(request.form['logpassword']).hexdigest()
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'logemail': request.form['logemail'],
             'logpassword': request.form['logpassword']
           }
    data_id = {
            'logemail': request.form['logemail'],
            }   
    # query for email validation
    check = mysql.query_db(query, data)
    # query for password validation
    check_pw = mysql.query_db(query_pw, data)

    # Validates email address for proper format.
    if len(request.form['logemail']) < 1:
        flash("Email cannot be blank!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['logemail']):
        flash("Invalid Email Address!")
        return redirect('/')
    elif len(check) == 0:
        flash("Email not found!")
        return redirect('/')

    #password validation
    if hashed_password != check_pw[0]['password']:
        flash("Password does not match.")
        return redirect('/')

    session['from'] = 1
    get_id = mysql.query_db(query_id, data_id)
    session['logged_id'] = get_id[0]['id']
    session['firstName'] = get_id[0]['first_name']
    return redirect('/wall')

#This is the home page logout button, where the user will logout.
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    flash("You have been logged out... ")
    return redirect('/')

# Post Message

@app.route('/post_msg', methods=['POST'])
def post_msg():
    message = request.form['message']
    print message
    userid = session['logged_id']
    print userid

    # Write query as a string.
    # we want to insert into our Db.
    query = "INSERT INTO messages (message, created_at, updated_at, users_id) VALUES (:message, NOW(), NOW(), :userid);"
 
   # We'll then create a dictionary of data from the POST data received.
    data = {
            'message': request.form['message'],
            'userid':  session['logged_id']
           }
    print data
    mysql.query_db(query, data)
    return redirect('/wall')

# Post Comments

@app.route('/post_cmt', methods=['POST'])
def post_cmt():
    query = "INSERT INTO comments (comment, created_at, updated_at, messages_id, users_id) VALUES (:comment, NOW(), NOW(), :message_id, :userid);"    
    comment = request.form['comment']
    userid = session['logged_id'] 
    message_id = request.form['message_id']
    # Write query as a string.
    # we want to insert into our Db.
    # We'll then create a dictionary of data from the POST data received.
    data = {
            'comment': request.form['comment'],
            'message_id':  request.form['message_id'],
            'userid':  session['logged_id'],
           }

    mysql.query_db(query, data)
    return redirect('/wall')
#delete unfinished
# @app.route('/wall/message/delete/<id>')
# def delete_comment(id):
#     del_comments_query = "DELETE FROM comments WHERE message_id = :id"
#     data = {
#         'id': id
#     }
#     mysql.query_db(del_comments_query, data)
#     del_message_query = "DELETE FROM messages WHERE id = :id"
#     mysql.query_db(del_message_query, data)
#     return redirect('/thewall')


app.run(debug=True)