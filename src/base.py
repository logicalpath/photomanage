import base64

# Base64 encoded data
base64_data = "AAAAFGZ0eXBxdCAgAAACAHF0ICAAAAAId2lkZQAC2CxtZGF0AAACrgYF//"

# Add padding characters if needed
padding_len = len(base64_data) % 4
if padding_len != 0:
    base64_data += '=' * (4 - padding_len)

# Decode the Base64 data
decoded_data = base64.b64decode(base64_data)

# Analyze the decoded data
if decoded_data.startswith(b'\x00\x00\x00\x14ftyp'):
    print('The video format is MOV (QuickTime)')
else:
    print('Unknown video format')