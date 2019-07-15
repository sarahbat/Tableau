# -*- coding: utf-8 -*-
"""
Merge all point locations in multiple GPX files in a single directory
Write to a single CSV

@author: sbattersby

Todo: set up with args to run from command line and set input directory location, output file name
"""

import gpxpy
import os
import csv


def main(directory_path, file_output):
    csv_out = open(file_output, 'w', newline='')
    csv_writer = csv.writer(csv_out, delimiter='|', lineterminator='\n')
    csv_writer.writerow(['lat'] + ['lon'] + ['elev'] + ['time'] + ['filename'])

    for filename in os.listdir(directory_path):
        if filename.endswith(".gpx"):
            print(filename)
            gpx_file = open(directory_path + '\\' + filename, 'r')

            gpx = gpxpy.parse(gpx_file)

            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        csv_writer.writerow(
                            [str(point.latitude)] +
                            [str(point.longitude)] +
                            [str(point.elevation)] +
                            [str(point.time)] +
                            [filename])

    csv_out.close()

    return 0


if __name__ == "__main__":
    main(
        directory_path='C:\\Users\\sbattersby\\Downloads\\gpxdata',
        file_output='c:\\temp\\output.csv')
