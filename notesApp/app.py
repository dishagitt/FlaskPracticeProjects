from flask import Flask, render_template, request, redirect
app = Flask(__name__)

import sqlite3
try:
    # connecting to sqlite3 db
    conn = sqlite3.connect('notes.db')
    
    # creating cursor object to execute sql query
    cursor = conn.cursor()
    
    # creating table if not exists
    cursor.execute(""" CREATE TABLE IF NOT EXISTS mynotes(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL
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
    
    
    
    

@app.route('/')
def index():
    # fetching data to display
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("select * from mynotes ORDER BY id DESC")
    notes = cursor.fetchall()
    conn.close()
    return render_template("home.html", items=notes)

@app.route('/notesApp', methods=['POST', 'PUT'])
def notesApp():  
    msg = None  
    
    #fetch data from form
    if request.method == "POST":
        try:    
            title = request.form.get('title')
            content = request.form.get('content')
            
            # connect to db
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            
            # insert in db
            cursor.execute("INSERT INTO mynotes(title,content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()
            msg = "Note inserted successfully!"
            # Redirect after POST (avoid duplicate insert on refresh)
            return redirect('/')            
        
        except sqlite3.Error as e:
            msg = f"Error inserting note: {e}"
    

# DELETE functionality
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mynotes WHERE id=?", (id,))
        conn.commit()
        conn.close()

        return redirect('/')
    
    except sqlite3.Error as e:
        return f"Error deleting note: {e}"
            
            
    
if __name__ == "__main__":
    app.run(debug=True)
    
        