'''
    This script is used to add GPS data to images.
    It solves the problem of adding GPS data to images that doesn't contain geo location, e.g., were taken by a camera that does not have GPS.
    The GPS data is taken from a file that contains the GPS data and the image name.
    The file is created by the user using Google Maps or any other GPS tool.    
    The file format is:
        https://maps.google.com/?q=31.6530003,35.1315193
        IMG-20230426-WA0002.jpg
        https://maps.google.com/?q=31.65279946743382,35.128664150834084
        IMG-20230421-WA0008.jpg
        https://maps.google.com/?q=31.652877,35.130917
        IMG-20230505-WA0021.jpg
        IMG-20230506-WA0001.jpg
        IMG-20230506-WA0002.jpg
    The input to the function is the file name, the original, GPSless images source folder path, and the destination folder path. Both folders must exist.
'''

import traceback
from exif import Image
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)



def add_new_image_data(src_folder_path, dst_folder_path, img_filename, latitude, longitude):
    try:
        img_path = f'{src_folder_path}/{img_filename}'

        with open(img_path, 'rb') as img_file:
            img = Image(img_file)

        img.gps_latitude = deg_min_sec(latitude)
        img.gps_latitude_ref = "N"
        img.gps_longitude = deg_min_sec(longitude)
        img.gps_longitude_ref = "E"
        logger.info(f'GPS locations added to {img_filename}')
        logger.info(f'gps_latitude: {img.get("gps_latitude")} {img.get("gps_latitude_ref")}')
        logger.info(f'gps_longitude: {img.get("gps_longitude")} {img.get("gps_longitude_ref")}\n')

        with open(f'{dst_folder_path}/{img_filename}', 'ab+') as new_image_file:
            new_image_file.write(img.get_file())

    except Exception as e:
        logger.error(f'traceback.format_exc(): \n {traceback.format_exc()}')
        logger.error(f'Exception: {e}')


# Convert latitude and longitude to degrees, minutes, seconds format.
def deg_min_sec(value):
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = (((value - degrees) * 60 - minutes) * 60)
    return (float(degrees), float(minutes), float(seconds))


def loop_file(file_name, image_src_path, image_dst_path):

    with open(file_name, 'r') as f:
        for line in f:
            if line.startswith('https://maps.google.com/?q='):
                latitude, longitude = line.split('=')[1].split(',')
            elif line.startswith('IMG-'):
                add_new_image_data(image_src_path, image_dst_path, line.strip(), latitude=float(latitude), longitude=float(longitude)) 
            else:#
                raise ('Not a legal line')


def print_images_data(folder_path):

    print(f'Nuber of files: {len(os.listdir(folder_path))}')

    for filename in os.listdir(folder_path):
        f = os.path.join(folder_path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            with open(f, 'rb') as img_file:
                img = Image(img_file)
    
                if not img.has_exif: print(f'filename: {filename} has no exif data')
                if img.has_exif:
                    #print(img.list_all())
                    print(f'filename: {filename}')
                    print(f'gps_latitude: {img.get("gps_latitude", None)} {img.get("gps_latitude_ref", None)}')
                    print(f'gps_longitude: {img.get("gps_longitude", None)} {img.get("gps_longitude_ref", None)}\n')        
        

if __name__ == "__main__":

    logging.info('Start')

    loop_file('loc_image_list.txt', image_src_path='./images', image_dst_path='./images_modified')

    ### A handy function to print all images GPS data
    #print_images_data('./images_modified')
