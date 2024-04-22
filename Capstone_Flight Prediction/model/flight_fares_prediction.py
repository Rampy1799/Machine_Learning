# -*- coding: utf-8 -*-
"""Flight Fares Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Gx8HSikrblFKe2KynaHQ-DMydi_7LlGb
"""

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES
# TO THE CORRECT LOCATION (/kaggle/input) IN YOUR NOTEBOOK,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.

import os
import sys
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from urllib.parse import unquote, urlparse
from urllib.error import HTTPError
from zipfile import ZipFile
import tarfile
import shutil

CHUNK_SIZE = 40960
DATA_SOURCE_MAPPING = 'flight-price-prediction:https%3A%2F%2Fstorage.googleapis.com%2Fkaggle-data-sets%2F1957837%2F3228623%2Fbundle%2Farchive.zip%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com%252F20240421%252Fauto%252Fstorage%252Fgoog4_request%26X-Goog-Date%3D20240421T202913Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D3fd5048f0a52a3ee05a52c2f37145dc4f09769d8734204f5cc4376b3a163fd47987df1f7a3342e46582bc123bdf9e6efdc4afc3e9853d3ec80e7411f73edfc661d2af181c12209b6a49f1e8f2c9f43a39fa314d8b5c92071b00f22830d337b46eaf2bf9103ee5f681701bf885dfc4340eae61e3af884d34ccc5f9d8c845169e2ae0ea5c9f23391951cef4a079f3407565eb034f28f5a7a21e8f01602cd105de956b89e267019202829f51cf732418f528a300beaa81750313b7f07e027b274a05c81e2eb39dea9599beaaf5ab0b06bc8b44a8b6986a1d8794319bfd4ffb2a514800de54fd9f0828a10a182918865395ca9fa39b8da9c6dd0df54f43159b663c9'

KAGGLE_INPUT_PATH='/kaggle/input'
KAGGLE_WORKING_PATH='/kaggle/working'
KAGGLE_SYMLINK='kaggle'

!umount /kaggle/input/ 2> /dev/null
shutil.rmtree('/kaggle/input', ignore_errors=True)
os.makedirs(KAGGLE_INPUT_PATH, 0o777, exist_ok=True)
os.makedirs(KAGGLE_WORKING_PATH, 0o777, exist_ok=True)

try:
  os.symlink(KAGGLE_INPUT_PATH, os.path.join("..", 'input'), target_is_directory=True)
except FileExistsError:
  pass
try:
  os.symlink(KAGGLE_WORKING_PATH, os.path.join("..", 'working'), target_is_directory=True)
except FileExistsError:
  pass

for data_source_mapping in DATA_SOURCE_MAPPING.split(','):
    directory, download_url_encoded = data_source_mapping.split(':')
    download_url = unquote(download_url_encoded)
    filename = urlparse(download_url).path
    destination_path = os.path.join(KAGGLE_INPUT_PATH, directory)
    try:
        with urlopen(download_url) as fileres, NamedTemporaryFile() as tfile:
            total_length = fileres.headers['content-length']
            print(f'Downloading {directory}, {total_length} bytes compressed')
            dl = 0
            data = fileres.read(CHUNK_SIZE)
            while len(data) > 0:
                dl += len(data)
                tfile.write(data)
                done = int(50 * dl / int(total_length))
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl} bytes downloaded")
                sys.stdout.flush()
                data = fileres.read(CHUNK_SIZE)
            if filename.endswith('.zip'):
              with ZipFile(tfile) as zfile:
                zfile.extractall(destination_path)
            else:
              with tarfile.open(tfile.name) as tarfile:
                tarfile.extractall(destination_path)
            print(f'\nDownloaded and uncompressed: {directory}')
    except HTTPError as e:
        print(f'Failed to load (likely expired) {download_url} to path {destination_path}')
        continue
    except OSError as e:
        print(f'Failed to load {download_url} to path {destination_path}')
        continue

print('Data source import complete.')

# Importing the required libraries
import numpy as np
import pandas as pd

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Commented out IPython magic to ensure Python compatibility.
#imports

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.pipeline import Pipeline

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV,KFold, cross_val_predict

from sklearn.preprocessing import LabelEncoder, LabelBinarizer, OneHotEncoder, OrdinalEncoder

from sklearn.feature_extraction import DictVectorizer



# %matplotlib inline

# Fetching the data
df_main = pd.read_csv("/kaggle/input/flight-price-prediction/Clean_Dataset.csv")

df_main

"""# EDA on the dataset


"""

df_main.shape

df_main.drop(columns=['Unnamed: 0'], axis = 1, inplace = True)

df_main.shape

df_main

df_main.isna().sum()

"""As there's no null values in the dataset, we can proceed to feature engineering etc

# Visualizations
"""

# Checking for the category columns and numerical columns

df_main.dtypes

category_cols = ['airline',  'source_city', 'departure_time', 'stops', 'arrival_time', 'destination_city', 'class']

# Let's see the most hot destination cities

df_main.destination_city.value_counts().plot.bar()

"""# Prices of Destination cities mapped to avg Prices


"""

df_main.groupby("destination_city")['price'].mean().plot.bar()

df_main.groupby("source_city")['price'].mean().plot.bar()

