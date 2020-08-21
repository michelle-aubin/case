import plac
from xml.dom import minidom
from Case import Case


# Returns a list of queries
# input_file: a trec-covid .xml file containing the queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        q = topic.getElementsByTagName('query')[0].childNodes[0].data
        queries.append(q)
    return queries


@plac.annotations(
   db_name=("Path to database", "positional", None, str)
)
def main(db_name):
    engine = Case(db_name)
    query = input("Enter a query: ")
    while query != "quit":
        results = engine.search(query)
        engine.print_query_results(results)
        query = input("Enter a query: ")


if __name__ == "__main__":
    plac.call(main)