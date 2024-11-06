from intelhex import IntelHex
from dataclasses import dataclass
from typing import List, Any
import struct

@dataclass
class TLV:
    type: int
    length: int
    value: bytes
    offset_start: int
    offset_end: int

def read_hex_file(filename: str) -> bytes:
    """Read Intel HEX file using intelhex library and return binary data."""
    ih = IntelHex(filename)
    # Get start and end addresses of the data
    start_addr = ih.minaddr()
    end_addr = ih.maxaddr()

    # Convert to bytes
    return bytes(ih.tobinarray(start=start_addr, end=end_addr))

def decode_tlvs(data: bytes) -> List[TLV]:
    """Decode TLV structures from binary data."""
    tlvs = []
    offset = 704

    while offset < len(data):
        #print(data[offset])
        # Ensure we have enough bytes for type and length
        if offset + 3 > len(data):
            break

        tlv_offset_start = offset

        # Extract type (1 byte)
        tlv_type = data[offset]
        offset += 1

        # Extract length (2 bytes)
        tlv_length = int.from_bytes(data[offset:offset+2], byteorder='little')
        offset += 2

        # Ensure we have enough bytes for value
        if offset + tlv_length > len(data):
            break

        tlv_offset_end = offset + tlv_length

        # Extract value
        tlv_value = data[offset:offset+tlv_length]
        offset += tlv_length

        tlvs.append(TLV(tlv_type, tlv_length, tlv_value, tlv_offset_start, tlv_offset_end))

    return tlvs

def format_tlv_value(tlv: TLV) -> Any:
    """Format TLV value based on type and length."""
    try:
        if tlv.length == 1:
            return int.from_bytes(tlv.value, byteorder='big')
        elif tlv.length == 2:
            return struct.unpack('>H', tlv.value)[0]
        elif tlv.length == 4:
            return struct.unpack('>I', tlv.value)[0]
        elif tlv.length == 8:
            return struct.unpack('>Q', tlv.value)[0]
        else:
            # Try to decode as UTF-8 string, fall back to hex
            try:
                return tlv.value.decode('utf-8')
            except UnicodeDecodeError:
                return tlv.value.hex()
    except struct.error:
        return tlv.value.hex()

def main():
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hex_file>")
        sys.exit(1)

    try:
        input_file = sys.argv[1]
        # Parse HEX file using intelhex
        binary_data = read_hex_file(sys.argv[1])

        print("Filename: " + input_file)

#
#         with open(input_file + ".bin", "wb") as binary_file:
#             # Write bytes to file
#             binary_file.write(binary_data)
#             binary_file.close()
#
#
        #print(binary_data.hex(), sep='\n')

        # Decode TLVs
        tlvs = decode_tlvs(binary_data)

        # Print results
        print("\nDecoded TLVs:")
        print("-" * 50)
        for i, tlv in enumerate(tlvs, 1):
            formatted_value = format_tlv_value(tlv)
            print(f"TLV #{i} [{tlv.offset_start:02X} - {tlv.offset_end:02X}]:")
            print(f"  Type: {tlv.type} (0x{tlv.type:02X})")
            print(f"  Length: {tlv.length}")
            print(f"  Value: {formatted_value}")
            print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
