#!/bin/bash

WAV_FILE=$1
TAG=$2

#Run command
bash ~/saigen/tools/speech_recognition/decode_chain_callbi.sh --sr 8000 --num-channels 1 --tag $TAG --dir-work /tmp/zulu ~/models/nb_zu_gen_v2.1 ~/models/nb_zu_gen_v2.1/exp/chain_cleaned/tdnn1g_sp/graph_nb_zu_gen_v2.1_gen_2020-03-06 $WAV_FILE

exit $?