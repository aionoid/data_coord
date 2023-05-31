# TODO: change kml to split "Region" to folders or Files

import os
import random
import copy
import csv
import utm
import typer
import pyproj
import pandas as pd
import simplekml as sk
from rich.console import Console
from rich.table import Table
from pyproj import Transformer
from typing_extensions import Annotated

app = typer.Typer()
console = Console()

directory = "output"

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

        #  f.write("<Folder><name>{}</name>\n".format("__LOCATION__FOLDER__NAME__"))
        #  # data inside for location
        #  f.write("</Folder>\n")

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
def utm2dd_form():
    """
    utm 2 dd table form
    """
    console.print("input csv format")
    tablein = Table("ID","UTM Type","Easting","Northing","Zone Number","Zone Letter")
    tablein.add_row("id_name_project_01","wgs84","448251.7103","5463888.924","30","R")
    tablein.add_row("id_name_project_02","ns","448251.7103","5463888.924","30","R")
    console.print(tablein)
    console.print("output csv format")
    tableout = Table("ID","Latitude", "Longitude","utm-type","Location")
    tableout.add_row("id_name_project_01","27.25156458","-0.2514588","WGS84","tinilan-w")
    tableout.add_row("id_name_project_02","27.69854712","-0.2564847","ns","tinilan-e")
    console.print(tableout)
    

@app.command()
def csv2kml_form():
    """
    csv 2 kml table form
    """
    console.print("input csv format")
    tablein = Table("ID","Latitude", "Longitude")
    tablein.add_row("id_name_project_01","27.25156458","-0.2514588")
    tablein.add_row("id_name_project_02","27.25156458","-0.2514588")
    console.print(tablein)

@app.command()
def splitter_form():
    """
    splitter table form
    """
    console.print("input csv format")
    tablein = Table("id_name_project","owner name","project name","project in latin","category","Location","municipal","the state","The area granted m2","state of project","state of file","color","Latitude", "Longitude")
    tablein.add_row("id_name_project_01","","")
    tablein.add_row("id_name_project_02","...","...")
    console.print(tablein)

@app.command()
def utm2dd(inf: str):
    """
        reads in a CSV file containing UTM coordinates and converts them to decimal degrees
        check utm2dd-form for input csv format

        #  Here's an example input CSV file:
        #  UTM Type,Easting,Northing,Zone Number,Zone Letter
        #  ID,wgs84,448251.7103,5463888.924,12,S
        #  ID,ns,447721.7991,5461517.686,12,S
        #  Output//
        #  ID,"Latitude", "Longitude","utm-type","Location"
        #
    """
    input_file = f"{inf}.csv"
    output_file = f"{directory}/{inf}_dd.csv"
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
            name = row[12]

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
        reads in a CSV file containing latitude, longitude, and outputs a KML file containing the polygon.
        check csv2kml-form for csv format

        #  reads in a CSV file containing latitude, longitude,
        #  and name information for multiple points that form a polygon, and outputs
        #  a KML file containing the polygon that can be opened in Google Earth:
        #  input csv format 
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
def splitter(data: Annotated[str, typer.Argument(help="location to csv data file")]):
    """
    split data by Location with non null coordinates
    """
    # read the large csv file into a pandas dataframe
    df = pd.read_csv(data)

    column_name = "Location"
    # get the unique values of the column you want to split the data by
    column_values = df[column_name].unique()

    # loop over the unique values of the column
    for value in column_values:
        # create a dataframe for each unique value
        value_df = df[df[column_name] == value]
        # remove ID column
        value_df = value_df.drop(columns=['id_name_project'])
        new_df = value_df.dropna(subset=['Latitude'])

        # write the dataframe to a new csv file
        #  value_df.to_csv(f'{column_name}_{value}.csv', index=False)
        #  new_df.to_csv(f'output/{column_name}_{value}_nonull.csv', index=False)
        new_df.to_csv(f'output/{value}.csv', index=False)

