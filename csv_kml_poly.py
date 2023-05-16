#  Python program that reads in a CSV file containing latitude, longitude,
#  and name information for multiple points that form a polygon, and outputs
#  a KML file containing the polygon that can be opened in Google Earth:

# csv format 
#  ID,Latitude,Longitude
#  b store,51.019305,-114.053946
#  b store,51.019396,-114.053688
#  b store,51.019189,-114.053525
#  b store,51.019112,-114.053783
import csv
import random

def write_kml_polygon(output_file, coordinates):
    # set this file polys random color
    color = "%06x" % random.randint(0, 0xFFFFFF)
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

input_file = "output/data_dd.csv"
output_file = "output/data_kml.kml"

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

# Write KML file for each set of coordinates
#  for i, coords in enumerate(coordinates):
#      print(coords)
#      output_filename = "output/output_{}.kml".format(i)
#      #  output_filename = "output/output_{}.kml".format(coords[0][2])
#      write_kml_polygon(output_filename, coords)
write_kml_polygon(output_file, coordinates)
