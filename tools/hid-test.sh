#!/bin/bash

HIDAPI_TOOL="/usr/bin/hidapitester"

if [ ! -f $HIDAPI_TOOL ]; then
    echo "Error: $HIDAPI_TOOL not found"
    exit 1
fi

TARGET_VIDPID="05AC/024F"
TARGET_USAGE="03"
TARGET_USAGE_PAGE="01"

HID_TARGET_OPTS="--vidpid $TARGET_VIDPID --usage $TARGET_USAGE --usagePage $TARGET_USAGE_PAGE"

# Run the HIDAPI tester tool
#$HIDAPI_TOOL $HID_TARGET_OPTS -l 20 --open --send-output 0xb2,0x24 --read-input

# Function that queries the HIDAPI tester tool for the device's input report
# Input parameter is bytes for --send-output
hid_tester_query(){
    $HIDAPI_TOOL $HID_TARGET_OPTS -q -l 20 --open --send-output $1 --read-input
}

echo -e "Device name:\n"
echo "$(hid_tester_query 0xb2,0x24)"  | xxd -r -a

echo -e "\nFw number:"
hid_tester_query 0xb2,0x25

