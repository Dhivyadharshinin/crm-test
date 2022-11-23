class NWisefinPage:
    index = None
    offset = None
    limit =10
    query_limit = 10

    def __init__(self, index):
        self.index = index
        self.offset = (index-1) * 10
        self.limit = (index) * 10

    def __init__(self, index, limit):
        self.index = index
        self.limit = limit * index
        self.offset = (index - 1) * 10
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


class NWisefinPageExtra:
    index = None
    offset = None
    limit =25
    query_limit = 25

    # def __init__(self, index):
    #     self.index = index
    #     self.offset = (index-1) * 25
    #     self.limit = (index) * 10

    def __init__(self, index, limit):
        self.index = index
        self.limit = limit * index
        self.offset = (index - 1) * limit
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
