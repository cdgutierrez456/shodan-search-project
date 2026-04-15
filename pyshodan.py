import os
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from shodansearch import ShodanSearch
from login_automatization import has_valid_credentials

def get_results(results, index):
    res = {
        'index': index,
        'data': f'\nResultado {index}\n'
                f"Direccion IP: {results['ip_str'] if results else 'no_ip'}\n"
                f"Hostname: {results['hostnames'] if results else 'no_hostname'}\n"
                f"Localizacion: {results['location'] if results else 'no_location'}\n"
                f"Credenciales por defecto: {has_valid_credentials(results)}\n"
    }
    return res

def main():
    load_dotenv()

    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

    ssearch = ShodanSearch(SHODAN_API_KEY)

    results = ssearch.search("title:dvwa", page=1)

    if not results:
        return

    t = time.perf_counter()

    workers = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            workers.append(executor.submit(get_results, results['matches'][i], i))

    for worker in as_completed(workers):
        result = worker.result()
        print(result['data'])

    print(f'Tiempo de procesamiento: {time.perf_counter() - t:.2f}s')

if __name__ == "__main__":
    main()