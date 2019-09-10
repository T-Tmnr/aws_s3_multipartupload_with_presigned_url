# AWS S3 Multipart Uploading with Pre-Signed URL
Testing multipart uploading with pre-singed URL.


## Notice
### Content-Type
When uploading parts, you should not set `Content-Type` on request header.
If you set it, maybe get response with `SignatureDoesNotMatch` error.

### Using pre-signed URL on web-browser
If you will use pre-signed url on browser, you need to configure S3 CORS.
https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/cors.html

### Incomplete Multipart Upload Parts
If you do not complete multipart uploading, uploaded parts are remained on a bucket.
You should set S3 lifecycle policy `AbortIncompleteMultipartUpload` for remove these parts.

## References
https://aws.amazon.com/premiumsupport/knowledge-center/s3-multipart-upload-cli/?nc1=h_ls
