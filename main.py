from flask import Flask, jsonify
from pymongo import MongoClient
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import json
# get this object
from flask import Response

app = Flask(__name__)


def get_traces():
    """
    get_traces

    This function get the traces from remote mongodb and convert them into pandas data frame.
    :return:  The pandas data frame of traces .
    """

    # Connect to remote MongoDb
    mongo_client = MongoClient('34.90.254.95', 27017, username='ccsTraces', password='CCSTracesAnalysis54!3',
                               authSource='traces')
    db = mongo_client['traces']
    data_points = list(db.volume_create.find({}))
    df_mongo = json_normalize(data_points)

    # We are only focused in this exercise for the total duration which is info.finished so dropping others
    df_mongo = df_mongo.drop(['children', 'info.name', 'stats.driver.count', 'stats.rpc.count',
                              'stats.wsgi.count', '_id', 'info.started'], axis=1)
    df_mongo = df_mongo[np.isfinite(df_mongo['info.finished'])]

    return df_mongo


def outliers_z_score(ys):
    """
    outliers_z_score

    This function gets a list of values and apply the z score method to determine the outliers.
    :param ys: The array or list of values.
    :return:  The indexes of values which are above the threshold.
    """
    # compute mean
    mean_y = 0
    for x in ys:
        mean_y += x
    mean_y = mean_y / len(ys)

    # compute standard deviation
    stdev_y = 0
    for x in ys:
        stdev_y += (x - mean_y) ** 2
    stdev_y = np.sqrt(stdev_y / len(ys)) 

    threshold = 3
    z_scores = [] 
    for x in ys:
       z_scores.append((x - mean_y) / stdev_y) 
    
    return np.where(np.abs(z_scores) > threshold), z_scores, mean_y, stdev_y


def outliers_modified_z_score(ys):
    """
    outliers_modified_z_score

    This function gets a list of values and apply the modified z score method to determine the outliers.
    :param ys: The array or list of values.
    :return:  The indexes of values which are above the threshold.
    """
    threshold = 3
    median_y = np.median(ys) 
    ysFrame = pd.DataFrame(ys)
    median_absolute_deviation_y = ysFrame.mad() 
    modified_z_scores = [] 
    for x in ys:
        modified_z_scores.append(0.6745 * (x - median_y) / median_absolute_deviation_y)

    return np.where(np.abs(modified_z_scores) > threshold), modified_z_scores, median_y, median_absolute_deviation_y


def outliers_iqr(ys):
    """
    outliers_iqr

    This function gets a list of values and apply the IQR method to determine the outliers.
    :param ys: The array or list of values.
    :return:  The indexes of values which are outside the quartiles.
    """
    ##############################################################################
    #    TODO
    #    Calculate IQR here
    ##############################################################################
    quartile_1, quartile_3 = np.percentile(ys, [25, 75]) 
    iqr = quartile_3 - quartile_1 
    lower_bound = q1 - 1.5 * iqr 
    upper_bound = q3 - 1.5 * iqr 
    return np.where((ys > upper_bound) | (ys < lower_bound))


# TODO: Write your group number in place of #
@app.route("/")
def index():
    return "welcome to exercise 6 of group #"


# TODO:  Return the name of the project which took most of the time when you create a server in Openstack.
@app.route("/project_most_time_server_creation")
def project_most_time_server_creation():
    return ""


# TODO: Return the name of the service which took most of the time when you create a server in Openstack.
@app.route("/service_most_time_server_creation")
def service_most_time_server_creation():
    return ""


# TODO: Return the first request path triggered when you create a server in Openstack.
@app.route("/first_request_path")
def first_request_path():
    return ""


# TODO: Return the sequence of the Projects being triggered each separating
#  by a comma without any spaces (All till level 2 and including level 2) when you create a server in Openstack.
@app.route("/sequence_projects")
def sequence_projects():
    return ""


# TODO: Return the anomaly observation indexes using z-score method
@app.route("/get_outliers_z_score")
def get_outliers_z_score():
    df_mongo = get_traces()
    anomaly_observations, z_scores, mean, stdev = outliers_z_score(df_mongo['info.finished'].values)
    return Response(json.dumps(anomaly_observations[0].tolist()),  mimetype='application/json')


# TODO: Return the anomaly observation indexes using modified z-score method
@app.route("/get_outliers_modified_z_score")
def get_outliers_modified_z_score():
    df_mongo = get_traces()
    anomaly_observations, z_scores, median, mad = outliers_modified_z_score(df_mongo['info.finished'].values)
    return Response(json.dumps(anomaly_observations[0].tolist()),  mimetype='application/json')


# TODO: Return the anomaly observation indexes using IQR method
@app.route("/get_outliers_iqr")
def get_outliers_iqr():
    df_mongo = get_traces()
    anomaly_observations = outliers_iqr(df_mongo['info.finished'].values)
    return Response(json.dumps(anomaly_observations[0].tolist()),  mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
