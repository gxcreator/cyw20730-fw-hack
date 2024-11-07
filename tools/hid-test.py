from __future__ import print_function

import hid
import time

TARGET_VID : int= 0x05AC
TARGET_PID : int = 0x024F
TARGET_USAGE : int = 3
TARGET_USAGE_PAGE :int = 1

target_path : str = None

# enumerate USB devices
def find_device_path(vid, pid, usage, usage_page):
    for d in hid.enumerate():
        if d['vendor_id'] != TARGET_VID or d['product_id'] != TARGET_PID or d['usage'] != TARGET_USAGE or d['usage_page'] != TARGET_USAGE_PAGE:
            continue
        print("Device found:")
        keys = list(d.keys())
        keys.sort()
        for key in keys:
            print("%s : %s" % (key, d[key]))
        print()
        target_path = d['path']
        return target_path

def open_hid_device(path):
    # try opening a device, then perform write and read
    h = hid.device()
    try:
        print("Opening the device")
        h.open_path(target_path)

        print("Manufacturer: %s" % h.get_manufacturer_string())
        print("Product: %s" % h.get_product_string())
        print("Serial No: %s" % h.get_serial_number_string())

        # enable non-blocking mode
        #h.set_nonblocking(1)
        return h
    except IOError as ex:
        print(ex)
        return None

def hid_txrx(h, data):
    # write some data to the device
    print("TX => " + "".join(["%02x " % x for x in data]))
    h.write(data)

    # wait
    time.sleep(0.05)

    while True:
        d = h.read(64)
        if d:
            # print d in hex as hex numbers:
            print("RX <= " + "".join(["%02x " % x for x in d]))
            if d[0] == 0x01:
                continue
            return d
        else:
            break

def itonhid_get_name(h):
    print("Reading name...")
    return hid_txrx(h, [0xb2, 0x24])

def itonhid_get_version(h):
    print("Reading version...")
    return hid_txrx(h, [0xb2, 0x25])

def itonhid_get_serial(h):
    print("Reading serial...")
    return hid_txrx(h, [0xb2, 0x40])            

def itonhid_set_dfu_mode(h, mode):
    print("Setting DFU mode...")
    return hid_txrx(h, [0xb2, 0x26, mode])

def itonhid_get_read_mem(h, addr, length):
    print("Reading MEM...")
    addr_bytes = addr.to_bytes(2, byteorder='little')
    length_bytes = length.to_bytes(1, byteorder='little')
    return hid_txrx(h, [0xb2, 0x29, addr_bytes[0], addr_bytes[1], length_bytes[0]])

def device_read_mem(h, addr, length):
    hid_reply = itonhid_get_read_mem(h, addr, length)
    if hid_reply is None:
        return None
    if len(hid_reply) < 6 + length + 2:
        print("Invalid reply length: %d" % len(hid_reply))
        return None
    
    if hid_reply[0] != 0xb1:
        print("Invalid reply code: %02x" % hid_reply[0])
    
    rcv_length = hid_reply[3]
    if rcv_length != length:
        print("Invalid reply length: %02x != %02x" % (rcv_length, length))
        return None
    rcv_addr = hid_reply[4] + (hid_reply[5] << 8)    
    if rcv_addr != addr:
        print("Invalid reply address: %04x != %04x" % (rcv_addr, addr))
        return None
    data = hid_reply[6:6+length]
    chksum = hid_reply[6+length:6+length+2]
    # calculate checksum
    element_sum = sum(data) + 0x20
    # convert sum to 2 bytes
    sum_bytes = bytearray(element_sum.to_bytes(2, byteorder='little'))

    if sum_bytes != bytes(chksum):
        print("Checksum error: %02x %02x != %02x %02x" % (sum_bytes[0], sum_bytes[1], chksum[0], chksum[1]))
        return None
    else:
        print("Checksum OK: %02x %02x" % (chksum[0], chksum[1]))
        return data


data = [0x69, 0x02, 0x00, 0x00, 0x00, 0x18, 0x01, 0x00, 0x00, 0x80, 0x02, 0x00, 0xd0, 0x07, 0xc4, 0x20, 0x00, 0x1c, 0x02, 0x60, 0x00, 0xd8, 0x06, 0x00, 0x00, 0x20, 0x02, 0x60, 0x00, 0xd8, 0x06, 0x00]

# # Calculate sum of data bytes:
# element_sum = sum(data)
# # convert sum to 2 bytes
# sum_bytes = element_sum.to_bytes(2, byteorder='little')
# print("Sum: %02x %02x" % (sum_bytes[0] + 0x20, sum_bytes[1]))
# exit()


print("Starting...")
print("Looking for device...")
target_path = find_device_path(TARGET_VID, TARGET_PID, TARGET_USAGE, TARGET_USAGE_PAGE)

if target_path is None:
    print("Device not found")
    exit()

print("Opening the device...")
h = open_hid_device(target_path)

if h is None:
    print("Failed to open the device")
    exit()

# reply = itonhid_get_name(h)
# assert reply is not None

# reply = itonhid_get_version(h)
# assert reply is not None

reply = itonhid_get_serial(h)
assert reply is not None

reply = itonhid_set_dfu_mode(h, 2)
assert reply is not None

# read the first 0x500 bytes of the EEPROM
FLASH_SIZE= 32768 #32KB
FLASH_CHUNK_SIZE = 0x20 # Reading by 32 bytes per packet

eeprom_data = []

for i in range(0, FLASH_SIZE, FLASH_CHUNK_SIZE):
    print("Read: %d/%d" % (i, FLASH_SIZE))
    reply = device_read_mem(h, i, FLASH_CHUNK_SIZE)
    assert reply is not None
    eeprom_data.extend(list(reply[:FLASH_CHUNK_SIZE]))


#reply = itonhid_get_read_mem(h, 0x0000, 0x10)

reply = itonhid_set_dfu_mode(h, 0)

#print("FLASH data:")

# Beatifully print byte data as hex with ascii:
# for chunk in eeprom_data:
#     print("".join(["%02x " % x for x in chunk]) + "  " + "".join([chr(x) if x >= 32 and x <= 126 else '.' for x in chunk]))

print("DATA size: %d" % len(eeprom_data))

# Write to file
with open("backup.bin", "wb") as f:
    f.write(bytearray(eeprom_data))
    f.flush()
    f.close()

# print("Closing the device")
# h.close()

# except IOError as ex:
#     print(ex)
#     print("hid error:")
#     print(h.error())


print("Done")
