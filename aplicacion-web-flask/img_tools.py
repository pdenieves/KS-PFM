import os
import numpy as np
from imutils import paths
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, array_to_img
from tensorflow.keras.models import load_model

from PIL import Image
import cv2 as cv2

from app import app


# Revisamos si se trata de una imagen a partir de la extensión del fichero
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Función que calcula el PSNR (Peak Signal to Noise Ratio). Usaremos el PSNR como métrica de nuestro modelo
def psnr(orig, pred):
    # cast the target images to integer
    orig = orig * 255.0
    orig = tf.cast(orig, tf.uint8)
    orig = tf.clip_by_value(orig, 0, 255)

    # cast the predicted images to integer
    pred = pred * 255.0
    pred = tf.cast(pred, tf.uint8)
    pred = tf.clip_by_value(pred, 0, 255)
    
    # return the psnr
    return tf.image.psnr(orig, pred, max_val=255)


# Función que obtiene el canal Y de la imagen
def get_y_channel(image):
    # convert the image to YCbCr colorspace and then split it to get the
    # individual channels
    ycbcr = image.convert("YCbCr")
    (y, cb, cr) = ycbcr.split()
    
    # convert the y-channel to a numpy array, cast it to float, and
    # scale its pixel range to [0, 1]
    y = np.array(y)
    y = y.astype("float32") / 255.0
    
    # return a tuple of the individual channels
    return (y, cb, cr)


# Función que aplica el reescalado de la imagen de [0,1] a [0,255] (canal Y)
def clip_numpy(image):
    # cast image to integer, clip its pixel range to [0, 255]
    image = tf.cast(image * 255.0, tf.uint8)
    image = tf.clip_by_value(image, 0, 255).numpy()
    
    # return the image
    return image


# Función que convierte la imagen YUV a RGB.
def rebuild_image(y, cb, cr):
    # do a bit of initial preprocessing, reshape it to match original size, and then convert it to a PIL Image
    y = clip_numpy(y).squeeze()
    y = y.reshape(y.shape[0], y.shape[1])
    y = Image.fromarray(y, mode="L")
    
    # resize the other channels of the image to match the original dimension
    outputCB= cb.resize(y.size, Image.LANCZOS)
    outputCR= cr.resize(y.size, Image.LANCZOS)
    
    # merge the resized channels altogether and return it as a numpy array
    final = Image.merge("YCbCr", (y, outputCB, outputCR)).convert("RGB")
    return np.array(final)


# Filtro para aumentar la nitidez de la imagen
def sharpen(img):
    sharpen_filter = np.array([
        [ 0, -1,  0],
        [-1,  7, -1],
        [ 0, -1,  0]
    ])
    sharpen_filter = sharpen_filter / sharpen_filter.sum()
    sharpen_img = cv2.filter2D(img, -1, sharpen_filter)
    
    return sharpen_img


# Genero la imagen a través del modelo previamente entrenado
def predict_image(model, image):
    # retrieve the individual channels of the current image and perform inference
    (y, cb, cr) = get_y_channel(image)
    upscaledY = model.predict(y[None, ...])[0]
    
    # rebuild image
    predicted_img = rebuild_image(upscaledY, cb, cr)
    
    return predicted_img

def transform_image( image, target_width, target_height ): 
    resized_image = image
    width, height = image.size
    new_width = width
    new_height = height
    
    if height < target_height:
        ratio = width / height
        new_height = target_height
        new_width = round( ratio * new_height )
    elif width < target_width:
        ratio = height / width
        new_width = target_width
        new_height = round( ratio * new_width )
    resized_image = resized_image.resize( (new_width,new_height), Image.ANTIALIAS)
    width, height = resized_image.size
    if width > height:
        ratio = width / height
        new_height = target_height
        new_width = round( ratio * new_height )
    else:
        ratio = height / width
        new_width = target_width
        new_height = round( ratio * new_width )
    resized_image = resized_image.resize( (new_width,new_height), Image.ANTIALIAS)
    
    left = (new_width - target_width)/2
    top = (new_height - target_height)/2
    right = (new_width + target_width)/2
    bottom = (new_height + target_height)/2
    cropped_image = resized_image.crop( (left, top, right, bottom) )
    
    return cropped_image


# #####################################
# Función que genera la imagen
# Invocado desde la web
# #####################################
def generate_image(filename):
    # Load model
    model = load_model(app.config['MODEL_FOLDER'], custom_objects={"psnr" : psnr})
    #model.summary()

    # Load image to be transformed
    img_original = Image.open(app.config['UPLOAD_FOLDER'] + filename)
    
    # Transform (scale and crop) image to 300x300
    img_transformed = transform_image( img_original, 100, 100 )

    # Generate the new image
    img_generated = predict_image(model, img_transformed)
    
    # Resaltar bordes para aumentar la nitidez
    img_improved = sharpen(img_generated)
    img_final = array_to_img(img_improved)

    # Save de new image
    filename_new = filename.rsplit('.', 1)[0] + '_transformed.' + filename.rsplit('.', 1)[1]
    img_final.save(app.config['GENERATED_FOLDER'] + filename_new)
    
    return filename_new
