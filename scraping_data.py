import csv
from scholarly import scholarly

# Fungsi untuk mencari dan mendapatkan data judul dan abstrak
def search_scholar(query, max_results=5):
    
    search_query = scholarly.search_pubs(query)
    results = []

    # scholarly.pprint(next(search_query))
    pub = next(search_query)
    print(pub)
    # for i in range(max_results):
    #     try:
    #         pub = next(search_query)
    #         title = pub['bib']['title']
    #         abstract = pub['bib']['abstract']
    #         results.append({'title': title, 'abstract': abstract})
    #     except StopIteration:
    #         break

    # return results


def save_to_csv(results, filename="results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'abstract'])
        writer.writeheader()
        for result in results:
            writer.writerow(result)
      

# Contoh penggunaan
query = "sistem informasi berbasis web"
results = search_scholar(query, max_results=10)


# save_to_csv(results, "scholar_results.csv")


for idx, result in enumerate(results):
    print(f"{idx + 1}. Title: {result['title']}")
    print(f"   Abstract: {result['abstract']}\n")
