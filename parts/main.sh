#!/usr/bin/env bash
cd .. 
cd models/research
protoc object_detection/protos/*.proto --python_out=.
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
python object_detection/builders/model_builder_test.py
printf "\n \n TENSORFLOW WORKING NORMALLY IF TESTS PASSED \n \n"
printf "Waiting 2 seconds before proceeding \n"
sleep 1 
printf "Waiting 1 second before proceeding \n"
sleep 1

cd ..
cd ..
cd parts
python path_parser.py
cd ..
cd models
CUDA_VISIBLE_DEVICES=0
python research/object_detection/model_main.py -model_dir=train --logtostderr --train_dir=train --pipeline_config_path=config.txt
