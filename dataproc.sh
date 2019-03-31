#!/usr/bin/env bash

gcloud beta dataproc clusters create my-cluster \
    --image-version=preview \
    --metadata 'PIP_PACKAGES=requests pyquery' \
    --initialization-actions \
    gs://dataproc-initialization-actions/python/pip-install.sh
