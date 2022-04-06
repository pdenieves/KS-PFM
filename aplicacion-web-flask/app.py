from flask import Flask

app = Flask(__name__, template_folder='templates')
app.secret_key = "secret key"

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

HOME_PAGE = 'http://localhost:5000/uploadfile'
app.config['HOME_PAGE'] = HOME_PAGE
