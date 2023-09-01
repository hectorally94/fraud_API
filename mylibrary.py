# Load libraries
from pandas import read_csv
import pandas as pd
import numpy as np
from pandas.plotting import scatter_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
##from sklearn.preprocessing import Imputer
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from matplotlib import pyplot
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc

from termcolor import colored as cl # text customization
from xgboost import XGBClassifier
from sklearn.svm import LinearSVC, LinearSVR, SVC, SVR
from sklearn.ensemble import BaggingClassifier, BaggingRegressor,RandomForestClassifier,RandomForestRegressor

import re
import warnings
from sklearn import metrics
warnings.filterwarnings('ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')
import pymysql
from app import app
from config import mysql
from flask import Flask, Response, jsonify
from flask import  request
import py_eureka_client.eureka_client as eureka_client
import json

