#!/bin/bash
cd .. 
cd models/research
protoc object_detection/protos/*.proto --python_out=.
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
cd ..
cd .. 
cd parts
python live.py
cd ..
cd models/train 
ls -t | grep model.ckpt | grep .index
VAR="$(ls -t | grep model.ckpt | grep .index)"
printf "\n\nCHOSEN FILE BASED ON DATE CREATED: \n"
VAR1=$(echo $VAR | awk '{ print $1 }')
echo $VAR1
VAR1=$(echo ${VAR1%??????})
echo $VAR1
cd ..
sleep 2
python research/object_detection/export_inference_graph.py --input_type image_tensor --pipeline_config_path config.txt --trained_checkpoint_prefix  train/$VAR1 --output_directory fine_tuned_model
python research/object_detection/live.py
