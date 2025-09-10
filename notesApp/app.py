from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, random


app = Flask(__name__)
app.secret_key = 'supersecretkey'    # secret key used to sign session cookies

# ====== Flask-Mail Configuration ======
app.config['MAIL_SERVER'] = 'smtp.gmail.com'          # SMTP server address
app.config['MAIL_PORT'] = 587                         # Port for TLS
app.config['MAIL_USE_TLS'] = True                     # Enable TLS encryption
app.config['MAIL_USE_SSL'] = False                    # Disable SSL (can't use both)
app.config['MAIL_USERNAME'] = "s123onuu@gmail.com"    # sender email
app.config['MAIL_PASSWORD'] = "kobaejjltgxbiyea"      # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = "s123onuu@gmail.com"

mail = Mail(app)  # Initialize Flask-Mail with app

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
    return render_template("login.html")

@app.route('/signup/')
def signupPage():
    return render_template("signup.html")

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
    return render_template("home.html", items=notes ,fname=session.get("fname"))


# ---------------- SIGNUP WITH OTP ---------------- #
@app.route('/send_otp', methods=["GET", "POST"])
def send_otp():
    fname = request.form.get("fname")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for("signupPage"))

    # Save user info temporarily in session
    session['fname'] = fname
    session['email'] = email
    session['password'] = generate_password_hash(password)  # Hash password

    otp = random.randint(100000, 999999)
    session['otp'] = str(otp)  # Store as string for comparison

    try:
        msg = Message(subject='Your OTP Code',
                      recipients=[email])
        msg.body = f'Your OTP code is: {otp}'
        mail.send(msg)
        flash("OTP sent successfully! Check your email.", "info")
        return render_template("verifyOTP.html", reset = False)
  # FIX: Redirect to OTP entry page
    except Exception as e:
        flash(f"Error sending OTP: {str(e)}", "error")
        return redirect(url_for("signupPage"))



# verify otp
@app.route('/verify_otp', methods=["POST"])
def verify_otp():
    entered_otp = request.form.get("otp")

    if entered_otp == session.get('otp'):
        # Insert user into database
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (fname, email, password)
            VALUES (?, ?, ?)
        ''', (session['fname'], session['email'], session['password']))
        conn.commit()
        conn.close()

        flash("Account created successfully! You can now log in.", "success")
        session.clear()
        return redirect(url_for("login"))
    else:
        flash("Invalid OTP! Please try again.", "error")
        return render_template("verifyOTP.html")  # FIX: Stay on OTP page if failed


# ---------------- LOGIN ---------------- #
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[3], password):
                session['userId'] = user[0]
                session['fname'] = user[1]
                session['email'] = user[2]
                return redirect(url_for('home'))
            else:
                flash("Incorrect email or password!", "error")
        except sqlite3.Error as e:
            flash(f"Database error: {e}", "error")

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('startPage'))


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


# reset page (get user email to send otp)
@app.route("/reset", methods=["GET"])
def resetPage():
    return render_template("reset.html")

# ---------------- RESET PASSWORD WITH OTP ---------------- #
@app.route('/send_reset_otp', methods=["POST"])
def send_reset_otp():
    email = request.form.get("email")

    # Check if email exists in DB
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("Email not registered!", "error")
        return redirect(url_for("resetPage"))

    session['reset_email'] = email

    otp = random.randint(100000, 999999)
    session['otp'] = str(otp)

    try:
        msg = Message(subject='Password Reset OTP',
                      recipients=[email])
        msg.body = f'Your OTP code is: {otp}'
        mail.send(msg)
        flash("Reset OTP sent! Check your email.", "info")

        # 👉 Load OTP page for reset
        return render_template("verifyOTP.html", reset=True)

    except Exception as e:
        flash(f"Error sending OTP: {str(e)}", "error")
        return redirect(url_for("resetPage"))


@app.route('/verify_reset_otp', methods=["POST"])
def verify_reset_otp():
    entered_otp = request.form.get("otp")

    if entered_otp == session.get('otp'):
        flash("OTP verified! Please reset your password.", "success")
        return redirect(url_for("new_password_page"))  # a form to set new password
    else:
        flash("Invalid OTP! Please try again.", "error")
        return render_template("verifyOTP.html", reset=True)


# reset new password page
@app.route('/new_password', methods=["GET"])
def new_password_page():
    return render_template("resetPassword.html")


 # reset new password in db
@app.route('/update_password', methods=["POST"])
def reset_password():
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for("new_password_page"))

    email = session.get('reset_email')
    if not email:
        flash("Session expired. Please try again.", "error")
        return redirect(url_for("login"))

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
    conn.commit()
    conn.close()

    flash("Password updated successfully! You can now log in.", "success")
    session.clear()
   
    return redirect(url_for("login"))



# change password page
@app.route('/change_password', methods = ['POST'])
def change_password():
    userId = session["userId"]

    if 'userId' not in session:
        flash("You must be logged in.", "error")
        return redirect(url_for('login'))

    current = request.form.get('current_password')
    newpass = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not current or not newpass or not confirm:
        flash("All fields are required.", "error")
        return redirect(url_for('home'))

    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE id = ?", (userId,))
    row = cursor.fetchone()

    if not row:
        flash("User not found.", "error")
        return redirect(url_for('home'))

    storedpass = row[0]
    if not check_password_hash(storedpass, current):
        flash("Incorrect Current Password", "error")
        return redirect(url_for('home'))
    
    if newpass != confirm:
        flash("Confirm password do not match", "error")
        return redirect(url_for('home'))

    new_hashed_password = generate_password_hash(newpass)
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed_password, userId))
    conn.commit()
    conn.close()
    flash("Chnaged password successfully!", "info")
    return redirect(url_for('home'))



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    
        