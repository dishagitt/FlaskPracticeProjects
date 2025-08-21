from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
import sqlite3


app = Flask(__name__)
app.secret_key = 'supersecretkey'    # secret key used to sign session cookies
bcrypt = Bcrypt(app)


def init_db():
    try:
        # connecting to sqlite3 db
        conn = sqlite3.connect('notes.db')
    
        # creating cursor object to execute sql query
        cursor = conn.cursor()
        
        # creating table if not exists
        # user table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            );
        """)
        
        # notes table
        cursor.execute(""" CREATE TABLE IF NOT EXISTS mynotes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL, 
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(userId) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        
        # make changes permanent
        conn.commit()
        # print("table 'products' created successfully")
    
    except sqlite3.Error as e:
        print(f"error creating table: {e}")
    
    finally:
        if conn:
            # closing connection when finished
            conn.close()
  
    
    
# startPage -> render login page
@app.route('/')
def startPage():
    return render_template("loginAndSignup.html")

# home page with add notes form and notes display functionslity
@app.route('/home')
def home():
    # fetching data to display
    if "userId" not in session:
        return redirect(url_for("startPage"))
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("select id, title, content from mynotes where userId = ? ORDER BY id DESC", (session["userId"],))
    notes = cursor.fetchall()
    conn.close()
    return render_template("home.html", items=notes)


# ADD notes
@app.route('/notesApp', methods=['POST'])
def notesApp():  
    msg = None  
    
    #fetch data from form
    if request.method == "POST":
        if "userId" not in session:
            return redirect(url_for("startPage"))
        try:    
            title = request.form.get('title')
            content = request.form.get('content')
            userId = session["userId"]
            
            # connect to db
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            
            # insert in db
            cursor.execute("INSERT INTO mynotes(userId, title,content) VALUES (?, ?, ?)", (userId, title, content))
            conn.commit()
            conn.close()
            msg = "Note inserted successfully!"
            # Redirect after POST (avoid duplicate insert on refresh)
            return redirect(url_for("home"))
        
        except sqlite3.Error as e:
            msg = f"Error inserting note: {e}"
    
    

# DELETE note
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mynotes WHERE id=?", (id,))
        conn.commit()
        conn.close()

        return redirect(url_for('home', id=session["userId"]))
    
    except sqlite3.Error as e:
        return f"Error deleting note: {e}"
            
     
     
# EDIT note page open
@app.route('/edit/<int:id>', methods=['GET','POST'])
def editPage(id):
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("select * from mynotes where id=?", (id,))
        notes = cursor.fetchall()
        conn.close()
        return render_template("editNotes.html", items=notes)
    except sqlite3.Error as e:
        return f"Error in opening edit page: {e}"

    
# save note after editing
@app.route('/update/<int:id>', methods=["POST"])
def updateNote(id):
    if "userId" not in session:
        return redirect(url_for("startPage"))

    try:
        editedTitle = request.form.get('title')
        editedContent = request.form.get('content')
        
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE mynotes SET title=?, content=? WHERE id=? AND userId=?",
            (editedTitle, editedContent, id, session["userId"])
        )
        conn.commit()
        conn.close()

        return redirect(url_for('home', id=session['userId']))
        
    except sqlite3.Error as e:
        return f"Error editing note: {e}"

    

# Close edit page 
@app.route('/closeEdit/', methods=["GET"])
def closeEdit():
    if "userId" not in session:
        return redirect(url_for("startPage"))  # or your login page
    return redirect(url_for("home", id=session["userId"]))


    

# sign up (register user)
@app.route('/signUp/', methods=["GET", "POST"])
def registerUser():
    try:
        if request.method == 'POST':
            fname = request.form.get('fname')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # hashing the password before storing in db 
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(fname, email, password) VALUES(?, ?, ?)",(fname, email, hashed_password))
            conn.commit()
            return redirect(url_for('login'))            
            
    
    except sqlite3.Error as e:
        return f"Database error: {e}"
    
    finally:
        if conn:
            conn.close()
    
    return render_template("loginAndSignup.html")

     

# login user
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * from users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            
            if user is None:
                return "incorrect email or password"
            
            # verify password
            if user and bcrypt.check_password_hash(user[3], password):
                session['userId'] = user[0]
                session['fname'] = user[1]
                return redirect(url_for('home', id=session['userId']))
            else:
                return "incorrect email or password"
                
        except sqlite3.Error as e:
            return f"database error: {e}"
    
    return render_template("loginAndSignup.html") 


# logout user
@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()
    # Redirect to the login page (startPage)
    return redirect(url_for('startPage'))

    
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    
        