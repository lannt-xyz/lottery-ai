from Utils.KQXSVN import KQXSVN
from datetime import datetime

class KQXSVNFirstSpecial(KQXSVN):

    def __init__(self):
        # Initialize any variables you need here
        pass

    def getFilePrefix(self):
        return 'fstSpec_'

    def craw(self, processingDate: datetime):
        lastTwoPrizze = super().craw(processingDate)
        lastTwoPrizze = {key: values[-2:] for key, values in lastTwoPrizze.items()}
        return lastTwoPrizze
