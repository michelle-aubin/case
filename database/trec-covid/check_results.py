from xml.dom import minidom
import plac

# Returns a list of queries
def get_queries(input_file):
    queries = []
    xml_doc = minidom.parse(input_file)
    topics = xml_doc.getElementsByTagName('topic')
    for topic in topics:
        queries.append(topic.getElementsByTagName('query')[0].childNodes[0].data)
    return queries


# Returns a dictionary of doc_ids with relevance score as value
# Given a topic number, t
def get_judgements(input_file, t):
    judgements = {}
    with open(input_file, "r") as f_in:
        for line in f_in:
            tnum, iteration, doc_id, score = line.split()
            tnum = int(tnum)
            if tnum < t:
                continue
            elif tnum > t:
                return judgements
            else:
                judgements[doc_id] = int(score.strip())
    return judgements

@plac.annotations(
   f_result=("File name of the result set", "positional", None, str),
   f_key=("File name of the TREC-COVID relevance judgement set.", "positional", None, str),
   f_queries=("File name of the query set.", "positional", None, str)
)
def main(f_result, f_key, f_queries):
    queries = get_queries(f_queries)
    with open(f_result, "r") as f_in:
        for line in f_in:
            tnum, q0, doc_id, rank, score = line.strip().split("\t")
            tnum = int(tnum)
            judgements = get_judgements(f_key, tnum)
            try:
                score = judgements[doc_id]
            except KeyError:
                score = 0
            finally:
                if score == 0:
                    score_str = ""
                elif score == 1:
                    score_str = "partially"
                else:
                    score_str = "fully"
                print("%d\t%d\t%s - %s" % (tnum, int(rank), doc_id, score_str))

if __name__ == "__main__":
    plac.call(main)