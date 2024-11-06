# Cypress CYW20730 aka Broadcom BCM20730 aka Infeneon firmware hacking

# Tools

## tlvdecode.py

Parses OTA image and extracts TLVs. 

Usage:

`python3 ./tools/tlvdecode.py ./dumps/F.20730A2.CDDZHD042.K2_8887_OTA_V01.09_02C0.hex`

Example output:

```
Filename: ./F.20730A2.CDDZHD042.K2_8887_OTA_V01.09_02C0.hex

Decoded TLVs:
--------------------------------------------------
TLV #1 [2C0 - 2C5]:
  Type: 105 (0x69)
  Length: 2
  Value: 0
--------------------------------------------------
TLV #2 [2C5 - 2C9]:
  Type: 24 (0x18)
  Length: 1
  Value: 0
--------------------------------------------------
TLV #3 [2C9 - 2CE]:
  Type: 128 (0x80)
  Length: 2
  Value: 53255
--------------------------------------------------
TLV #4 [2CE - 2F1]:
  Type: 196 (0xC4)
  Length: 32
  Value: 1c026000d806000020026000d806000024026000d80600004403600020000000

```