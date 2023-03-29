import random

class Node():
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class ReplacementPolicy():
    def get(self, key):
        raise NotImplementedError('subclasses must override get()!')
    def put(self, key, val):
        raise NotImplementedError('subclasses must override put()!')
    def clear(self):
        raise NotImplementedError('subclasses must override clear()!')


class LRUCache(ReplacementPolicy):
    def __init__(self, capacity) -> None:
        super().__init__()
        self.capacity = capacity
        self.available = capacity
        #.storage saves the current key and value pair
        self.storage = {}
        # double linked list
        # where the key, val refers to the image data in db
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add(self, node):
        tmp_p = self.tail.prev
        tmp_p.next = node
        self.tail.prev = node
        node.prev = tmp_p
        node.next = self.tail
        self.storage[node.key] = node
        self.available -= len(node.val)

    # delete a key from memcache
    def invalidateKey(self, key):
        curr_node = self.storage[key]
        tmp_p = curr_node.prev
        temp_n = curr_node.next
        # update the two nodes by linking them together
        tmp_p.next = temp_n
        temp_n.prev = tmp_p
        self.storage.pop(key)
        self.available += len(curr_node.val)

    # when a key is retrived, it's the most recently used and should be at the end of dll
    # if key in current cache, we remove it from dll 
    # we add it to the end of dll
    def get(self, key):
        """
        >>> a = LRUCache(10)
        >>> a.put(1, 'a')
        0
        >>> a.put(2, 'bb')
        0
        >>> a.get(3)
        -1
        >>> a.get(1)
        'a'
        """
        # Update the value of the key if the key exists in cache. 
        # call function invalidate key to delete from cache
        # call function add to add it to cache again
        # Otherwise, report the fact that such key doesnt exist
        if key in self.storage:
            tmp_node = self.storage[key]
            self.invalidateKey(key)
            self.add(tmp_node)
            return tmp_node.val
        return -1
    
    def put(self, key, val) -> int:
        """
        >>> a = LRUCache(10)
        >>> a.put(1, 'a')
        0
        >>> a.put(2, 'bb')
        0
        >>> a.head.next.key
        1
        >>> a.put(5, 'eeeee')
        0
        >>> a.get(1)
        'a'
        >>> a.head.next.key
        2
        >>> a.put(7, 'ggggggg')
        0
        >>> print(set(a.storage.keys()))
        {1, 7}
        >>> b = a = LRUCache(10)
        >>> b.put(11, "a"*11)
        -1
        """
        size = len(val)
        if size > self.capacity:
            return -1
        if key in self.storage:
            self.invalidateKey(key)
        # check if capacity is reached
        # if reached, keep popping the first element in dll
        # until we have enough space
        while self.available < size:
            deleted_node = self.head.next
            self.invalidateKey(deleted_node.key)
        new_node = Node(key, val)
        self.storage[key] = new_node
        self.add(new_node)
        return 0

    def clear(self):
        self.available = self.capacity
        #.storage saves the current key and value pair
        self.storage = {}
        # double linked list
        # where the key, val refers to the image data in db
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head


class RRCache(ReplacementPolicy):

    def __init__(self, capacity) -> None:
        super().__init__()
        self.capacity = capacity
        self.available = capacity
        #.storage saves the current key and value pair
        self.storage = {}
        # double linked list
        # where the key, val refers to the image data in db

    def get(self, key):
        """
        :param key: the id of the image
        :return: the image data of the image
        >>> a = RRCache(3)
        >>> a.put(1, 'a')s
        0
        >>> a.storage
        {1: 'a'}
        >>> a.get(1)
        'a'
        >>> a.get(2)
        -1
        """
        if key in self.storage:
            target_val = self.storage[key]
            return target_val
        return -1

    def put(self, key, val) -> int:
        """
        :param key: the id of the image
        :param val: the list of [image data, image size]
        :return: None, -1 if the image size > maximum capacity
        >>> a = RRCache(3)
        >>> a.put(1, 'a')
        0
        >>> a.storage
        {1: 'a'}
        >>> a.put(3, 'ccc')
        0
        >>> a.storage
        {3: 'ccc'}
        """
        size = len(val)
        if size > self.capacity:
            return -1
        # check if capacity is reached
        # if reached, keep popping the first element in dll
        # until we have enough space
        while self.available < size:
            if len(self.storage) == 1:
                self.clear()
            else:
                # deleted_key = random.randint(1, len(self.storage)-1)
                deleted_key = list(self.storage.keys())[0]
                self.available += len(self.storage[deleted_key])
                del self.storage[deleted_key]

        self.storage[key] = val
        self.available -= len(val)
        return 0

    def clear(self):
        self.available = self.capacity
        self.storage = {}


class NOCache(ReplacementPolicy):
    def clear(self):
        return None
    def get(self, key):
        return -1
    def put(self, key, val):
        return -1

    


if __name__ == "__main__":
    # pass
    import doctest
    doctest.testmod()
