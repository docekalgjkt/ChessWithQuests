class KwestManager:
    def __init__(self):
        self.kvesty = []

    def method(self, typ):
        for kwest in self.kvesty:
            if type(kwest).__name__ == typ:
                return kwest
        return None

    def pridej_kwest(self, kwest):
        self.kvesty.append(kwest)