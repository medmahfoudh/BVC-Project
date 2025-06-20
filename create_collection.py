from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType

client = QdrantClient(
    url="https://94d74b83-c25c-4b39-b117-9aec9a65db4c.us-east4-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Lt2YQ-IAfyBJAbRK6F2IxjnojnKSm72ENq-4z7-wqZY"
)

# client.create_collection(
#     collection_name="wieland_reports",
#     vectors_config=VectorParams(size=384, distance=Distance.COSINE)
# )

client.create_payload_index(
    collection_name="wieland_reports",
    field_name="metadata.company_name",
    field_schema=PayloadSchemaType.KEYWORD
)