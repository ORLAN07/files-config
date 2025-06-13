import boto3
from botocore.exceptions import NoCredentialsError

def download_from_s3(bucket, object_name, file_name):
    """
    Downloads a file from an S3 bucket

    :param bucket: Name of the S3 bucket
    :param object_name: Name of the object in S3
    :param file_name: Local path where the file will be saved
    :return: True if the file was downloaded, else False
    """
    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        s3_client.download_file(bucket, object_name, file_name)
        print(f"File {object_name} downloaded from {bucket} to {file_name}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

# Example usage
if __name__ == "__main__":
    # Name of the S3 bucket
    bucket_name = 'fap-commons-pro-a5-generated-lists-storage'
    # Name of the object in S3
    object_name = 'closed_P_list/10037_20240718_00001P-pag1'
    # Local path where the file will be saved
    file_name = '10037_20240718_00001P-pag1'

    # Call the function to download the file
    download_from_s3(bucket_name, object_name, file_name)