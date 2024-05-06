from Utils.KQXSVN import KQXSVN
from datetime import datetime

class KQXSVNFirstSpecial:
    def __init__(self):
        # Initialize any variables you need here
        pass

    def craw(self, processingDate: datetime):
        kqxsvn = KQXSVN()
        lastTwoPrizze = kqxsvn.craw(processingDate)
        lastTwoPrizze = {key: values[-2:] for key, values in lastTwoPrizze.items()}
        return lastTwoPrizze
