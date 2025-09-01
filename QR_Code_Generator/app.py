from flask import Flask, render_template
from forms import QRCodeForm
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)

@app.route('/')
def home():
   form = QRCodeForm()
   return render_template('index.html', form=form)


if __name__ == '__main__':
   app.run(debug = True)