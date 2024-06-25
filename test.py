from reader.sireader2 import SIReaderReadout
import json
from trackChecking import Route, checkRoute

sir = SIReaderReadout()
track_a = [38, 35, 31, 34, 39, 32, 33, 36, 37]
track_b = [35, 31, 38, 39, 32, 33, 36, 34, 37]
track_c = [34, 32, 36, 38, 35, 31, 37, 35, 33, 39]

Ra = Route("A")
Ra.setRoute(track_a)

Rb = Route("B")
Rb.setRoute(track_b)

Rc = Route("C")
Rc.setRoute(track_c)

routeArr = [Ra, Rb, Rc]



while(True):  # returns True if card is inserted
    
    if sir.poll_sicard():
        try:
            data = sir.read_sicard()
            print(sir.ack_sicard())
            #print(data["punches"])
            arr=[]
            
            for a in data["punches"]:
                print(a[0], a[1])
                arr.append(a[0])
            print(data["start"])
            print(data["finish"])
            print("time: ", (data["finish"]-data["start"]).total_seconds())


            for r in routeArr:
                a = checkRoute(r, arr)
                print(a.succes, a.count)
            # pointArr = []
            # tracker = 0
            # countCheck = 0
            # print("track a: ", (arr==track_a))
            # for i in range(0, len(arr)):
            #     print(i+1, " element")
            #     print("scanned: ", arr[i], " waiting for: ", track_a[tracker])
            #     if arr[i] == track_a[tracker]:
            #         pointArr.append(CheckPoint(arr[i], "ok"))
            #         tracker +=1
            #         countCheck += 1
            #     else:
            #         pointArr.append(CheckPoint(arr[i], "bad"))
            # print("check a: ")
            # for p in pointArr:
            #     print(p.id, p.type)
            # print("overall: ", countCheck == len(track_a))
            
            # pointBrr = []
            # tracker = 0
            # countCheck = 0
            # print("track b: ", (arr==track_b))
            # for i in range(0, len(arr)):
            #     print(i+1, " element")
            #     print("scanned: ", arr[i], " waiting for: ", track_b[tracker])
            #     if arr[i] == track_b[tracker]:
            #         pointBrr.append(CheckPoint(arr[i], "ok"))
            #         tracker +=1
            #         countCheck += 1
            #     else:
            #         pointBrr.append(CheckPoint(arr[i], "bad"))
            # print("check b: ")
            # for p in pointBrr:
            #     print(p.id, p.type)
            # print("overall: ", countCheck == len(track_b))

            # pointCrr = []
            # tracker = 0
            # countCheck = 0
            # print("track c: ", (arr==track_c))
            # for i in range(0, len(arr)):
            #     print(i+1, " element")
            #     print("scanned: ", arr[i], " waiting for: ", track_c[tracker])
            #     if arr[i] == track_c[tracker]:
            #         pointCrr.append(CheckPoint(arr[i], "ok"))
            #         tracker +=1
            #         countCheck += 1
            #     else:
            #         pointCrr.append(CheckPoint(arr[i], "bad"))
            # print("check c: ")
            # for p in pointCrr:
            #     print(p.id, p.type)
            # print("overall: ", countCheck == len(track_c))

               # beeps the station after readout
        except Exception as e:
            print(e)