from scipy.stats import kendalltau
import plac


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
                    print("%s   %s" % (f_result1[20:-4], f_result2[20:-4]))
                    for i in range(5):
                        result1 = f1.readline().strip()
                        result2 = f2.readline().strip()
                        results1.append(result1)
                        results2.append(result2)
                        print("%s       %s" % (result1, result2))
                    # read blank line that separates the results for each query
                    f1.readline()
                    f2.readline()
                    overlap = set(results1).intersection(set(results2))
                    if overlap:
                        print("Intersection of result sets: ", overlap)
                    else:
                        print("No intersection of results")
                    for i, (r1, r2) in enumerate(zip(results1, results2)):
                        if r1 == r2:
                            print("Doc %s has rank %d in both results" % (r1, i+1))
                    print("")





if __name__ == "__main__":
    plac.call(main)
