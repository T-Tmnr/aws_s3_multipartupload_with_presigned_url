from pathlib import Path
import logging
import argparse

from boto3 import Session
import requests


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class S3MultipartUploadUtil:
    """
    AWS S3 Multipart Upload Uril
    """
    def __init__(self, session: Session):
        self.session = session
        self.s3 = session.client('s3')
        self.upload_id = None
        self.bucket_name = None
        self.key = None

    def start(self, bucket_name: str, key: str):
        """
        Start Multipart Upload
        :param bucket_name:
        :param key:
        :return:
        """
        self.bucket_name = bucket_name
        self.key = key
        res = self.s3.create_multipart_upload(Bucket=bucket_name, Key=key)
        self.upload_id = res['UploadId']
        logger.debug(f"Start multipart upload '{self.upload_id}'")

    def create_presigned_url(self, part_no: int, expire: int=3600) -> str:
        """
        Create pre-signed URL for upload part.
        :param part_no:
        :param expire:
        :return:
        """
        signed_url = self.s3.generate_presigned_url(
            ClientMethod='upload_part',
            Params={'Bucket': self.bucket_name,
                    'Key': self.key,
                    'UploadId': self.upload_id,
                    'PartNumber': part_no},
            ExpiresIn=expire)
        logger.debug(f"Create presigned url for upload part '{signed_url}'")
        return signed_url

    def complete(self, parts):
        """
        Complete Multipart Uploading.
        `parts` is list of dictionary below.
        ```
        [ {'ETag': etag, 'PartNumber': 1}, {'ETag': etag, 'PartNumber': 2}, ... ]
        ```
        you can get `ETag` from upload part response header.
        :param parts: Sent part info.
        :return:
        """
        res = self.s3.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=self.key,
            MultipartUpload={
                'Parts': parts
            },
            UploadId=self.upload_id
        )
        logger.debug(f"Complete multipart upload '{self.upload_id}'")
        logger.debug(res)
        self.upload_id = None
        self.bucket_name = None
        self.key = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_file')
    parser.add_argument('--bucket', required=True)
    args = parser.parse_args()

    target_file = Path(args.target_file)
    bucket_name = args.bucket
    key = target_file.name
    max_size = 5 * 1024 * 1024

    file_size = target_file.stat().st_size
    upload_by = int(file_size / max_size) + 1

    session = Session()
    s3util = S3MultipartUploadUtil(session)

    s3util.start(bucket_name, key)
    urls = []
    for part in range(1, upload_by + 1):
        signed_url = s3util.create_presigned_url(part)
        urls.append(signed_url)

    parts = []
    with target_file.open('rb') as fin:
        for num, url in enumerate(urls):
            part = num + 1
            file_data = fin.read(max_size)
            print(f"upload part {part} size={len(file_data)}")
            res = requests.put(url, data=file_data)
            print(res)
            if res.status_code != 200:
                return
            etag = res.headers['ETag']
            parts.append({'ETag': etag, 'PartNumber': part})

    print(parts)
    s3util.complete(parts)


if __name__ == '__main__':
    main()
