import bcrypt

password = b"Admin@123"

# Generate salt and hash
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

print(hashed.decode())