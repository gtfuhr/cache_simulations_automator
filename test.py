import benchmarks

class Cache:
    def __init__(self,associativity,number_of_blocks,block_size):
        self.associativity = associativity
        self.number_of_blocks = number_of_blocks
        self.block_size = block_size
        return self
    
    def cache_size(self):
        return self.number_of_blocks * self.block_size