# sih-2023

# Blockchain and Biometric based Identity Verification System

1. Backend has 2 Running servers
    - DirectUS that has the entire data (encrypted)
    - Blockchain uploader, that uploads the verification record

2. Frontend has a single file that does the following verifications
    - Scan QR Code to extract ID if it exists
    - If ID is valid , check Face Similarity
    - If Face is not matching , check Fingerprint
    - On valid checks , mark student as present for the exam