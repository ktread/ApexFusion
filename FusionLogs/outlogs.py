import os
import requests
from google.cloud import storage
from datetime import date
import xml.etree.ElementTree as ET
import pandas as pd
import os
from io import StringIO
import csv
from google.cloud import storage

path = "/Users/treads/Documents/apex/"
date = date.today().strftime('%y%m%d')

params = {'sdate': date}
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/treads/Documents/fusion.json"
outlogpath = '/Users/treads/Documents/apex/outlog.csv'
dtlogpath = '/Users/treads/Documents/apex/datalogs.csv'


def outlog():
    r = requests.get('http://192.168.86.50:80/cgi-bin/outlog.xml', params=params)
    root = ET.fromstring(r.text)
    outlog = {}
    for child in root:
        for node in child:
            if node.tag in outlog:
                outlog[node.tag].append(node.text)
            else:
                outlog[node.tag] = [node.text]
    outlogdf = pd.DataFrame(outlog)
    outlogdf.to_csv('/Users/treads/Documents/apex/outlog.csv')


def datalog():
    datalog = {}
    dates = []
    r = requests.get('http://192.168.86.50:80/cgi-bin/datalog.xml', params=params)
    root = ET.fromstring(r.text)
    for child in root:
        for node in child:
            if node.tag == 'date':
                currentdate = node.text
            elif node.tag == 'probe':
                dates.append(currentdate)
                for endpoint in node:
                    if endpoint.tag in datalog:
                        datalog[endpoint.tag].append(endpoint.text)
                    else:
                        datalog[endpoint.tag] = [endpoint.text]
    datalogdf = pd.DataFrame(datalog)
    datalogdf['date'] = dates

    datalogdf.to_csv('/Users/treads/Documents/apex/datalogs.csv')


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    bucket_name = bucket_name
    source_file_name = source_file_name
    destination_blob_name = destination_blob_name
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


if __name__ == '__main__':
    outlog()
    datalog()
    upload_blob("fusion_logs", dtlogpath, "datalogs" + date + ".txt")
    upload_blob("fusion_logs", outlogpath, "outlogs" + date + ".txt")
