import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import PIL

from app import app


# Check if the file is an image
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Generate the new image as a prediction
def predict_image(model, image):
    ycbcr = image.convert("YCbCr")
    y, cb, cr = ycbcr.split()
    y = img_to_array(y)
    y = y.astype("float32") / 255.0

    input = np.expand_dims(y, axis=0)
    out = model.predict(input)

    out_img_y = out[0]
    out_img_y *= 255.0

    # Restore the image in RGB color space.
    out_img_y = out_img_y.clip(0, 255)
    out_img_y = out_img_y.reshape((np.shape(out_img_y)[0], np.shape(out_img_y)[1]))
    out_img_y = PIL.Image.fromarray(np.uint8(out_img_y), mode="L")
    out_img_cb = cb.resize(out_img_y.size, PIL.Image.Resampling.BICUBIC)
    out_img_cr = cr.resize(out_img_y.size, PIL.Image.Resampling.BICUBIC)
    out_img = PIL.Image.merge("YCbCr", (out_img_y, out_img_cb, out_img_cr)).convert('RGB')
    return out_img


def generate_image(filename):
    # Load model
    model = load_model(app.config['MODEL_FOLDER'] + 'model_keras.h5')
    #model.summary()

    # Load image to be transformed
    img_original = load_img(app.config['UPLOAD_FOLDER'] + filename)

    # Generate the new image
    img_transformed = predict_image(model, img_original)

    # Save de new image
    filename_new = filename.rsplit('.', 1)[0] + '_transformed.' + filename.rsplit('.', 1)[1]
    img_transformed.save(app.config['GENERATED_FOLDER'] + filename_new)
    
    return filename_new
