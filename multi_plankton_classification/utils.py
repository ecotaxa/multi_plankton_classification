import tensorflow_hub as hub
import tensorflow as tf
from scipy.special import softmax
import os

from PIL import Image
import numpy as np
from skimage import transform

def load_model(model_name):
    with open(os.path.join(model_path, model_name, file_name)) as f:
    sumlines = f.readlines()

    nameslines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('name'))]
    name_classes = nameslines[0].split(": ")[-1]
    classes=name_classes.split(",")
    num_classes=len(classes)

    inputlines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('input'))]
    input_shape = inputlines[0].split(": ")[-1]
    IMAGE_SIZE = tuple([int(x.replace("(", "").replace(")", "")) for x in input_shape.split(", ")])


    hublines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('tfhub_module'))]
    module_handle = hublines[0].split(": ")[-1]


    model = tf.keras.Sequential([tf.keras.layers.InputLayer(input_shape=IMAGE_SIZE + (3,)),
                                         hub.KerasLayer(module_handle, trainable=do_fine_tuning, name="module"),
                                         #         tf.keras.layers.Dropout(rate=0.1),
                                         tf.keras.layers.Dense(num_classes,
                                                               kernel_regularizer=tf.keras.regularizers.l2(0.0001),
                                                               name=model_name + "dense")
                                         ])
    model.build((None,) + IMAGE_SIZE + (3,))
 
    model.load_weights("/home/lovnower/workarea/Vision/caffe/Models/classifier_multi_single_plancton_limit10000_bis/model_weights.h5")


def load_filename(filename):
    np_image = Image.open(filename)
    np_image = np.array(np_image).astype('float32')/255
    np_image = transform.resize(np_image, (IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    np_image = np.expand_dims(np_image, axis=0)

    return np_image


def predict_image(image):
    res = model.predict(image)

    y_pred = softmax(res, axis=1)

   label=classes[np.argmax(y_pred)]

   return label,y_pred[0][np.argmax(y_pred)])


