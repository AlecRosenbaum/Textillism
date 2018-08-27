import io

from flask import Flask, request, redirect, flash, send_file, render_template_string

from transform import transform

UPLOAD_FOLDER = "/path/to/the/uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            fout = transform(file_in=file, file_out=io.BytesIO())
            return send_file(fout, as_attachment=True, attachment_filename="output.png")

    return render_template_string(
        r"""
        <!doctype html>
        <head>
            <title>Convert An Image</title>
        </head>
        <body>
            <h1>Convert An Image to Text!</h1>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <ul class=flashes>
                    {% for message in messages %}
                        <li>{{ message }}</li>
                    {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}
            <p>Note that this may take a minute to process.</p>
            <form method=post enctype=multipart/form-data>
                <p>
                    <input type=file name=file>
                    <input type=submit value=Upload>
                </p>
            </form>
        </body>
        """
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
