import typer

import random
import csv
import utm
import pyproj
from pyproj import Transformer

app = typer.Typer()

def convert_utm_to_wgs84(easting, northing):
    transformer = Transformer.from_crs("EPSG:30730", "EPSG:4326")  # Nord Sahara (EPSG:30791) to WGS84 (EPSG:4326)
    lon, lat = transformer.transform( easting, northing)
    return lat, lon

def convert_utm_to_dd(utm_easting, utm_northing, zone_number, zone_letter):
    lat, lon = utm.to_latlon(utm_easting, utm_northing, zone_number, zone_letter)
    return lat, lon


def generate_dark_color_hex():
    # Generate random RGB values in the range 0-127 (to produce darker colors)
    red = random.randint(0, 127)
    green = random.randint(0, 127)
    blue = random.randint(0, 127)
    # Convert RGB values to hexadecimal
    color_hex = "{:02x}{:02x}{:02x}".format(red, green, blue)
    #  color_hex = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    return color_hex

def write_kml_polygon(output_file, coordinates):
    # set this file polys random color
    #  color = "%06x" % random.randint(0, 0xFFFFFF)
    color = generate_dark_color_hex()
    with open(output_file, "w") as f:
        # Write KML header
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        f.write("<Document>\n")
        style = f"<Style id=\"msn_ylw-pushpin44\"><LineStyle><color>ff{color}</color><width>3.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n"
        f.write(style)
        #  f.write("<Style id=\"msn_ylw-pushpin44\"><LineStyle><color>ff00ffff</color><width>3.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n")

        for i, coords in enumerate(coordinates):
            # set diffrent color for each poly
            #  color = "%06x" % random.randint(0, 0xFFFFFF)
            # Write KML polygon
            f.write("<Placemark>\n")
            f.write("<name>{}</name>\n".format(coords[0][2]))
            f.write("<styleUrl>#msn_ylw-pushpin44</styleUrl>\n")
            #  style = f"<Style><LineStyle><color>ff{color}</color><width>3.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n"
            #  f.write(style)
            f.write("<Polygon>\n")
            f.write("<outerBoundaryIs>\n")
            f.write("<LinearRing>\n")
            f.write("<coordinates>\n")

            # Loop through each coordinate and write it to the KML file
            for coord in coords:
                lon, lat = coord[:2]
                f.write("{},{},0\n".format(lon, lat))

            # Write the first coordinate again to close the polygon
            lon, lat = coords[0][:2]
            f.write("{},{},0\n".format(lon, lat))

            # Finish writing the KML polygon
            f.write("</coordinates>\n")
            f.write("</LinearRing>\n")
            f.write("</outerBoundaryIs>\n")
            f.write("</Polygon>\n")
            f.write("</Placemark>\n")

        # Write KML footer
        f.write("</Document>\n")
        f.write("</kml>\n")

@app.command()
def utm2dd(inf: str):
    """
        #  Python program that reads in a CSV file containing UTM coordinates and converts them to decimal degrees

        # Here's an example input CSV file:
        #  UTM Type,Easting,Northing,Zone Number,Zone Letter
        #  ID,wgs84,448251.7103,5463888.924,12,S
        #  ID,ns,447721.7991,5461517.686,12,S
        # Output//
        # ID,"Latitude", "Longitude","utm-type"
        #
    """
    input_file = f"{inf}.csv"
    output_file = f"{inf}_dd.csv"
    print(f"input '{input_file}', output '{output_file}'")

    with open(input_file, "r") as input_csv, open(output_file, "w", newline="") as output_csv:
        reader = csv.reader(input_csv)
        writer = csv.writer(output_csv)

        # Write header to output CSV
        writer.writerow(["ID","Latitude", "Longitude","UTM-Type","Location"])

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
            location = row[8]
            name = row[0]

            if utm_type == "wgs84" :
                # Convert WGS84 UTM to decimal degrees
                lat, lon = convert_utm_to_dd(utm_easting, utm_northing, zone_number, zone_letter)
            else:
                # Convert Nord Sahara UTM Zone 30N coordinates to WGS84 (EPSG:4326)
                lon, lat = convert_utm_to_wgs84(utm_easting, utm_northing)

            # Write decimal degrees to output CSV
            writer.writerow([name,lat, lon,utm_type,location])

@app.command()
def csv2kml(inf: str):
    """
        #  Python program that reads in a CSV file containing latitude, longitude,
        #  and name information for multiple points that form a polygon, and outputs
        #  a KML file containing the polygon that can be opened in Google Earth:

        # csv format 
        #  ID,Latitude,Longitude
        #  b store,51.019305,-114.053946
        #  b store,51.019396,-114.053688
        #  b store,51.019189,-114.053525
        #  b store,51.019112,-114.053783
    """
    #  input_file = f"{inf}_dd.csv"
    input_file = f"{inf}.csv"
    output_file = f"{inf}_kml.kml"
    print(f"make kml poly file: input '{input_file}', output '{output_file}'")

    coordinates = []

    with open(input_file, "r") as input_csv:
        reader = csv.reader(input_csv)

        # Skip header row in input CSV
        next(reader)

        # Loop through each row in input CSV and add it to the list of coordinates
        current_name = None
        current_coords = []
        for row in reader:
            name = row[0]
            lat = float(row[1])
            lon = float(row[2])

            if current_name is None:
                current_name = name

            if name != current_name:
                coordinates.append(current_coords)
                current_coords = []
                current_name = name

            current_coords.append((lon, lat, name))

        # Append the last set of coordinates to the list
        coordinates.append(current_coords)

    write_kml_polygon(output_file, coordinates)

@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()


#  input_file = "data_utm_wgs84_poly.csv"
#  output_file = "output/data_dd.csv"
