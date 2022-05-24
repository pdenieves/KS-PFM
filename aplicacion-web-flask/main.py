import os
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, send_file, render_template
import webbrowser

from app import app
from img_tools import allowed_file, allowed_size, generate_image


# Login
@app.route("/login/", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        user = request.form['username']
        if user and request.form['password'] == user and user in app.config['ALLOWED_USERS']:
            app.logger.warning('Login realizado')
            return redirect('/uploadfile')
        else:
            error = 'User/password not valid!'
    return render_template('login.html', error=error)


# Upload API
@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            app.logger.info('No se ha encontrado el fichero')
            return redirect(request.url)
            
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        
        if file.filename == '':
            app.logger.info(f'Nombre de fichero no válido')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if not allowed_size(os.path.join(app.config['UPLOAD_FOLDER'], file.filename)):
                error = 'El tamaño de la imagen no es válido.'
                app.logger.info(file.filename + ' : ' + error)
                return render_template('upload_file.html', error=error)

            app.logger.info(filename + ' : Imagen cargada')
            filename_new = generate_image(filename)
            return redirect('/downloadfile/'+ filename + '/' + filename_new)
            
        else:
            error = 'Extensión del fichero no válida. Los tipos permitidos son: png, jpg, jpeg'
            app.logger.info(file.filename + ' : ' + error)
            return render_template('upload_file.html', error=error)

    if request.method == 'GET':
        return render_template('upload_file.html')


# Display images
@app.route('/display/<filename>')
@app.route('/display/<filename>/<folder>')
def display_image(filename, folder=''):
	if folder == '':
		folderpath = 'updates/'
	else:
		folderpath = folder + '/'
	return redirect(url_for('static', filename=folderpath + filename), code=301)


# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
@app.route("/downloadfile/<filename>/<filename_new>", methods = ['GET'])
def download_file(filename, filename_new=''):
    app.logger.info(filename_new + ' : Descargando imagen')
    return render_template('download_file.html', filename=filename, filename_new=filename_new)


@app.route('/return-files/<filename>')
def return_files(filename):
    file_path = app.config['GENERATED_FOLDER'] + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    app.logger.warning('Levantando la web')

    webbrowser.open_new(app.config['HOME_PAGE'])
    app.run(debug=True, use_reloader=False)

    app.logger.warning('Web no disponible')