df_main.groupby("airline")['price'].mean().plot.bar()

df_main.airline.value_counts().plot.bar()

df_main.groupby("stops")['price'].mean().plot.bar()

sns.pairplot(df_main, hue = "price", height = 3)

df_main.groupby("days_left")['price'].mean().plot()

df_main.groupby("departure_time")['price'].mean().plot()

df_main.groupby("arrival_time")['price'].mean().plot()

sns.barplot(x = "class", y ="price",  data = df_main, estimator = np.median, hue = "airline")

df_main.duration.plot.hist(bins = 20)

df_main[['airline_code', 'flight_number']] = df_main['flight'].str.split('-', n=1, expand=True)
df_main.drop("flight", axis = 1, inplace = True)
df_main.drop("airline_code", axis = 1, inplace = True)

df_main['flight_number'] = df_main['flight_number'].astype('int')

df_main.head()

df_main.flight_number.value_counts()

sns.scatterplot(x = "flight_number", y = "price", data = df_main)
plt.xticks(range(0,10001,1000))
plt.yticks(range(0,120001,10000))
plt.show()

"""# Converting Categorical Columns to Numerical Columns for Linear Regression

"""

le = LabelEncoder()

df_main['stops'] = df_main['stops'].replace({'one': 1,
                                   'zero': 0,
                                   'two_or_more': 2})

df_main[category_cols] = df_main[category_cols].apply(le.fit_transform)

label_encoders = []
for column in category_cols:
    label_encoder = LabelEncoder()
    label_encoder.fit(df_main[column])
    label_encoders.append(label_encoder)
np.save("label_encoders.npy", label_encoders)

df_main.head()

import joblib
joblib.dump(le, "label_encoder.pkl")

label_encoding_mappings = {}

for column in category_cols:
    label_encoding_mappings[column] = dict(zip(le.classes_, le.transform(le.classes_)))

label_encoding_mappings

df_main.to_csv("final_ds.csv")

import matplotlib.pyplot as plt
import seaborn as sns

# Increase the size of the heatmap
plt.figure(figsize=(12, 10))

# Plot the heatmap with correlation values annotated
sns.heatmap(df_main.corr(), annot=True)

# Show the plot
plt.show()

"""# Feature Engineering

"""

x = df_main.drop('price', axis = 1)
y = df_main['price']

"""# Training and Testing split"""

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size = 0.2)

"""# Using KFold and CV

"""

kf = KFold(shuffle=True, random_state=42, n_splits=5)

s = StandardScaler()
lr = LinearRegression()

estimator = Pipeline([("scaler", s),
                      ("regression", lr)])

predictions = cross_val_predict(estimator, x, y, cv=kf)

r2_score(y, predictions)

mean_absolute_error(y,predictions)

"""# Hyperparameter Tuning

"""

alphas = np.geomspace(1e-9, 1e0, num=10)
alphas

las = Lasso()

scores = []
coefs = []
for alpha in alphas:
    las = Lasso(alpha=alpha, max_iter=100000)

    estimator = Pipeline([
        ("scaler", s),
        ("lasso_regression", las)])

    predictions = cross_val_predict(estimator, x, y, cv = kf)

    score = r2_score(y, predictions)

    scores.append(score)

list(zip(alphas,scores))

Lasso(alpha=1e-6).fit(x, y).coef_

Lasso(alpha=1.0).fit(x, y).coef_

plt.figure(figsize=(10,6))
plt.semilogx(alphas, scores, '-o')
plt.xlabel('alphas')
plt.ylabel('R2 score');

best_estimator = Pipeline([
                    ("scaler", s),
                    ("make_higher_degree", PolynomialFeatures(degree=2)),
                    ("lasso_regression", Lasso(alpha=0.03))])

best_estimator.fit(x, y)
best_estimator.score(x, y)

predii = cross_val_predict(best_estimator, x, y, cv=kf)
r2_score(y, predii)

# Same estimator as before

estimator = Pipeline([("scaler", StandardScaler()),
        ("polynomial_features", PolynomialFeatures()),
        ("ridge_regression", Ridge())])

params = {
    'polynomial_features__degree': [1, 2, 3],
    'ridge_regression__alpha': np.geomspace(4, 20, 30)
}

grid = GridSearchCV(estimator, params, cv=kf)

grid.fit(x,y)

y_predict = grid.predict(x)

r2_score(y, y_predict)

import joblib
joblib.dump(grid, "model_main_1.pkl")

x.head()

y.head()

"""# Making Stramlit application"""

pip install streamlit

"""# Running Streamlit app using ngrok

"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# 
# import streamlit as st
# 
# st.write(' # Hello World')

# !pip uninstall pyngrok -y
# !pip install pyngrok

# !streamlit run app.py &>/dev/null&

# !ngrok update

# !ngrok authtoken 2fQsMoklEdUjhjNzzQY838kOwOl_39CAv7N6eFmJgZ2F1T5Eu

# from pyngrok import ngrok

# # Setup a tunnel to the Streamlit port 8501
# # ngrok_tunnel = ngrok.connect(port=8501)

# # Print the public URL where your Streamlit app is hosted
# print('Streamlit App can be accessed at:', ngrok_tunnel.public_url)

