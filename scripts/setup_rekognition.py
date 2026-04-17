import boto3
import sys

rekognition = boto3.client('rekognition')
COLLECTION_ID = 'attendance-collection'

def create_collection():
    try:
        print(f"Creating collection: {COLLECTION_ID}")
        rekognition.create_collection(CollectionId=COLLECTION_ID)
        print("Success.")
    except rekognition.exceptions.ResourceAlreadyExistsException:
        print("Collection already exists.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_collection()
