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
   input_file=("Input file of queries", "positional", None, str),
   output_file=("Output file", "positional", None, str), 
   run_tag=("Tag representing the run", "positional", None, str),
   db_name=("Database name", "positional", None, str)
)
def main(input_file, output_file, run_tag, db_name):
    engine = Case(db_name)
    # get queries from input file
    queries = get_queries(input_file)
    for tnum, query in enumerate(queries):
        tnum += 1
        results = engine.search(query)
        i = 0
        with open(output_file, "a") as f_out:
            for tup in results:
                doc = tup[1]
                score = tup[0]
                # return max 1000 docs
                if i >= 1000 or not results:
                    # no docs returned
                    if i == 0:
                        # make dummy list
                        output_vals = [str(tnum), "Q0", doc, str(i+1), str(score), run_tag, "\n"]
                        f_out.write("\t".join(output_vals))
                    break
                i += 1
                output_vals = [str(tnum), "Q0", doc, str(i), str(score), run_tag, "\n"]
                f_out.write("\t".join(output_vals))

if __name__ == "__main__":
    plac.call(main)