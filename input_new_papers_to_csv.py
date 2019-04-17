#!/home/peter/miniconda3/envs/tensorflow python

import csv
import os


# Custom modules
import world_map_plot as wmp

def input_stuff_to_paper_csv(root_dir='.'):

    subject = input("\nSubject of paper: ").strip()
    paper_title = input("\nName of paper: ").strip()
    year_written = input("\nYear Written: ").strip()
    first_author = input("\nFirst Author: ").strip()
    institute_of_origin = input("\nInsititute of origin: ").strip()
    latitude = input("\nLatitude of institute: ").strip()
    longitude = input("\nLongitude of institute: ").strip()

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

#def retrieve_lat_n_lon_of_institute(institute_name):



#def find_fitting_subject_directory(subject, root_dir='.'):
#
#    for root, dirs, files in os.walk(root_dir):
#        
#        for file_name in files:
#            if file_name == subject.lower():


if __name__ == '__main__':
    root_dir = '.'
    input_stuff_to_paper_csv()
