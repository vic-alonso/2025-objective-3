import functions_framework
from flask import Request
from google.cloud import storage


@functions_framework.http
def count_items_in_the_bucket(request: Request) -> dict:
    bucket_name = request.args.get("bucket_name", "vic-objective-3")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs())
    items = len(blobs)
    return {"bucket": bucket_name, "items": items}
