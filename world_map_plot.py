from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

import csv
import os

import ntpath

import argparse

import pdb

# based off code authored by Joshua Hrisko
# https://engineersportal.com/blog/2018/8/16/rotating-globe-in-python-using-basemap-toolkit

# Custom modules
import input_new_papers_to_csv as inpc



def draw_world_map(subjects, yr_range=[2010,2019]):

    # Make list of subjects case insensitive, as well
    # as replace white space with underscores
#    for subject in subjects: 
#        subjects.pop(subject)
#        subject = subject.replace(" ", "_").lower()
#        subjects.append(subject)

    fig = plt.figure(figsize=(9,6))

    # set perspective angle
    lat_viewing_angle = 50
    lon_viewing_angle = -73

    # define color maps for water and land
    ocean_map = (plt.get_cmap('ocean'))(210)
    cmap = plt.get_cmap('gist_earth')

    # call the basemap and use orthographic projection at viewing angle
    m = Basemap(projection='vandg',
                lon_0=0, resolution='c')

    # coastlines, map boundary, fill continents/water, fill ocean, draw countries
    m.drawcoastlines()
    m.drawmapboundary(fill_color=ocean_map)
    m.fillcontinents(color=cmap(200), lake_color=ocean_map)
    m.drawcountries()

    # latitude/longitude line vectors
    lat_line_range = [-90,90]
    lat_lines = 8
    lat_line_count = (lat_line_range[1]-lat_line_range[0])/lat_lines

    merid_range = [-180,180]
    merid_lines = 9
    merid_count = (merid_range[1]-merid_range[0])/merid_lines

    m.drawparallels(np.arange(lat_line_range[0], lat_line_range[1], lat_line_count))
    m.drawmeridians(np.arange(merid_range[0], merid_range[1], merid_count))
    m.drawmapboundary(fill_color='aqua')

    # plot names of institutes
    institutions = read_paper_csv(subjects=subjects, 
                            yr_range=yr_range)

    # Get the lats, lons, no of mentions, and subjects of papers
    # from each institute
    inst_lats = []
    inst_lons = []
    inst_labels = []
    inst_no_mentions = []
    institute_subjects = []
    all_subjects = []

    # Initiate multiple marker colors for institutes with papers in
    # multiple subjects 
    marker_colors = ['indigo', 'blue', 'aqua', 'green', 'yellow',
                     'orange', 'sienna', 'red', 'grey', 'black']

    coords_lat = {}
    coords_lon = {}
    mk_colors = {}

    for institute_name, institute_dict in institutions.items():
        # keep track of institute latitudes and longitudes so that
        # labels can be applied later
        inst_lats.append(institute_dict['lat'])
        inst_lons.append(institute_dict['lon'])
        inst_labels.append(institute_name)
        inst_no_mentions.append(institute_dict['no_mentions'])

#        lats.append(institute['lat'])
#        lons.append(institute['lon'])
#        no_mentions.append(institute['no_mentions'])
        mk_idx = 0
        for inst_subject in institute_dict['subjects']:
            if inst_subject not in institute_subjects:
                institute_subjects.append(inst_subject)
                coords_lat[inst_subject] = [institute_dict['lat']]
                coords_lon[inst_subject] = [institute_dict['lon']]
                mk_colors[inst_subject] = marker_colors[mk_idx]
                mk_idx += 1
            else:
                coords_lat[inst_subject].append(institute_dict['lat'])
                coords_lon[inst_subject].append(institute_dict['lon'])


    x_all = []
    y_all = []

    mk_size = 14.0

    for subject in institute_subjects:
        lats = coords_lat[subject]
        lons = coords_lon[subject]
        mk_color = mk_colors[subject]

        # test lons and lats
        lats.append(37.8716)
        lons.append(237.7273)
        pdb.set_trace()
        m.plot(lons, lats, color=mk_color,
                            marker='o', markersize=mk_size,
                            zorder=10)
        mk_size -= 2.0

    # apply labels to all markers applied to world map
    for name, num_mentions, xpt, ypt in zip(inst_labels,
                        inst_no_mentions, inst_lons, inst_lats):
        plt.text(xpt+50000.0, ypt+50000.0, name + ' (' +
                    str(num_mentions) + ')')

    # save figure at 150 dpi and show it
    #plt.savefig('orthographic_map_example_python.png', dpi=150, transparent=True)
    plt.show()


