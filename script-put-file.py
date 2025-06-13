import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_name, bucket, object_name=None):
    """
    Uploads a file to an S3 bucket

    :param file_name: Path to the file to upload
    :param bucket: Name of the S3 bucket
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if the file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

# Example usage
if __name__ == "__main__":
    # Name of the file you want to upload
    file_name = '10037_20240718_00003P-pag1'
    # Name of the bucket
    bucket_name = 'fap-commons-pro-a5-generated-lists-storage'
    # S3 object name (optional)
    object_name = 'closed_P_list/10037_20240718_00003P-pag1'

    # Call the function to upload the file
    upload_to_s3(file_name, bucket_name, object_name)