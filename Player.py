# Player class
class Player:
    def __init__(self, tag = 'None', playerId = -1):
        self.tag = tag
        self.playerId = playerId
        self.attendance = 1
        self.h2h = {}

    # h2h is a dict whose keys are player names and values are a 2 index array
    # index 0 contains win count and index 1 contains loss count
    def seth2h(opponent, winLoss):
        pass

    def __str__(self):
        return "{0}".format(self.tag)

# testDict = {"a": 1, "b": 2, "c": 3}
# for key in testDict:
#     print(testDict[key])
