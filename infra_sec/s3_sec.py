import boto3
from botocore.exceptions import ClientError

def check_bucket_public_access(s3_client, bucket_name):
    """
    Check if a bucket has public access.

    Args:
    - s3_client: An instance of boto3 S3 client.
    - bucket_name: Name of the S3 bucket.

    Returns:
    - True if the bucket is public, False otherwise.
    """
    try:
        # Check if block public access is set
        response_block_public_access = s3_client.get_public_access_block(Bucket=bucket_name)
        block_public_acls = response_block_public_access['PublicAccessBlockConfiguration']['BlockPublicAcls']
        block_public_policy = response_block_public_access['PublicAccessBlockConfiguration']['BlockPublicPolicy']

        # Check if policies allow public access
        response_policy_status = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        is_public = response_policy_status['PolicyStatus']['IsPublic']

        # Check ACLs for public grants
        response_acl = s3_client.get_bucket_acl(Bucket=bucket_name)
        for grant in response_acl['Grants']:
            grantee = grant.get('Grantee', {})
            grantee_type = grantee.get('Type')
            if grantee_type == 'Group':
                uri = grantee.get('URI')
                if uri in ('http://acs.amazonaws.com/groups/global/AllUsers', 'http://acs.amazonaws.com/groups/global/AuthenticatedUsers'):
                    return True

        if is_public and not (block_public_acls and block_public_policy):
            return True
                                        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            return False  # Bucket policy doesn't exist, so it's not public
        else:            
            raise e

    return False

def block_bucket_public_access(s3_client, bucket_name):
  """
  Enable Block Public Access for a bucket.

  Args:
    s3_client: An instance of boto3 S3 client.
    bucket_name: Name of the S3 bucket.
  """
  s3_client.put_public_access_block(
    Bucket=bucket_name,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
  )

def get_all_buckets(s3_client):
  """
  Retrieves a list of all S3 buckets in the account, handling pagination.

  Args:
      s3_client: An instance of boto3 S3 client.

  Returns:
      A list of bucket dictionaries or an empty list if there are no buckets.
  """
  buckets = []
  marker = None
  while True:
    kwargs = {'MaxItems': 1000}  # Limit results per request (optional)
    if marker:
      kwargs['Marker'] = marker
    response = s3_client.list_buckets(**kwargs)
    buckets.extend(response.get('Buckets', []))
    marker = response.get('NextMarker')
    if not marker:
      break
  return buckets


def check_and_block_public_access(s3_client):
  """
  Iterates through all S3 buckets and extracts names for potential future use.

  Args:
      s3_client: An instance of boto3 S3 client.
  """
  buckets = get_all_buckets(s3_client)
  for bucket in buckets:
    # Extract bucket name from the dictionary
    bucket_name = bucket.get('Name')
    print(f"Bucket Name: {bucket_name}")

    try:
      if check_bucket_public_access(s3_client, bucket_name):
        print(f"Bucket {bucket_name} has public access. Enabling Block Public Access...")
        block_bucket_public_access(s3_client, bucket_name)
        print(f"Block Public Access enabled for bucket {bucket_name}.")
      else:
        print(f"Bucket {bucket_name} does not have public access.")
    except ClientError as e:
      print(f"Error checking bucket {bucket_name}: {e}")


if __name__ == "__main__":
  s3_client = boto3.client('s3')
  check_and_block_public_access(s3_client)