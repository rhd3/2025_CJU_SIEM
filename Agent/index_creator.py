from elasticsearch import Elasticsearch

es = Elasticsearch("http://192.168.10.200:9200")

def create_index_with_mapping(index_name):
    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "source": {"type": "keyword"},
                "host": {"type": "keyword"},
                "message": {"type": "text"},
                "raw": {"type": "text"}
            }
        }
    }
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        print(f"Index {index_name} created with mapping.")
    else:
        print(f"Index {index_name} already exists.")