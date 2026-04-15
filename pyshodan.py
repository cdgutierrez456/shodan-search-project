from dotenv import load_dotenv
from shodansearch import ShodanSearch
from login_automatization import has_valid_credentials

import os

def main():
    load_dotenv()

    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

    ssearch = ShodanSearch(SHODAN_API_KEY)

    results = ssearch.search("title:dvwa", page=1)

    if not results:
        return

    for i in range(10):
        print(f'\nResultado {i}')
        print(f"Direccion IP: {results['matches'][i]['ip_str'] if results else 'no_ip'}")
        print(f"Hostname: {results['matches'][i]['hostnames'] if results else 'no_hostname'}")
        print(f"Localizacion: {results['matches'][i]['location'] if results else 'no_location'}")
        print(f"Credenciales por defecto: {has_valid_credentials(results['matches'][i])}")

if __name__ == "__main__":
    main()