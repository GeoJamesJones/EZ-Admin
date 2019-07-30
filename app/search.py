from flask import app

def add_to_index(index, document, payload):
    if not app.elasticsearch:
        return
    app.elasticsearch.index(index=index, doc_type=document, body=payload)

def remove_from_index(index, document, id):
    if not app.elasticsearch:
        return
    app.elasticsearch.delete(index=index, doc_type=document, id=id)

def query_index(index, document, query, page, per_page):
    if not app.elasticsearch:
        return [], 0
    search = app.elasticsearch.search(
        index=index, doc_type=document,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']