from flask import Flask
import time
import logging

app = Flask(__name__, template_folder='templates')
app.secret_key = "secret key"

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['GENERATED_FOLDER'] = 'static/generated/'
app.config['MODEL_FOLDER'] = 'static/models/'
app.config['LOG_FOLDER'] = 'log/'

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
app.config['ALLOWED_USERS'] = set(['pedro', 'aitor', 'sergio', 'victoria', 'demo'])

app.config['HOME_PAGE'] = 'http://localhost:5000/login'

fecha_hora = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(filename=app.config['LOG_FOLDER'] + f'web-flask-' + fecha_hora + '.log', level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def log_image(filename='.', text=''):
    if filename == '':
        filename = '.'
    with open(app.config['LOG_FOLDER'] + f'img-control-' + fecha_hora + '.log', 'a') as file_log:
        file_log.write(str(time.strftime("%Y-%m-%d %H:%M:%S")) + ' | ' + str(filename) + ' | ' + str(text) + '\n')
