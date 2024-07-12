# -*- coding: utf-8 -*-
"""
Functions to integrate your model with the DEEPaaS API.
It's usually good practice to keep this file minimal, only performing
the interfacing tasks. In this way you don't mix your true code with
DEEPaaS code and everything is more modular. That is, if you need to write
the predict() function in api.py, you would import your true predict function
and call it from here (with some processing / postprocessing in between
if needed).
For example:

    import mycustomfile

    def predict(**kwargs):
        args = preprocess(kwargs)
        resp = mycustomfile.predict(args)
        resp = postprocess(resp)
        return resp

To start populating this file, take a look at the docs [1] and at
an exemplar module [2].

[1]: https://docs.ai4os.eu/
[2]: https://github.com/ai4os-hub/ai4os-demo_app
"""

from pathlib import Path
import pkg_resources

from multi_plankton_classification.misc import _catch_error

from webargs import fields

from multi_plankton_classification.utils import (
    load_model,
    load_filename,
    predict_image
)


BASE_DIR = Path(__file__).resolve().parents[1]


@_catch_error
def get_metadata():
    """
    DO NOT REMOVE - All modules should have a get_metadata() function
    with appropriate keys.
    """
    distros = list(pkg_resources.find_distributions(str(BASE_DIR), only=True))
    if len(distros) == 0:
        raise Exception("No package found.")
    pkg = distros[0]  # if several select first

    meta_fields = {
        "name": None,
        "version": None,
        "summary": None,
        "home-page": None,
        "author": None,
        "author-email": None,
        "license": None,
    }
    meta = {}
    for line in pkg.get_metadata_lines("PKG-INFO"):
        line_low = line.lower()  # to avoid inconsistency due to letter cases
        for k in meta_fields:
            if line_low.startswith(k + ":"):
                _, value = line.split(": ", 1)
                meta[k] = value

    return meta


def get_predict_args():
    """
    Get the list of arguments for the predict function
    """
    arg_dict = {
        "image": fields.Field(
            required=True,
            type="file",
            location="form",
            description="An image containing plankton to separate",
        ),
    }

    return arg_dict


# @_catch_error
def predict(**kwargs):
    """ 
         Prediction function 
    """
     
    # Load model
    model, image_size, classes = load_model("classifier_multi_single_plancton_limit10000_bis")
    
    # Change image format
    image = load_filename(kwargs['image'].filename, image_size)

    # Get predicted classification
    label, score = predict_image(model, image, classes)
     
    return {"label": label, "score": str(score)}


