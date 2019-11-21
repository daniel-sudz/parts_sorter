import os, sys, shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from subprocess import call

#delete exported-modal_folder
models_path =  os.path.join(str(Path(os.getcwd()).parents[0]))
config_path = os.path.join(models_path, "models")
try:
	shutil.rmtree(os.path.join(config_path,'fine_tuned_model'))
except: 
	print("export folder not existant, creating new one")
os.makedirs(os.path.join(config_path,'fine_tuned_model'))
os.chmod(os.path.join(config_path,'fine_tuned_model'),0o777) 

