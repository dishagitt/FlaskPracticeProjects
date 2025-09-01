from flask import Flask, render_template, request, redirect, url_for
from forms import QRCodeForm
import secrets
import qrcode, os, uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)

@app.route('/')
def home():
    form = QRCodeForm()
    return render_template('index.html', form=form)


@app.route('/generateQR', methods=['POST'])
def generateQR():
    try:
        # Get form input
        data = request.form.get("inputText")
        if not data:
            return render_template("index.html", form=QRCodeForm(), msg="Please enter some text or a URL")

        # Create a new QR code object each time
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = f"qr_{unique_id}.png"
        filepath = os.path.join("static", filename)

        # Save QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)

        # Show display page with QR
        return render_template(
            "displayQR.html",
            qr_url=url_for("static", filename=filename),
            filename=filename
        )

    except Exception as e:
        msg = f"An error occurred: {e}"
        print(msg)
        return render_template("index.html", form=QRCodeForm(), msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
