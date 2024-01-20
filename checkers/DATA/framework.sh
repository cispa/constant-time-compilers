#!/bin/bash
source "${DATA_ROOT}/data.sh"
source "${DATA_COMMON}/DATA_init.sh"
export FRAMEWORK=ctccp
export PHASE1_TRACES=${DATA_RUN_COUNT} 
export PHASE2_FIXEDKEYS=3
export PHASE2_TRACES=10
export PHASE3_TRACES=20
export PINTOOL_ARGS=""

export TESTDIR=${PWD}/
export RESULTDIR=${PWD}/results
export BASEDIR=$(pwd)
export SPECIFIC_LEAKAGE_CALLBACK=${DATA_LEAKAGE_MODELS}/sym_byte_value.py

function cb_prepare_framework {
  :
}

function cb_genkey {
  dd if=/dev/urandom of=$1 bs=255 count=1 > /dev/null 2> /dev/null
  RES=$((RES + $?))
}

function cb_pre_run {
  log_verbose "running with key $1"
}

function cb_run_command {
  echo "${BINARY} ${CLASS_SEED} $1"
}

function cb_post_run {
  :
}

function cb_prepare_algo {
  ALGO=$1
  # key bits
  PARAM=$2
  SHIFT=$((SHIFT+1))
  CLASS_SEED=$PARAM
  WORKDIR="$FRAMEWORK/$ALGO/$PARAM"
}
DATA_parse "$@"
rm -rf $RESULTDIR