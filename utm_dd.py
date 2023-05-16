
#  Python program that reads in a CSV file containing UTM coordinates and converts them to decimal degrees

# Here's an example input CSV file:
#  UTM Type,Easting,Northing,Zone Number,Zone Letter
#  ID,wgs84,448251.7103,5463888.924,12,S
#  ID,ns,447721.7991,5461517.686,12,S
# Output//
# ID,"Latitude", "Longitude","utm-type"
#

import csv
import utm
import pyproj
from pyproj import Transformer

def convert_utm_to_wgs84(easting, northing):
    transformer = Transformer.from_crs("EPSG:30730", "EPSG:4326")  # Nord Sahara (EPSG:30791) to WGS84 (EPSG:4326)
    lon, lat = transformer.transform( easting, northing)
    return lat, lon

def convert_utm_to_dd(utm_easting, utm_northing, zone_number, zone_letter):
    lat, lon = utm.to_latlon(utm_easting, utm_northing, zone_number, zone_letter)
    return lat, lon

#  input_file = "data_utm_wgs84_poly.csv"
#  output_file = "output/data_dd.csv"
input_file = "data_utm_poly.csv"
output_file = "output/data_dd.csv"

with open(input_file, "r") as input_csv, open(output_file, "w", newline="") as output_csv:
    reader = csv.reader(input_csv)
    writer = csv.writer(output_csv)

    # Write header to output CSV
    writer.writerow(["ID","Latitude", "Longitude","UTM-Type"])

    # Skip header row in input CSV
    next(reader)

    # Loop through each row in input CSV
    for row in reader:
        # Parse UTM coordinates and zone information from input CSV
        utm_type = row[1]
        utm_easting = float(row[2])
        utm_northing = float(row[3])
        zone_number = int(row[4])
        zone_letter = row[5]
        name = row[0]

        if utm_type == "wgs84" :
            # Convert WGS84 UTM to decimal degrees
            lat, lon = convert_utm_to_dd(utm_easting, utm_northing, zone_number, zone_letter)
        else:
            # Convert Nord Sahara UTM Zone 30N coordinates to WGS84 (EPSG:4326)
            lon, lat = convert_utm_to_wgs84(utm_easting, utm_northing)

        # Write decimal degrees to output CSV
        writer.writerow([name,lat, lon,utm_type])
