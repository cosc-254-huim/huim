class UtilListElem:
    def __init__(self, tid: int, iutil: int, rutil: int):
        self.tid = tid
        self.iutil = iutil
        self.rutil = rutil


class UtilList:
    def __init__(self, item: int):
        self.item = item
        self.sum_iutils = 0
        self.sum_rutils = 0
        self.elems = []

    def add_elem(self, elem: UtilListElem):
        self.elems.append(elem)
        self.sum_iutils += elem.iutil
        self.sum_rutils += elem.rutil


class ItemUtilPair:
    def __init__(self, item: int, util: int):
        self.item = item
        self.util = util