def read_paper_csv(subjects=None, yr_range=(2010, 2019)):
    '''Read provided csv detailing papers with institutes of origin'''

    # check if a particular csv was specified. If not, open all
    # csv files and provide contents
    csv_list = []
    for subject in subjects:
        subject_csv_list = directory_walk('.', subject=subject)
        for csv_file in subject_csv_list:
            csv_list.append(csv_file)

    if not csv_list:
        raise Exception("""Error: No csv file found fitting subject
                        description.""")
    start_yr = yr_range[0]
    end_yr = yr_range[1]

    # Initialize a dictionary of dictionaries containing all info
    # needed to plot the institutions provided by paper csv
    # files on the world map. The keys of the dictionaries are
    # institute names, and the values are dictionaries containing
    # coordinates of the institutions, as well as number of times
    # they were mentioned
    institutions = {}

    for csv_file in csv_list:
        # Get basename of file and remove file extension to get the
        # subject 

        # Grab the subject of the csv, which is the name of the 
        # csv file minus the extension
        csv_subject = os.path.split(csv_file)[-1][:-4]
        with open(csv_file, 'r') as cf:
            csvreader = csv.reader(cf)
            fields = next(csvreader)

            for row in csvreader:

                # Check whether or not the row is empty
                if not row:
                    continue

                # Check if the paper detailed in row was written
                # in the given year range
                elif int(row[1].strip()) not in range(start_yr, end_yr):
                    continue

                else:
                    institute = row[3].strip()
                    if institute in institutions:
                        institutions[institute]['no_mentions'] += 1
                        if csv_subject not in \
                                    institutions[institute]['subjects']:
                            institutions[institute]['subject'].append(
                                                    csv_subject)

                    # Else, add new institutions dictionary entry
                    # whose key is the institute's name and whose
                    # value is another dictionary containing 
                    # information about the institute
                    else:
                        institutions[institute] = {}
                        institutions[institute]['name'] = row[3].strip()
                        institutions[institute]['lat'] = \
                                                float(row[4].strip())
                        institutions[institute]['lon'] = \
                                                float(row[5].strip())
                        institutions[institute]['no_mentions'] = 1
                        institutions[institute]['subjects'] = []
                        institutions[institute]['subjects'].append(
                                                    csv_subject)

    return institutions


def directory_walk(start_directory, subject=None):

    csv_list = []
    for dirpath, dirnames, filenames in os.walk(start_directory):


        for filename in filenames:
            if subject != None and subject == filename.lower()[:-4]:
                csv_path = os.path.join(dirpath, filename)
                csv_list.append(csv_path)

            elif subject == None and filename.endswith('.csv'):
                csv_path = os.path.join(dirpath, filename)
                csv_list.append(csv_path)

        if dirpath.lower().endswith(subject.lower()):
            # Do a recursive call to walk down this path and retrieve
            # all files and dirs
            csv_list = directory_walk(dirpath, subject=None)
            return csv_list

    return csv_list


class ExhaustError(Exception):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Arguments to be 
        input to create world map of all papers that I have read thus 
        far''')
    parser.add_argument('-s', '--subject_list', type=str, nargs='+',
                    help='List of subjects to be plotted in world map',
                    required=True)
    parser.add_argument('-yr', '--year_range', type=int, 
                        help="""Give the range of years for papers""", 
                        nargs=2)
    parsed_flags, _ = parser.parse_known_args()
    subject_list = []
    for subject in parsed_flags.subject_list:
        subject = subject.lower()
        subject_list.append(subject)
    if parsed_flags.year_range:
        draw_world_map(subject_list, yr_range=parsed_flags.year_range)
    else:
        draw_world_map(subject_list)

