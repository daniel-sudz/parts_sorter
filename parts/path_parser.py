import os, sys, shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from subprocess import call

# APPEND python path, import tensorflow, and return to directory
current_path = os.getcwd()
os.chdir("/home/sudz/Desktop/vex_parts-v3/models")
sys.path.append("research")
sys.path.append("research\\object_detection\\utils")
import tensorflow as tf
os.chdir(current_path)
 
#print("enter the xmls folder path")
#f_path = str(input())

def renaming(f_path):	s
	print("adjusting annotated files based on folder structure")
	final_path = os.path.join(os.getcwd(), f_path)
	image_dir = os.path.join(str(Path(final_path).parents[1]), "compress")


	for filename in os.listdir(final_path):
		if filename.endswith(".xml") or filename.endswith(".xml"):
			current_file = os.path.join(final_path, filename)
			correct_file_name = os.path.join(image_dir, filename)
			xml_tree = ET.parse(current_file)
			xml_root = xml_tree.getroot()
			found_path = xml_root.find('path')

			found_path = xml_root.find('path')
			found_path.text = correct_file_name.replace('xml','jpg')
			print(found_path.text)
			print(current_file)
			xml_tree.write(current_file)

		continue

def comb_tfrecord(tfrecords_path, save_path, batch_size=128):
        with tf.Graph().as_default(), tf.Session() as sess:
            ds = tf.data.TFRecordDataset(tfrecords_path).batch(batch_size)
            batch = ds.make_one_shot_iterator().get_next()
            writer = tf.python_io.TFRecordWriter(save_path)
            while True:
                try:
                    records = sess.run(batch)
                    for record in records:
                        writer.write(record)
                except tf.errors.OutOfRangeError:
                    break
train_records = [] 
eval_records = []
label_map_string = ""

current_path = os.getcwd()
current_dirs = os.listdir(current_path)
for paths in current_dirs:
	target = os.path.join(paths, 'anot/xmls')
	if (os.path.isdir(target)):
		#Create train val numbering based on how many xmls files are present
		fout = open(os.path.join(paths, 'anot/trainval.txt'),'w+')
		for i in range(1,len(os.listdir(os.path.join(paths, 'anot/xmls')))):
			fout.write(str(i)+'\n')
		fout.close()

		#Run xmls target jpg renamer since labelImg does not support relative paths aparrantly 
		renaming(target)

		#Generate TF records for each part folder 
		current_path = os.getcwd()
		os.chdir(paths)
		call(["python", os.path.join('create_tf_record.py')])
		os.chdir(current_path)
		
		#Merge individual label_map files into train dir
		label_map_dir = os.path.join(paths, 'anot/label_map.pbtxt')
		if (os.path.isfile(label_map_dir)):
			curr_map = open(label_map_dir, "r")
			read = curr_map.read() 
			label_map_string += read 
			

	#Add found tf_records to final tf_record merge
	train_record_path = os.path.join(paths, 'train.record')
	val_record_path = os.path.join(paths, 'val.record')
	if os.path.isfile(train_record_path):
		train_records.append(train_record_path)
	if os.path.isfile(val_record_path):
		eval_records.append(val_record_path)
	

# Merge TF_records: note: not compatible with tensorflow version 2.x !depreceation warning
print(train_records)
print(eval_records)
#comb_tfrecord(train_records, 'train.record')
#comb_tfrecord(eval_records, 'val.record')

#create config file dynamically
fout1 = open('config/part1.txt','r').read()
fout2 = open('config/part2.txt','r').read()
fout3 = open('config/part3.txt','r').read()

merger_train_record = ""
merger_val_record = ""
for path in train_records:
	if (path == train_records[-1]):
		merger_train_record += '"' + os.path.join(os.getcwd(),path) + '"'
	else:
		merger_train_record += '"' + os.path.join(os.getcwd(),path) + '",'
for path in eval_records:
	if (path == eval_records[-1]):
		merger_val_record +=  '"' + os.path.join(os.getcwd(),path) + '"'
	else:
		merger_val_record +=  '"' + os.path.join(os.getcwd(),path) + '",'
fout = open('config.txt', 'w')
fout.write(fout1 + '[' + merger_train_record + ']' + fout2 + '[' + merger_val_record + ']' + fout3)
fout.close()
 

#Move generated tf_combined to models folder
models_path =  os.path.join(str(Path(os.getcwd()).parents[0]))
config_path = os.path.join(models_path, "models")
try:
	os.remove(os.path.join(config_path,'config.txt'))
except: 
	print("config file is not existant, skipping")
shutil.move('config.txt', config_path)

#write label_map.pbtxt merge
label_map_dir = os.path.join(models_path, 'models/annotations/label_map.pbtxt')
write_map = open(label_map_dir, 'w')
write_map.write(label_map_string)
print(label_map_string)
print("DONE")

#initiate training 
#train_func = 'python research/object_detection/model_main.py -model_dir=train --logtostderr --train_dir=train --pipeline_config_path=config.txt'
#os.chdir(os.path.join(models_path, "models"))
#print(os.getcwd())
#import subprocess
#subprocess.run(["python", "research/object_detection/model_main.py", "-model_dir=train", "--logtostderr", "--train_dir=train", "--pipeline_config_path=config.txt"])
#os.system(train_func)








