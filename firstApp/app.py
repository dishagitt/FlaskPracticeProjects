from flask import Flask,render_template,request
app = Flask(__name__)

@app.route('/')
def index():
   return render_template("calc.html")

@app.route('/calculate', methods=['POST'])
def calculate():
   try:
      val1 = float(request.form.get('num1'))
      val2 = float(request.form.get('num2'))
      operation = request.form.get('operation')
      
      if operation == 'add':
         result = val1 + val2
      elif operation == 'subtract':
         result = val1 - val2
      elif operation == 'multiply':
         result = val1 * val2
      elif operation == 'divide':
         result = val1 / val2
      else:
         result = "Invalid"
      
      return render_template("calc.html",result=result)
   
   except ValueError:
      print("Error: Invalid input. Please enter numbers.")
   

if __name__ == '__main__':
   app.run(debug=True)