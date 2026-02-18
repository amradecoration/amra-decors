from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class SupabaseStorage(S3Boto3Storage):
    def url(self, name):
        return (
            f"https://{settings.SUPABASE_PROJECT_ID}.supabase.co/"
            f"storage/v1/object/public/{self.bucket_name}/{name}"
        )
