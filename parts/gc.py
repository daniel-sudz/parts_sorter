import random, xml.etree.ElementTree as ET
import os, sys, shutil, warnings
from pathlib import Path
from subprocess import call

## Modify this as needed ##########################################################################
## Sets the root directory of the project to the path up a dir from gc.py ##
ROOT_DIRECTORY = str(Path(os.getcwd()).parents[0])
PROJECT_FOLDER = 'parts_sorter'
GS_BUCKET = 'gs://sudz'
####################################################################################################
## This is the split between training/val/test, it is completely random and not garunteed to be exact 
TRAINING_SPLIT = 0.8
VALIDATE_SPLIT = 0.1
TEST_SPLIT = 0.1 
#####################################################################################################
## Define to enable forced debug output or not
IS_DEBUG_OVERIDE = 0 
#####################################################################################################

#Decides if we should print debug print statements or not
print("ENTER true for debug overide or false for non overide")
if (input() in {True,'true','True','TRUE','true', '1'}): 
    IS_DEBUG_ENABLED = 1
    if (IS_DEBUG_OVERIDE == 0):
        print ("DEBUG MODE IS ENABLED")
else: 
    print ("DEBUG MODE IS DISABLED")
    IS_DEBUG_ENABLED = 0
if (IS_DEBUG_OVERIDE): 
    print("DEBUG OVERRIDE IS ENABLED") 
def dprint(printing_output): 
    if (IS_DEBUG_OVERIDE):
        print(printing_output)
    else: 
        if(IS_DEBUG_ENABLED):
            print(printing_output)

def xml_to_csv_extraction(xml_file):
    csv_meta_data = []
    xml_tree = ET.parse(xml_file)
    xml_root = xml_tree.getroot()
    xml_objects = xml_root.findall('object')

    for found_object in xml_objects:
        for dimension in list(xml_root.find('size')):
            if dimension.tag == 'width':
                width = dimension.text
            if dimension.tag == 'height':
                height = dimension.text
        picture_path = xml_root.find('path').text
        for node1 in found_object.getiterator():
            if node1.tag == 'name':
                object_name = node1.text
            if node1.tag == 'bndbox':
                for node2 in list(node1):
                    if node2.tag == 'xmin':
                        xmin = node2.text
                    if node2.tag == 'xmax':
                        xmax = node2.text
                    if node2.tag == 'ymin':
                        ymin = node2.text
                    if node2.tag == 'ymax':
                        ymax = node2.text

                csv_meta_data.append(
                    [[object_name, width, height, picture_path], [xmin, xmax, ymin, ymax]])
                    # print (node2.tag, node2.attrib, node2.text)
    return csv_meta_data

def datasplit():
    randfloat = random.uniform(0, 1)
    if (randfloat < TRAINING_SPLIT): 
        return "TRAIN"
    if (randfloat > TRAINING_SPLIT and randfloat < (VALIDATE_SPLIT + TRAINING_SPLIT)):
        return "VALIDATE"
    if (randfloat > (TRAINING_SPLIT+ VALIDATE_SPLIT)): 
        return "TEST"

def xml_to_csv_compiler(extracted):
    for element in extracted: 
        element_width = element[0][1]
        #print('element width' +  '\n' + element_width)
        element_height = element[0][2]
        #print('element height' + '\n' + element_height)
        #print(int(element[1][0]))
        x_relative_min = str(round(int(element[1][0])/int(element_width),3)) 
        x_relative_max = str(round(int(element[1][1])/int(element_width),3))
        y_relative_min = str(round(int(element[1][2])/int(element_height),3))
        y_relative_max = str(round(int(element[1][3])/int(element_height),3))

        element_path = element[0][3]
        element_label = element[0][0]
        element_catagory = datasplit()
        csv_line = element_catagory + ',' + element_path + ',' + element_label + ',' + x_relative_min + ',' + y_relative_min + ',,,' + x_relative_max + ',' + y_relative_max + ',,'
        #print(csv_line)
        return csv_line

def xml_to_csv_linker(xml_target):
    csv_lines_for_dir = []
    xml_files_for_dir = os.listdir(xml_target)
    for xml_file in xml_files_for_dir:
        if (xml_file.endswith('xml')):
            full_xml_path = os.path.join(xml_target, xml_file)  
            xml_extracted_metadata = xml_to_csv_extraction(full_xml_path)
            xml_csv_line = str(xml_to_csv_compiler(xml_extracted_metadata))
            dprint(xml_csv_line)
            csv_lines_for_dir.append(xml_csv_line)
    return csv_lines_for_dir

def renaming(f_path):
    dprint("adjusting annotated files based on folder structure")
    final_path = os.path.join(os.getcwd(), f_path)
    image_dir = os.path.join(str(Path(final_path).parents[1]), "compress")

    for filename in os.listdir(final_path):
        if filename.endswith(".xml") or filename.endswith(".xml"):
            current_file = os.path.join(final_path, filename)
            correct_file_name = os.path.join(image_dir, filename)
            try:
                xml_tree = ET.parse(current_file)
            except: 
                print('FAILED TO PARSE FILE ' + current_file + '\n')
                print('Sometimes this happens for no reason, try rerunning the program or restoring xml files from github. The files may be corrupted. Verify the file in question')
            xml_root = xml_tree.getroot()
            found_path = xml_root.find('path')

            found_path = xml_root.find('path')
            #found_path.text = correct_file_name.replace('xml','jpg')
            gc_PATH = os.path.relpath(correct_file_name, ROOT_DIRECTORY)
            gc_PATH = os.path.join(GS_BUCKET, PROJECT_FOLDER, gc_PATH).replace("\\","/").replace('xml','jpg')
            found_path.text = gc_PATH
            dprint(found_path.text)
            dprint(gc_PATH)
    
            #dprint(current_file)
            xml_tree.write(current_file)
        continue

current_path = os.getcwd()
current_dirs = os.listdir(current_path)
for paths in current_dirs:
    target = os.path.join(paths, 'anot/xmls')
    if (os.path.isdir(target)):
        # Run xmls target jpg renamer since labelImg does not support relative paths aparrantly 
        renaming(target)

all_generated_csv_lines = []
for paths in current_dirs:
    target = os.path.join(paths, 'anot/xmls')
    if (os.path.isdir(target)):
        # Runs xmls converter to google automl format  
        csv_lines_generated = xml_to_csv_linker(target)
    for every_csv_line in csv_lines_generated:
        all_generated_csv_lines.append(every_csv_line)
#dprint(all_generated_csv_lines)

fout = open("labels.csv", "w")
for final_generated_csv_lines in all_generated_csv_lines:
    if (final_generated_csv_lines != all_generated_csv_lines[-1]):
        fout.write(final_generated_csv_lines + '\n')
    else: 
        fout.write(final_generated_csv_lines + '\n')
fout.close()

