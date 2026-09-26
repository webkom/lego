from unittest import mock

from botocore import exceptions

from lego.apps.files.storage import Storage
from lego.utils.test_utils import BaseTestCase


class StorageTestCase(BaseTestCase):
    def setUp(self) -> None:
        with self.settings(
            AWS_ACCESS_KEY_ID="lego-test",
            AWS_SECRET_ACCESS_KEY="lego-test-secret-key",
            AWS_REGION="us-east-1",
        ):
            self.storage = Storage()

    def test_signs_with_sigv4(self) -> None:
        self.assertEqual(self.storage.client.meta.config.signature_version, "s3v4")
        self.assertEqual(
            self.storage.resource.meta.client.meta.config.signature_version, "s3v4"
        )

    def test_presigned_post_uses_sigv4_fields(self) -> None:
        signed = self.storage.generate_upload_url(
            "lego", "abakus.png", "http://localhost/redirect/"
        )

        self.assertIn("x-amz-algorithm", signed["fields"])
        self.assertIn("x-amz-signature", signed["fields"])

    def test_set_development_cors_allows_browser_uploads(self) -> None:
        with mock.patch.object(self.storage.client, "put_bucket_cors") as put_cors:
            self.storage.set_development_cors("lego")

        put_cors.assert_called_once_with(
            Bucket="lego",
            CORSConfiguration={
                "CORSRules": [
                    {
                        "AllowedOrigins": ["*"],
                        "AllowedMethods": ["GET", "HEAD", "POST", "PUT"],
                        "AllowedHeaders": ["*"],
                    }
                ]
            },
        )

    def test_set_development_cors_ignores_client_errors(self) -> None:
        error = exceptions.ClientError(
            {"Error": {"Code": "NotImplemented"}}, "PutBucketCors"
        )
        with mock.patch.object(
            self.storage.client, "put_bucket_cors", side_effect=error
        ):
            self.storage.set_development_cors("lego")
