from geopy import geocoders
from PyPDF2 import PdfFileReader, PdfFileWriter
from urllib.error import HTTPError

import csv
import os
import argparse

# DEBUGGING ONLY
import time

import json

# Custom modules
import world_map_plot as wmp

def input_stuff_to_paper_csv(flags):

    subject = input("\nSubject of paper: ").strip()
    paper_title = input("\nName of paper: ").strip()
    year_written = input("\nYear Written: ").strip()
    first_author = input("\nFirst Author: ").strip()
    institute_of_origin = input("\nInsititute of origin: ").strip()

    # Use geolocation service to find the latitude and longitude of
    # the institute of the first author
    try:
        geolocater = geocoders.GeoNames(username=flags.geonames_username)
        location_info = geolocater.geocode(institute_of_origin)
        longitude = location_info['lng']
        latitude = location_info['lat']

    # If the GeoName server cannot be accessed for some reason, ask
    # user for manual input
    except HTTPError as e:
        print("Request to GeoNames server failed due to ", e)
        confirmation = input("Manually input lat/long? (y/n): ")

        confirmation = ask_for_confirmation("Manually input lat/long?")

        if confirmation:
               while True:
                latitude = input("\nLatitude of institute: ").strip()
                longitude = input("\nLongitude of institute: ").strip()

                # See if lat/lon input can be converted to a float. If it
                # can, treat it as a valid entry. We can check later to
                # see if the input lat/lon actually correlate to valid
                # coordinates
                # TODO: write some verification function to see if the lat/lon
                #       input is actually valid
                try:
                    float(latitude)
                    float(longitude)

                except ValueError:
                    print("Error: input could not be converted to float")
                    print("Try Again")
                    pass

    # Replace whitespace in subject with underscore and make all
    # characters lowercase
    subject = subject.replace(" ", "_").lower()

    fields = [paper_title, year_written, first_author,
                institute_of_origin, latitude, longitude]

    csv_list = []
    csv_list = wmp.directory_walk(root_dir, subject=subject)

    if not csv_list:
        csv_addr = find_fitting_subject_directory(root_dir, subject, root_dir)
        csv_list.append(csv_addr)

    for subj_csv in csv_list:
        if os.path.exists(subj_csv):
            with open(subj_csv, 'a') as scsv:
                writer = csv.writer(scsv)
                writer.writerow(fields)
        else:
            with open(subj_csv, 'w') as scsv:
                writer = csv.writer(scsv)
                writer.writerow(fields)

    return

def write_input_as_pdf_metadata(flags):
    """
    Performs same actions as input_stuff_to_paper_csv function
    (i.e., asks user for input on details of relevant paper),
    but scrawls through relevant directories looking for all relevant
    pdfs and saves user input as metadata to the pdf itself. This
    allows us to look up the relevant metadata with the paper itself,
    rather than storing it all in a seperate csv file, which would
    make correlation difficult
    """

    # First scrawl through projects directory to find papers of interest
    # (in effect, we are just looking for any pdfs in the projects directory
    # and asking the user if it's a paper we would like to track on the
    # world map
    root_directory = flags.project_dir
    pdf_list = []
    for subdir, dirs, files in os.walk(flags.project_dir):
        for f in files:
            if f.endswith('.pdf'):
                pdf_list.append(f)

    # Ask user if they want to input any metadata for this paper (e.g.,
    # probably don't want to add metadata to any random pdf we find
    # while scrawling through the project directory
    for pdf_name in pdf_list:
        confirm_metadata_input = ask_for_confirmation("Do you want to input metadata for {}?".format(pdf_name))

        if confirm_metadata_input:
                # Ask for subject of paper.
                if os.path.exists(os.path.join(flags.project_dir, 'subjects.txt')):
                    subject_data = read_subject_json(flags.project_dir)
                    subject_dict = iterate_through_dicts(subject_data)
                    subject = ask_user_for_subject(subject_dict)

                else:
                    subject = input("\nSubject of paper: ").strip()
                    add_entry_to_subject_json({subject: []}, flags.project_dir)

                year_written = input("\nYear Written: ").strip()
                first_author = input("\nFirst Author: ").strip()
                institute_of_origin = input("\nInsititute of origin: ").strip()

                # Use geolocation service to find the latitude and longitude of
                # the institute of the first author
                try:
                    geolocater = geocoders.GeoNames(username=flags.username)
                    location_info = geolocater.geocode(institute_of_origin)
                    longitude = location_info['lng']
                    latitude = location_info['lat']
                    break

                # If the GeoName server cannot be accessed for some reason, ask
                # user for manual input
                except HTTPError as e:
                    print("Request to GeoNames server failed due to ", e)
                    confirm_man_coord_input = ask_for_confirmation("Manually input lat/long?")

                    if confirm_man_coord_input:

                        while True:
                            latitude = input("\nLatitude of institute: ").strip()
                            longitude = input("\nLongitude of institute: ").strip()

                            # See if lat/lon input can be converted to a float. If it
                            # can, treat it as a valid entry. We can check later to
                            # see if the input lat/lon actually correlate to valid
                            # coordinates
                            # TODO: write some verification function to see if the lat/lon
                            #       input is actually valid
                            try:
                                float(latitude)
                                float(longitude)

                            except ValueError:
                                print("Error: input could not be converted to float")
                                print("Try Again")
                                pass

                        # Create dictionary of metadata to write to pdf
                        # if latitude and longitude were included by the user, place them
                        # in the metadata
                        meta_data = {
                            'subject': subject.replace(" ", "_").lower(),
                            'year_written': year_written,
                            'first_author': first_author,
                            'institute_of_origin': institute_of_origin,
                            'latitude': latitude,
                            'longitude': longitude,
                                    }

                    else:
                        # Create dictionary of metadata to write to pdf
                        meta_data = {
                            'subject': subject.replace(" ", "_").lower(),
                            'year_written': year_written,
                            'first_author': first_author,
                            'institute_of_origin': institute_of_origin,
                                    }

                # write metadata to pdf
                with open(pdf_to_read, 'rb') as pdf_in:
                    pdf_in = open(pdf_to_read, 'rb')
                    reader = PdfFileReader(pdf_in)
                    writer = PdfFileWriter()

                    writer.appendPagesFromReader(reader)
                    prev_metadata = reader.getDocumentInfo()
                    writer.addMetadata(prev_metada)

                    writer.addMetadata(meta_data)

                    with open(pdf_to_read, 'ab') as pdf_out:
                        writer.write(pdf_out)


def find_fitting_subject_directory(root_dir, subject, path):
        if not os.listdir(root_dir):
            print("\nNo subdirectories to list")
            print("\nCreate a subdirectory?")
            confirm = input("\n(Y/N): ")
            if confirm.lower == "n" or confirm.lower == "no":
                csv_addr = os.path.join(path, "{}.csv".format(subject))
                return csv_addr
            else:
                subdir_name = input("\nSubdirectory name?")
                path = os.path.join(path, subdir_name)
                os.makedirs(path)
                csv_addr = os.path.join(path, "{}.csv".format(subject))
                return csv_addr

            csv_addr = path + "/{}.csv".format(subject)
            return
        print("""\nWhich directory best describes the subject of
                the paper?""")
        iterator = 0
        addr_dict = {}
        for dirname, _, _ in os.walk(root_dir):
            addr_dict[iterator] = dirname
            print("\n{0}) {1}".format(iterator, dirname))
            iterator += 1
        addr_dict[iterator] = "New directory"
        print("\n{}) New Directory".format(iterator))
        choice = int(input("\nEnter choice: "))

        try:
            chosen_dir = addr_dict[choice]
            print("\nCreate csv in directory {}?".format(chosen_dir))
            confirm = input("\n(Y/N): ")
            if confirm.lower == "n" or confirm.lower == "no":
                print("\nLook in subdirectories?")
                press = input("\n(Y/N): ")
                if confirm.lower == "n" or confirm.lower == "no":
                    print("\nreninitiating choice loop")
                    return find_fitting_subject_directory(root_dir,
                                            subject, path)
                else:
                    path = os.path.join(path, chosen_dir)
                    return find_fitting_subject_directory(chosen_dir,
                                            subject, path)
            else:
                path = os.path.join(path, chosen_dir)
                csv_addr = os.path.join(path, "{}.csv".format(subject))
                return csv_addr
        except KeyError:
            ("\nError: given index not one of the choices provided")
            return find_fitting_subject_directory(root_dir, subject)



def ask_for_confirmation(message_str):
    """
       Helper function asking user for confirmation. Removes
       ALOT of redundant loops.
    """
    while True:
        confirmation = input(message_str + ' (y/n): ')

        if confirmation.lower() == 'y' or confirmation.lower() == 'yes':
            return 1

        elif confirmation.lower() == 'n' or confirmation.lower() == 'no':
            return 0

        else:
            print("Input not recognized")
            print("Try again")

def read_subject_json(project_dir):
    """
    Retrieves possible subject categories from json. User can then be prompted
    to select one of the possible subject catgories for a new paper entry, or
    to add a new subject if the current entries are insufficient to describe the
    paper
    """

    with open(os.path.join(project_dir, 'paper_subjects.txt'), 'rb') as subject_json:
        subject_data = json.load(subject_json)

    return subject_data

def add_entry_to_subject_json(subject_data, project_dir):
    """
    Adds new data dict to json file
    """
    with open(os.path.join(project_dir, 'paper_subjects.txt'), 'w') as subject_json:
        json.dump(subject_data, subject_json)

def list_subjects_and_ask_for_user_input(subject_data):
    """
    Allows user to choose fitting category for paper entry, or to add a new
    subject if the subject for the paper is not currently contained in the json
    """
    # As the subject data retrieved from the subject_json is a dict of dicts,
    # iterate down all dicts
    pass

def iterate_through_dicts(iter_dict, indiced_dict={}, index=None):
    """
    Recursive function to iterate through a dict of dicts. This will provide a new,
    indexed dict for the user
    """
    # Begin indexing at 'a'. The Decimal conversion is provided below:
    ascii_char_a = 97

    # DEBUG: Begin timer for debugging purposes
    t0 = time.time()
    for counter, [key, value] in enumerate(iter_dict.items()):

        # FOR DEBUGGING PURPOSES ONLY
        # Check timer to see if too much time has lapsed
        if t0 - time.time() > 15.0:
            print("TIMEOUT ERROR")
            return

        # If there is already a letter index provided, append a number
        # index
        if index:
            index = index + str(counter)


        # If there is no index provided (i.e, we are on the first pass in the
        # recursion, use a letter index
        else:

            # If we are past the 'z' character, begin double lettering scheme
            # (i.e., 'aa', 'ab', etc.)
            if counter > 25:

                # Get number of times we have past through the entire alphabet
                num_thru_alphabet = counter // 26

                # Get current position in alphabet we are at
                curr_position_in_alphabet = counter % 26

                # Based on last two calcs, determine our double index (should not be a need for
                # more than a double index, unless I compile > 26^2 papers in my lifetime, which
                # seems unlikely
                index = chr(ascii_char_a + num_thru_alphabet - 1) + chr(ascii_char_a + curr_position_in_alphabet)

            else:
                index = chr(ascii_char_a + counter)


        indiced_dict[index] = key
        # If the value this key points to is another dict, recurse to
        # index that dict
        if isinstance(value, dict):
            indiced_dict = iterate_through_dicts(value, indiced_dict=indiced_dict, index=index)

    return indiced_dict

def ask_user_for_subject(subject_dict):
    '''
    For a given paper, give user selection of possible subjects to categorize
    it under. If a relevant subject is not listed, allow the user to make one
    of their choosing and insert it in the json for future reference
    '''
    # Provide user a list of available subjects
    list_subjects()

    # Ask user if the subject they would like to categorize the paper
    # under is in the available dict
    confirmation = ask_for_confirmation("Is the subject area of this paper listed?")

    if confirmation:

        # Ask user for index of relevant subject
        while True:
            input_index = input("Provide index of relevant subject here: ")

            try:
                relevant_subject = subject_dict[input_index]
                break

            except KeyError:
                print("ERROR: input key not recognized")
                print("TRY AGAIN")

                # User may need to see list of available subjects again
                confirmation = ask_for_confirmation("Print list of subjects again?")

                if confirmation:
                    list_subjects()

                continue

    else:
        # Ask user for subject to categorize paper under
        relevant_subject = input("Enter subject to categorize paper under here: ")

        # Ask user if this subject is a subcategory of a subject already listed
        confirmation = ask_for_confirmation("Is this subject a subcategory of one already provided?")

        if confirmation:

            while True:
                print("Which subject should it be placed under?")
                list_subjects()

                parent_subject_idx = input("Choose index of parent subject: ")

                # If the index is recognized, index user input subject appropiately
                # First, check if the provided index is actually in the dict
                try:
                    parent_subject = subject_dict[parent_subject_idx]
                    break

                except KeyError:
                    print("Index not recognized. Try again.")

            ## Iterate through keys and values once again to see if there are
            ## sibling subjects under the parent
            #counter = 0
            #for key in subject_dict.keys():

            #    # Don't check indices shorter or same length as parent index
            #    # Don't check indices longer than parent index + 1. Those are
            #    # grandchildren of parent index
            #    if len(key) <= len(parent_subject_idx) or len(key) > len(parent_subject_idx):
            #        continue

            #    else:
            #        # Check to see if the beginning of the index starts with
            #        # the parent index, indicating that it is indexed under it
            #        if key[:-1] == parent_subject_idx:
            #            counter += 1

            ## Now we can finally index the chosen index
            #input_subject_idx = parent_subject_idx + str(counter)

            # ...and place the new subect where it belongs in the json
            add_new_entry_to_subject_json(relevant_subject, parent_subject=parent_subject)

        else:
            add_new_entry_to_subject_json(relevant_subject)

    # and after all that rigamarole, return chosen subject to user
    return relevant_subject

def list_subjects(subject_dict):
    """
    List entries for subject_dict.
    List all available subjects
    """
    for key, value in subject_dict.items():

        index_len = len(key)

        # Tab the number of levels the subject is down the directory
        # (indicated by the length of the list)
        tabs = (index_len - 1) * "\t"

        print("{0}{1}) {2}".format(tabs, key, value))

def add_new_entry_to_subject_json(subject, parent_subject=None):
    """
    Add new entry to subject json under parent, if there is one
    """
    if parent_subject:
        pass





#def retrieve_lat_n_lon_of_institute(institute_name):



#def find_fitting_subject_directory(subject, root_dir='.'):
#
#    for root, dirs, files in os.walk(root_dir):
#
#        for file_name in files:
#            if file_name == subject.lower():


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--project_dir', type=str, required=True,
                        help="Project root directory to begin paper search")

    parser.add_argument('--geonames_username', type=str,
                        help="Username for GeoNames server")

    flags = parser.parse_args()

    print("Initiating directory crawl")
    write_input_as_pdf_metadata(flags)
