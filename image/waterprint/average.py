class AverageMeter():
    def __init__(self):
        self.N=0.0
        self.totals=0.0
        self.avg=0.0

    def update(self,v,n=1.0):
        self.N+=n
        self.totals+=v
        self.avg=self.totals/self.N