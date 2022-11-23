class PPRVysfinPage:
    index = None
    offset = None
    limit =5
    query_limit = 5

    def __init__(self, index):
        self.index = index
        self.offset = (index-1)* 5
        self.limit = (index)* 5

    def __init__(self, index, limit):
        self.index = index
        self.limit = limit * index
        self.offset = (index - 1) * 5
        #print('page start')
        #print(self.index)
        #print(self.limit)
        #print(self.offset)
        #print('page ends')

    def get_index(self):
        return self.index

    def get_offset(self):
        return self.offset

    def get_limit(self):
        return self.limit

    def get_query_limit(self):
        return self.limit+1

    def get_data_limit(self):
        return self.limit -1
