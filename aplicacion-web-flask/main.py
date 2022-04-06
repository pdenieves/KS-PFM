import os
from werkzeug.utils import secure_filename
from flask import Flask, flash,request, redirect, url_for, send_file, render_template
from app import app

import shutil
import webbrowser


# Check if the file is an image
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Image processing (test function)
def copy_file(original, target):
	shutil.copyfile(original, target)


# Upload API
@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
            
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            filename_new = 'copy_' + filename
            copy_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], filename_new))
            return redirect('/downloadfile/'+ filename + '/' + filename_new)
            
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

    return render_template('upload_file.html')


# Display images
@app.route('/display/<filename>')
def display_image(filename):
	print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)


# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
@app.route("/downloadfile/<filename>/<filename_new>", methods = ['GET'])
def download_file(filename, filename_new=''):
    return render_template('download_file.html', filename=filename, filename_new=filename_new)


@app.route('/return-files/<filename>')
def return_files(filename):
    file_path = app.config['UPLOAD_FOLDER'] + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    webbrowser.open_new(app.config['HOME_PAGE'])
    app.run(debug=True)