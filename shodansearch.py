import shodan

class ShodanSearch:

    def __init__(self, api_key):
        self.client = shodan.Shodan(api_key)

    def search(self, query, page=1):
        """Realiza una consulta en Shodan y devuelve una pagina de resultados."""
        try:
            results = self.client.search(query, page=page)
            return results
        except Exception as e:
            print(f"Error al realizar la peticion a Shodan: {e}")
