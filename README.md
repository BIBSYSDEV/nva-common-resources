# nva-common-resources
Common AWS resources shared between stacks

## Static HTML hosting

The stack provisions a private S3 bucket served over HTTPS through CloudFront.
Upload HTML content to the bucket; nothing else is required to publish it.

Resolve the bucket, distribution ID and public hostname from SSM:

```
/NVA/StaticHtml/BucketName
/NVA/StaticHtml/DistributionId
/NVA/StaticHtml/PublicDomainName
```

Publish content and invalidate the CloudFront cache for the changed paths:

```sh
aws s3 sync ./html/ s3://<bucket>/
aws cloudfront create-invalidation --distribution-id <distribution-id> --paths '/*'
```

Conventions the distribution relies on:

- `index.html` is served for `/` and for every directory path ending in `/`.
  A directory path without the trailing slash is redirected to the slashed form.
- `404.html` at the bucket root is served for missing objects. Upload one with
  the content, or viewers see the raw S3 error body.
- Objects are served with the `Content-Type` S3 assigned at upload. Set it
  explicitly when the file extension is missing or unusual.

Set the `StaticHtmlDomainName` parameter to serve from a branded hostname with
TLS 1.2 instead of the `*.cloudfront.net` hostname. The hostname must be covered
by `FrontendDomainCertificateArn`, and a DNS alias to the distribution's domain
name must be created outside this stack.
