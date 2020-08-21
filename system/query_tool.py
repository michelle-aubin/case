import plac
from Case import Case

@plac.annotations(
   db_name=("Path to database", "positional", None, str)
)
def main(db_name):
    engine = Case(db_name)
    print("Enter \"quit\" to exit the application.")
    query = input("Enter a query: ")
    while query != "quit":
        results = engine.search(query)
        engine.print_query_results(results)
        query = input("Enter a query: ")


if __name__ == "__main__":
    plac.call(main)