@app.command()
def csv2pins(data: Annotated[str, typer.Argument(help="location to csv data file")]):
    """
    read csv file to pins in google earth kml file
    """
    # TEMP create styles
    
    style1 = sk.Style() #creates shared style for all points
    style1.iconstyle.color = sk.Color.red #lime green
    style1.iconstyle.icon.href ='http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    style1.iconstyle.scale = 1
    style1.labelstyle.scale = 1
    style1.balloonstyle.bgcolor = sk.Color.darkred
    style1.balloonstyle.textcolor = sk.Color.white

    #  style2 = copy.copy(style1) #creates shared style for all points
    style2 = sk.Style() #creates shared style for all points
    style2.iconstyle.icon.href ='http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    style2.iconstyle.color = sk.Color.yellow 
    style2.balloonstyle.bgcolor = sk.Color.goldenrod
    style2.balloonstyle.textcolor = sk.Color.black

    #  style3 = copy.copy(style1)
    style3 = sk.Style() #creates shared style for all points
    style3.iconstyle.icon.href ='http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    style3.iconstyle.color = sk.Color.blue 
    style3.balloonstyle.bgcolor = sk.Color.darkblue
    style3.balloonstyle.textcolor = sk.Color.white

    #  style4 =copy.copy(style1)
    style4 = sk.Style() #creates shared style for all points
    style4.iconstyle.icon.href ='http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    style4.iconstyle.color = sk.Color.green
    style4.balloonstyle.bgcolor = sk.Color.darkgreen
    style4.balloonstyle.textcolor = sk.Color.white

    #  style5 = copy.deepcopy(style1)
    style5 = sk.Style() #creates shared style for all points
    style5.iconstyle.icon.href ='http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    style5.iconstyle.color = sk.Color.orange
    style5.balloonstyle.bgcolor = sk.Color.orangered
    style5.balloonstyle.textcolor = sk.Color.white
    ############
    # create kml
    kml = sk.Kml(name="Adrar", open=1)
    # read the large csv file into a pandas dataframe
    df = pd.read_csv(data)

    column_name = "Location"
    # get the unique values of the column you want to split the data by
    column_values = df[column_name].unique()

    # loop over the unique values of the column
    for value in column_values:
        # create a dataframe for each unique value
        value_df = df[df[column_name] == value]
        # remove ID column
        value_df = value_df.drop(columns=['id_name_project'])
        new_df = value_df.dropna(subset=['Latitude'])
        new_df = new_df.reset_index()  # make sure indexes pair with number of rows
        if new_df.empty:
            #  print(f'location {value} is empty')
            pass
        else:
            # create folder for kml
            fol = kml.newfolder(name=value)
            for index, row in new_df.iterrows():
                pnt = fol.newpoint(name=row["owner name"], coords =[(row["Longitude"],row["Latitude"])])
                for h in new_df.head():
                    if h == "color":
                        if row['color'] == 1:
                            pnt.style = style1
                            #  print("style 1")
                        elif row['color'] == 2:
                            pnt.style = style2
                            #  print("style 2")
                        elif row['color'] == 3:
                            pnt.style = style3
                            #  print("style 3")
                        elif row['color'] == 4:
                            pnt.style = style4
                            #  print("style 4")
                        elif row['color'] == 5:
                            pnt.style = style5
                            #  print("style 5")
                    elif h in ["index","Longitude","Latitude"]:
                        #  print(row["index"])
                        pass
                    else:
                        pnt.extendeddata.newdata(name=h, value=row[h], displayname=h)
    kml.save("adrar.kml")

def newkml_(data: str):
    # read the large csv file into a pandas dataframe
    df = pd.read_csv(data)

    column_name_location = "Location"
    column_name_id = "ID"
    # get the unique values of the column you want to split the data by
    location_values = df[column_name_location].unique()

    # loop over the unique values of the column
    for value in location_values:
        print("LOCAITON {}".format(value))
        # create a dataframe for each unique value
        location_df = df[df[column_name_location] == value]
        # drop empty "Latitude" value
        location_df = location_df.dropna(subset=['Latitude'])
        # get unique value for id on location_dataframe
        id_name_values = location_df[column_name_id].unique()
        for id_name in id_name_values:
            print("ID {}".format(id_name))
            # create a dataframe for each name_id
            id_name_df = df[df[column_name_id] == id_name ]
            for ind in id_name_df.index:
                 print(df['Latitude'][ind], df['Longitude'][ind])


