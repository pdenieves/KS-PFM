import os
from werkzeug.utils import secure_filename
from flask import Flask, flash,request, redirect, url_for, send_file, render_template
import webbrowser

from app import app
from img_tools import allowed_file, generate_image

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
            filename_new = generate_image(filename)
            return redirect('/downloadfile/'+ filename + '/' + filename_new)
            
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)

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
	print('***' + folder)
	return redirect(url_for('static', filename=folderpath + filename), code=301)


# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
@app.route("/downloadfile/<filename>/<filename_new>", methods = ['GET'])
def download_file(filename, filename_new=''):
    return render_template('download_file.html', filename=filename, filename_new=filename_new)


@app.route('/return-files/<filename>')
def return_files(filename):
    file_path = app.config['GENERATED_FOLDER'] + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    webbrowser.open_new(app.config['HOME_PAGE'])
    app.run(debug=True, use_reloader=False)
    #app.run()
