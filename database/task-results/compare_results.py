import plac
from kendall_tau_distance import kendall_tau_distance

@plac.annotations(
   f_result1=("File name of first result set", "positional", None, str),
   f_result2=("File name of second result set.", "positional", None, str),
   f_queries=("File name of the query set.", "positional", None, str)
)
def main(f_result1, f_result2, f_queries):
    print("Comparing %s and %s\n" % (f_result1, f_result2))
    with open(f_result1, "r") as f1:
        with open(f_result2, "r") as f2:
            with open(f_queries, "r") as fq:
                queries = fq.readlines()
                for query in queries:
                    print("Query: ", query.strip())
                    results1 = []
                    results2 = []
                    # print system names
                    # print("%s   %s" % (f_result1[20:-4], f_result2[20:-4]))
                    # get list of results and print
                    for i in range(5):
                        result1 = f1.readline().strip()
                        result2 = f2.readline().strip()
                        results1.append(result1)
                        results2.append(result2)
                    #    print("%s       %s" % (result1, result2))
                    # read blank line that separates the results for each query
                    f1.readline()
                    f2.readline()
                    print("Kendall tau distance: %d\n" % kendall_tau_distance(results1, results2))

if __name__ == "__main__":
    plac.call(main)
