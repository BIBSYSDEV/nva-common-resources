# nva-common-resources
Common AWS resources shared between stacks

## Static HTML hosting

The stack provisions an S3 bucket served over HTTPS through CloudFront. Anyone
who has, or guesses, a URL can read the content; there is no authentication.
Do not upload anything that must not be public. The bucket itself is reachable
only through CloudFront, never directly. Upload HTML content to the bucket;
nothing else is required to publish it.

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
- Every file must have an extension (`report.html`, `chart.png`). A path whose
  last segment has no dot is treated as a directory, so an extensionless object
  such as `LICENSE` can never be served.
- Directory names may contain dots (`v1.2/`), but then always link to them with
  the trailing slash. Without it the path is mistaken for a file and returns 404.
- `404.html` at the bucket root is served for missing objects. Upload one with
  the content, or viewers see the raw S3 error body.
- Objects are served with the `Content-Type` S3 assigned at upload, which it
  derives from the extension. Set it explicitly for unusual extensions.
- The NVA frontend at `https://<ApplicationDomain>` (SSM `/NVA/ApplicationDomain`)
  may embed pages in an iframe and fetch them cross-origin. Other origins can only navigate to the pages.

Set the `StaticHtmlDomainName` parameter to serve from a branded hostname with
TLS 1.2 instead of the `*.cloudfront.net` hostname. The hostname must be covered
by `FrontendDomainCertificateArn`, and a DNS alias to the distribution's domain
name must be created outside this stack.
