import plac
from check_results import get_queries

@plac.annotations(
   f_eval=("File name of the trec_eval results", "positional", None, str),
   f_queries=("File name of the query set.", "positional", None, str)
)
def main(f_eval, f_queries):
    query_precisions = {str(i) : {} for i in range(1,46)}
    p_5_dict = {}
    with open(f_eval, "r") as f_in:
        for line in f_in:
            if line[0:2] == "P_":
                measure, tnum, value = line.split()
                if tnum == "all":
                    continue
                query_precisions[tnum][measure] = float(value)
                if line[0:4] == "P_5 ":
                    p_5_dict[tnum] = float(value)

    queries = get_queries(f_queries)
    print("{:^60}{:<10}{:<15}".format("Query", "P_5", "Max Precision"))
    # sorting on p_5
    for tnum, p_5 in sorted(p_5_dict.items(), key=lambda item: item[1], reverse=True):
        topic = "Query %s: %s" % (tnum, queries[int(tnum)-1])
        for measure, value in sorted(query_precisions[tnum].items(), key=lambda item: item[1], reverse=True):
            max_p = "%s=%.3f" % (measure, value)
            print("{:<60}{:<10.3f}{:<15}".format(topic, p_5, max_p))
            break

if __name__ == "__main__":
    plac.call(main)