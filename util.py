import os
from PIL import Image
from PIL import ImageFilter
import zbarlight
import mysql.connector
import cv2
import numpy as np

def path(local_path):
  __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
  return os.path.join(__location__, local_path)


def read_qr_code(image_path):
  with open(image_path, 'rb') as image_file:
    image = Image.open(image_file)
    image.load()
  # image.thumbnail((1024, 1024), Image.ANTIALIAS)
  codes = zbarlight.scan_codes('qrcode', image)
  return codes


#host='barcode.csy3ezn4ypnq.us-west-2.rds.amazonaws.com',
def insert_event(dish_id, image_path, pupae_count, larvae_count):
  cnx = mysql.connector.connect(
    user='barcode_master',
    password=os.environ['BARCODE_DB_PASSWORD'],
    database='barcode_db',
    host='barcode3.csy3ezn4ypnq.us-west-2.rds.amazonaws.com',
    port=3306,
    )
  cursor = cnx.cursor()
  query = """
  INSERT INTO events (dish_id, image_path, timestamp, pupae_count, larvae_count)
  VALUES (%s, %s, current_timestamp(), %s, %s)
  """
  data = (dish_id, image_path, pupae_count, larvae_count)
  cursor.execute(query, data)
  cnx.commit()
  cursor.close()
  cnx.close()


def get_recent_events():
  cnx = mysql.connector.connect(
    user='barcode_master',
    password=os.environ['BARCODE_DB_PASSWORD'],
    database='barcode_db',
    host='barcode3.csy3ezn4ypnq.us-west-2.rds.amazonaws.com',
    port=3306,
    )
  cursor = cnx.cursor()
  query = """
  select dish_id, image_path, timestamp, pupae_count, larvae_count from events order by timestamp desc limit 100;
  """
  cursor.execute(query)
  result = []
  for (dish_id, image_path, timestamp, pupae_count, larvae_count) in cursor:
    result.append((dish_id, image_path, timestamp, pupae_count, larvae_count))
  cursor.close()
  cnx.close()
  return result


def blob_count(image_path):
  params = cv2.SimpleBlobDetector_Params()
  params.minThreshold = 100
  params.maxThreshold = 1000
  params.filterByArea = True
  params.minArea = 200
  params.filterByCircularity = False
  params.minCircularity = 0.1
  params.filterByConvexity = False
  params.minConvexity = 0.87
  params.filterByInertia = False
  params.minInertiaRatio = 0.01
  detector = cv2.SimpleBlobDetector_create(params)
  img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

  height, width = img.shape[:2] 
  aspect = height / width
  img = cv2.resize(img, (1000, 1000*aspect), interpolation = cv2.INTER_CUBIC)

  # Top two thirds
  height, width = img.shape[:2] 
  img = img[0:int(height*.66), :]
  keypoints = detector.detect(img)
  im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
  cv2.imwrite("/mnt/c/Users/Mark/Desktop/cv_out.png", im_with_keypoints)
  return len(keypoints)

# print(blob_count("/mnt/c/Users/Mark/Desktop/blobs.png"))
