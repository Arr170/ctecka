
class CheckPoint():
    def __init__(self, id, type):
        self.id = id
        self.type = type

class Route():
    route = []
    def __init__(self, name):
        self.name = name
        
    
    def setRoute(self, arr):
        if not isinstance(arr, list):
            raise TypeError("Must be a list.")
        for item in arr:
            if not isinstance(item, int):
                raise TypeError("Must be list of ints.")
        self.route = arr

class CheckInfo():
    succes: bool
    count: int
    points: list
    def __init__(self, suc, count, points):
        self.succes = suc
        self.count = count
        self.points = points

def checkRoute(route: Route, scannedPoints: list[int]): 

    CheckPointArr = []
    tracker = 0
    countCheck = 0
    
    print("checking: ", route.name)
    for i in range(0, len(scannedPoints)):
        # print(i+1, " element")
        # print("scanned: ", scannedPoints[i], " waiting for: ", route.route[tracker])
        if scannedPoints[i] == route.route[tracker]:
            CheckPointArr.append(CheckPoint(scannedPoints[i], True))
            tracker +=1
            if tracker >= len(route.route):
                break
            countCheck += 1
        else:
            CheckPointArr.append(CheckPoint(scannedPoints[i], False))
    print("result: ", countCheck == len(route.route))
    info = CheckInfo(countCheck == len(route.route), countCheck, CheckPointArr)
    return info
