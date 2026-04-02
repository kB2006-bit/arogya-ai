#!/usr/bin/env python3
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get the password hash from MongoDB
stored_hash = "$2b$12$nTbNzW5bp3q9.3AUXECz8ewLRmenaCLY3jsbC1AkmYQG/nzA3lAPS"
test_password = "Arogya123!"

# Test if password matches
result = pwd_context.verify(test_password, stored_hash)
print(f"Password verification result: {result}")

if result:
    print("✅ Demo user password is correct!")
else:
    print("❌ Demo user password is INCORRECT!")
    print("Generating new hash...")
    new_hash = pwd_context.hash(test_password)
    print(f"New hash: {new_hash}")
