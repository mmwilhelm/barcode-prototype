import os 
import tempfile
import boto3
import calendar
import time
from flask import Flask, jsonify, render_template, request

import util

application = Flask(__name__)


def path(local_path):
  __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
  return os.path.join(__location__, local_path)


@application.route("/")
def index():
  return render_template('index.html')


@application.route("/home")
def home():
  return render_template('home_feed.html')


@application.route("/events")
def events():
  return render_template('events_feed.html', events=util.get_recent_events())


@application.route('/upload_picture', methods=['POST'])
def upload_picture():
  print("Receiving image")
  _, tmp = tempfile.mkstemp(".png")
  request.files['picture'].save(tmp)
  qr_data = util.read_qr_code(tmp)
  s3_path = "{}/{}_{}".format("pictures", str(int(calendar.timegm(time.gmtime()))), os.path.split(tmp)[1])
  blob_count = util.blob_count(tmp)
  dish_id = "N/A"
  if qr_data and len(qr_data) > 0:
    print(qr_data)
    dish_id = qr_data[0]
    util.insert_event(qr_data[0], s3_path, blob_count, -1)
  else:
    print("No qr data found")
  # Todo - other thread
  data = open(tmp, 'rb')
  s3 = boto3.resource('s3')
  s3.Bucket('barcode-website').put_object(Key=s3_path, Body=data)
  print("Done")
  return render_template('feed_card.html', title="Image uploaded for dish: {}".format(dish_id), supporting_text="Blob count was {}".format(blob_count))

