import heapq as hq

class PQueue:
    def __init__(self, capacity):
        self.__items = []
        self.__capacity = capacity
        self.__entry_finder = {}
    
    # qver_num is the query version of terms that was used to get the score
    def add_doc_score(self, doc_id, score, qver_num):
        value = (score, doc_id, qver_num)
        # pqueue is not full yet
        if len(self.__items) < self.__capacity:
            # doc is already in the pqueue
            if doc_id in self.__entry_finder:
                old_doc_score = self.__entry_finder[doc_id]
                # add it if the new score is higher
                if old_doc_score[0] < score:
                    # print(self.__items)
                    self.replace_doc_score(old_doc_score, value)
            else:
                hq.heappush(self.__items, value)
                # print("Added ", (score, doc_id))
                # print(self.__items)
                self.__entry_finder[doc_id] = value
        # pqueue is full
        else:
            if score > self.__items[0][0]:
                # doc is already in the pqueue
                if doc_id in self.__entry_finder:
                    old_doc_score = self.__entry_finder[doc_id]
                    # replace it with new score if its higher
                    if score > old_doc_score[0]:
                        # print(self.__items)
                        self.replace_doc_score(old_doc_score, value)
                else:
                    removed = hq.heappushpop(self.__items, value)
                    # print("Removed ", removed)
                    # print("Added ", (score, doc_id))
                    self.__entry_finder.pop(removed[1])
                    self.__entry_finder[doc_id] = value
        

    def replace_doc_score(self, old_doc_score, new_doc_score):
        # print("Replacing ", old_doc_score, " with ", new_doc_score)
        self.__items.remove(old_doc_score)
        # print(self.__items)
        self.__items.append(new_doc_score)
        self.__entry_finder[new_doc_score[1]] = new_doc_score
        hq.heapify(self.__items)
    
    def get_items(self):
        return self.__items

    # assigns new score to doc score at index i of the list
    # used when adding proximity score to a doc's score
    def assign_new_score(self, i, new_score):
        self.__items[i] = new_score
        # could update entry finder with new score

    # sorts doc score in descending order of score
    def sort_descending(self):
        self.__items = hq.nlargest(len(self.__items), self.__items)


    


        