#!/bin/bash

#
# Temporary script - will be removed in the future
#

./main -m ./models/13B/vicuna-1.1-q8_0.bin \
       -f ./prompts/chat-with-vicuna-v1.txt \
       -ins --ctx_size 2048 \
       -b 256 \
       --top_k 10000 \
       --temp 0.2 \
       --repeat_penalty 1.1 \
       -t 16