@app.command()
def newkml(data: str):
    # read the large csv file into a pandas dataframe
    df = pd.read_csv(data)

    column_name_location = "Location"
    column_name_id = "ID"
    # get the unique values of the column you want to split the data by
    location_values = df[column_name_location].unique()

    # set this file polys random color
    #  color = "%06x" % random.randint(0, 0xFFFFFF)
    color = generate_dark_color_hex()
    output_file = f"{data}_kml.kml"
    with open(output_file, "w") as f:
        # Write KML header
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
        f.write("<Document>\n")
        #  style = f"<Style id=\"msn_ylw-pushpin44\"><LineStyle><color>ff{color}</color><width>3.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n"
        #  f.write(style)

        # loop over the unique values of the column
        for value in location_values:
            color = generate_dark_color_hex()
            f.write(f"<StyleMap id=\"m_ylw-pushpin{color}\"> <Pair> <key>normal</key> <styleUrl>#s_ylw-pushpin{color}</styleUrl> </Pair> <Pair> <key>highlight</key> <styleUrl>#s_ylw-pushpin_hl{color}</styleUrl> </Pair> </StyleMap> <Style id=\"s_ylw-pushpin{color}\"> <LineStyle> <color>ff{color}</color><width>3.2</width> </LineStyle> <PolyStyle> <color>4d{color}</color> </PolyStyle> </Style> <Style id=\"s_ylw-pushpin_hl{color}\"> <LineStyle><width>3.2</width> <color>ff{color}</color> </LineStyle> <PolyStyle> <color>4d{color}</color> </PolyStyle> </Style>")
            f.write("<Folder><name>{}</name>\n".format(value))
            # Write KML polygon
            # data inside for location
            print("LOCAITON {}".format(value))
            # create a dataframe for each unique value
            location_df = df[df[column_name_location] == value]
            # drop empty "Latitude" value
            location_df = location_df.dropna(subset=['Latitude'])
            # get unique value for id on location_dataframe
            id_name_values = location_df[column_name_id].unique()
            for id_name in id_name_values:
                print("ID {}".format(id_name))
                # create a dataframe for each name_id
                id_name_df = df[df[column_name_id] == id_name ]
                f.write("<Placemark>\n")
                f.write("<name>{}</name>\n".format(id_name))
                f.write(f"<styleUrl>#m_ylw-pushpin{color}</styleUrl>\n")
                #  style = f"<Style><LineStyle><color>ff{color}</color><width>3.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n"
                #  f.write(style)
                f.write("<Polygon>\n")
                f.write("<outerBoundaryIs>\n")
                f.write("<LinearRing>\n")
                f.write("<coordinates>\n")
                for ind in id_name_df.index:
                    lat = id_name_df['Latitude'][ind]
                    lon = id_name_df['Longitude'][ind]
                    print(df['Latitude'][ind], df['Longitude'][ind],ind)
                    f.write("{},{},0\n".format(lon, lat))
                # Write the first coordinate again to close the polygon
                first_coord = id_name_df.index[0]
                lat = df['Latitude'][first_coord]
                lon = df['Longitude'][first_coord]
                f.write("{},{},0\n".format(lon, lat))
                # Finish writing the KML polygon
                f.write("</coordinates>\n")
                f.write("</LinearRing>\n")
                f.write("</outerBoundaryIs>\n")
                f.write("</Polygon>\n")
                f.write("</Placemark>\n")
            # close folder
            f.write("</Folder>\n")
        # Write KML footer
        f.write("</Document>\n")
        f.write("</kml>\n")

def copyrights():
    """
    print devloper and version 
    """
    tablein = Table("devloper","version")
    tablein.add_row("B. Yacoub","1.2.0")
    console.print(tablein)

if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    copyrights()
    app()

