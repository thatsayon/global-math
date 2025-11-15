import random

def generate_room_code(name):
    # Extract first 4 uppercase letters from name, fallback if too short
    prefix = ''.join([c for c in name.upper() if c.isalpha()])[:4]
    number = random.randint(100, 999)
    code = f"{prefix}-{number}"
    return code
