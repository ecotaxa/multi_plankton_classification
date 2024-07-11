import tensorflow_hub as hub
import tensorflow as tf
from scipy.special import softmax
import os

from PIL import Image
import numpy as np
from skimage import transform

import multi_plankton_classification.config as cfg

def load_model(model_name):
    with open(os.path.join(cfg.MODEL_DIR, model_name, "Result_Summary.txt")) as f:
        sumlines = f.readlines()

    nameslines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('name'))]
    name_classes = nameslines[0].split(": ")[-1]
    classes=name_classes.split(",")
    num_classes=len(classes)

    inputlines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('input'))]
    input_shape = inputlines[0].split(": ")[-1]
    image_size = tuple([int(x.replace("(", "").replace(")", "")) for x in input_shape.split(", ")])


    hublines = [sumlines[itt].strip() for itt, x in enumerate(sumlines) if int(x.startswith('tfhub_module'))]
    module_handle = hublines[0].split(": ")[-1]


    model = tf.keras.Sequential([tf.keras.layers.InputLayer(input_shape=image_size + (3,)),
                                         hub.KerasLayer(module_handle, trainable=False, name="module"),
                                         #         tf.keras.layers.Dropout(rate=0.1),
                                         tf.keras.layers.Dense(num_classes,
                                                               kernel_regularizer=tf.keras.regularizers.l2(0.0001),
                                                               name=model_name + "dense")
                                         ])
    model.build((None,) + image_size + (3,))
 
    model.load_weights(os.path.join(cfg.MODEL_DIR, model_name, "model_weights.h5"))
    
    return model,image_size,classes


def load_filename(filename,image_size):
    np_image = Image.open(filename)
    np_image = np.array(np_image).astype('float32')/255
    np_image = transform.resize(np_image, (image_size[0], image_size[1], 3))
    np_image = np.expand_dims(np_image, axis=0)

    return np_image


def predict_image(model, image, classes):
    res = model.predict(image)

    y_pred = softmax(res, axis=1)

    label=classes[np.argmax(y_pred)]

    return label,y_pred[0][np.argmax(y_pred)]


