from elasticsearch import Elasticsearch

# Connessione all'istanza locale di Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Nomi dei due indici di riferimento
idx_nomi = "index_nomi"
idx_testi = "index_testi"

def search():
    print("=== INTERFACCIA DI RICERCA ===")
    print("Sintassi:")
    print("  contenuto: parola")
    print("  contenuto: \"frase esatta\"")
    print("  nome: nome_file.txt")
    print("  Scrivi 'exit' per uscire.\n")

    while True:
        try:
            user_input = input("Query > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input or user_input.lower() == 'exit':
            break

        # Parsing della query per il contenuto (indice testi)
        if user_input.startswith("contenuto:"):
            val = user_input.split("contenuto:", 1)[1].strip()
            # Se la stringa e racchiusa tra virgolette uso match_phrase
            if val.startswith('"') and val.endswith('"'):
                clean_val = val[1:-1]
                query_body = {"query": {"match_phrase": {"contenuto": clean_val}}}
            else:
                query_body = {"query": {"match": {"contenuto": val}}}
            target_index = idx_testi

        # Parsing della query per nome file (indice nomi)
        elif user_input.startswith("nome:"):
            val = user_input.split("nome:", 1)[1].strip()
            query_body = {"query": {"match": {"filename": val}}}
            target_index = idx_nomi
        else:
            print("Sintassi non valida! Usa 'contenuto: ...' o 'nome: ...'\n")
            continue

        # Limite risultati e invio della query HTTP ad Elasticsearch
        query_body["size"] = 10
        res = es.search(index=target_index, body=query_body)
        hits = res['hits']['hits']

        # Stampa dei risultati e del tempo di esecuzione in ms
        print(f"\nRisultati trovati nell'indice '{target_index}': {res['hits']['total']['value']} (in {res['took']} ms)")
        for h in hits:
            src = h['_source']
            if target_index == idx_nomi:
                print(f" - File trovato: {src['filename']}")
            else:
                print(f" - Documento: {src['filename']} (riga {src.get('linea', '-')}) | {src['contenuto'][:80]}...")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    search()

