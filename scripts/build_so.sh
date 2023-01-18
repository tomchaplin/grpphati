#!/bin/bash
# To build the sys.so that EireneBackend expects, we follow a 2-step process
# 1. Use Julia 1.6 to build a system image which contains a precomplied version of
#    * Eirene
#    * functions that EireneBackend will use
# 2. Use julia.sysimage to patch that system image, incorporating necessary PyCall modules
# Usage:
# Change $JULIA_PATH to point to your Julia 1.6 binary
# This assumes a hatch setup with the optional [eirene] depdendency installed in an enviornment called eirene
# You may want to change this by removing the eirene:
# You could also just run each of these commands by hand

JULIA_PATH="/home/tom/Downloads/julia/julia-1.6.7/bin/julia"
$JULIA_PATH build_eirene_sys.jl
hatch run eirene:python -m julia.sysimage \
  --julia $JULIA_PATH --base-sysimage "scripts/eirene_sys.so" patched_sys.so
