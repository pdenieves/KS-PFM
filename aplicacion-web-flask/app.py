from flask import Flask

app = Flask(__name__, template_folder='templates')
app.secret_key = "secret key"

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['GENERATED_FOLDER'] = 'static/generated/'
app.config['MODEL_FOLDER'] = 'static/models/'

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['HOME_PAGE'] = 'http://localhost:5000/uploadfile'
