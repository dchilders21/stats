import os
import sys

from flask import Flask

from stats import model_libs, match_stats, form_model, form_data

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_PATH = static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
#form_data.run_data()

print('INITIALIZED...')

#print(training_data)


# Step 1 Get Data
# Step 2 Calculate Model
# Step 3 Predict upcoming matches
