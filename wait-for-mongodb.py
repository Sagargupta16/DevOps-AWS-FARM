#!/usr/bin/env python3
import time
import pymongo
import os
import sys

def wait_for_mongodb(mongodb_url, timeout=30):
    """Wait for MongoDB to be ready"""
    print(f"Waiting for MongoDB at {mongodb_url}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=2000)
            # Try to get server info to test connection
            client.server_info()
            print("MongoDB is ready!")
            client.close()
            return True
        except Exception as e:
            print(f"MongoDB not ready yet: {e}")
            time.sleep(2)
    
    print(f"Timeout waiting for MongoDB after {timeout} seconds")
    return False

if __name__ == "__main__":
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    if not wait_for_mongodb(mongodb_url):
        sys.exit(1)
