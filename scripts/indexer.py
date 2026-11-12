import os
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch("http://localhost:9200")

# Nomi dei due indici
idx_nomi = "index_nomi"
idx_testi = "index_testi"

# Reset se esistono gia
for idx in [idx_nomi, idx_testi]:
    if es.indices.exists(index=idx):
        es.indices.delete(index=idx)

# Indice per i nomi dei file (analyzer keyword)
es.indices.create(
    index=idx_nomi,
    body={
        "mappings": {
            "properties": {
                "filename": {"type": "text", "analyzer": "keyword"}
            }
        }
    }
)

# Indice per il contenuto (analyzer english)
es.indices.create(
    index=idx_testi,
    body={
        "mappings": {
            "properties": {
                "filename": {"type": "keyword"},
                "contenuto": {"type": "text", "analyzer": "english"},
                "linea": {"type": "integer"}
            }
        }
    }
)

start_time = time.time()
data_dir = "dati"

docs_nomi = []
docs_testi = []
file_count = 0

for name in sorted(os.listdir(data_dir)):
    if name.endswith(".txt"):
        file_count += 1
        filepath = os.path.join(data_dir, name)
        
        # Aggiungo al primo indice
        docs_nomi.append({
            "_index": idx_nomi,
            "_source": {"filename": name}
        })
        
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        for num, line in enumerate(lines, 1):
            text = line.strip()
            if text:
                docs_testi.append({
                    "_index": idx_testi,
                    "_source": {
                        "filename": name,
                        "contenuto": text,
                        "linea": num
                    }
                })

# Caricamento tramite bulk
bulk(es, docs_nomi)
bulk(es, docs_testi)

tot_time = round(time.time() - start_time, 2)

print(f"Indicizzazione terminata in {tot_time} secondi.")
print(f"File indicizzati: {file_count}")
print(f"Righe totali: {len(docs_testi)}")
