import unittest
from unittest.mock import MagicMock

from infra_sec import s3_sec

class TestBucketPublicAccess(unittest.TestCase):

    def test_bucket_not_public(self):
        s3_client = MagicMock()
        s3_client.get_public_access_block.return_value = {
            'PublicAccessBlockConfiguration': {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        }
        s3_client.get_bucket_policy_status.return_value = {
            'PolicyStatus': {
                'IsPublic': False
            }
        }
        s3_client.get_bucket_acl.return_value = {
            'Grants': [
                {
                    'Grantee': {
                        'Type': 'CanonicalUser',
                        'DisplayName': 'owner',
                    },
                    'Permission': 'FULL_CONTROL',
                }
            ]
        }
        
        bucket_name = 'example_bucket'
        self.assertFalse(s3_sec.check_bucket_public_access(s3_client, bucket_name))

    def test_bucket_public(self):
        s3_client = MagicMock()
        s3_client.get_public_access_block.return_value = {
            'PublicAccessBlockConfiguration': {
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        }
        s3_client.get_bucket_policy_status.return_value = {
            'PolicyStatus': {
                'IsPublic': True
            }
        }
        s3_client.get_bucket_acl.return_value = {
            'Grants': [
                {
                    'Grantee': {
                        'Type': 'Group',
                        'URI': 'http://acs.amazonaws.com/groups/global/AllUsers',
                    },
                    'Permission': 'READ',
                }
            ]
        }
        
        bucket_name = 'example_bucket'
        self.assertTrue(s3_sec.check_bucket_public_access(s3_client, bucket_name))

class TestBlockBucketPublicAccess(unittest.TestCase):

    def test_block_public_access(self):
        """
        Test blocking public access to an S3 bucket.
        """

        s3_client = MagicMock()

        # Simulate successful public access block configuration
        s3_client.put_public_access_block.return_value = {
            'PublicAccessBlockConfiguration': {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        }

        bucket_name = 'example_bucket'
        s3_sec.block_bucket_public_access(s3_client, bucket_name)

        # Assert that put_public_access_block was called with expected arguments
        s3_client.put_public_access_block.assert_called_once_with(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )        