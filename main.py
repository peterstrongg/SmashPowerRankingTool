import pysmashgg
from tabulate import tabulate
from time import sleep
import xlsxwriter
import os

import Player

KEY = pysmashgg.SmashGG('2429ea2ccddc1718cc121120d210722e', True)
FILE_NAME = 'single.txt'
ATTENDANCE_REQ = 1

def getElligiblePlayers(tournaments):
    players = []
    for tournament in tournaments:
        page = 1
        entrants = KEY.tournament_show_entrants(tournament, 'ultimate-singles', page)
        while len(entrants) > 0:
            for i in range(len(entrants)):
                tag = entrants[i]['entrantPlayers'][0]['playerTag']
                playerId = entrants[i]['entrantPlayers'][0]['playerId']
                newEntrant = True

                # If player is already in list, increment attendance by 1
                for j in range(len(players)):
                    if playerId == players[j].playerId:
                        newEntrant = False
                        players[j].attendance += 1
                # end for

                if newEntrant:
                    players.append(Player.Player(tag, playerId))
            # end for

            page += 1
            entrants = KEY.tournament_show_entrants(tournament, 'ultimate-singles', page)
        # end while
    # end for

    elligiblePlayers = []
    for i in range(len(players)):
        if(players[i].attendance >= ATTENDANCE_REQ):
            elligiblePlayers.append(players[i])

    return elligiblePlayers
# end def

def getH2H(players, tournaments):
    for player in players:
        for opponent in players:
            player.h2h[opponent.tag] = [0, 0]

    for tournament in tournaments:
        page = 1
        sets = KEY.tournament_show_sets(tournament, 'ultimate-singles', page)
        while len(sets) > 0:
            for set in sets:
                winner = ''
                loser = ''
                if set['winnerId'] == set['entrant1Players'][0]['entrantId']:
                    winner = set['entrant1Players'][0]['playerTag']
                    loser = set['entrant2Players'][0]['playerTag']
                elif set['winnerId'] == set['entrant2Players'][0]['entrantId']:
                    winner = set['entrant2Players'][0]['playerTag']
                    loser = set['entrant1Players'][0]['playerTag']

                if winner not in players[0].h2h.keys() or loser not in players[0].h2h.keys():
                    page += 1
                    sets = KEY.tournament_show_sets(tournament, 'ultimate-singles', page)
                    break
                # end if

                for player in players:
                    if player.tag == winner:
                        if winner in player.h2h:
                            player.h2h[loser][0] = player.h2h[loser][0]+1
                    elif player.tag == loser:
                        if loser in player.h2h:
                            player.h2h[winner][1] = player.h2h[winner][1]+1
                # end for
            # end for
            page += 1
            sets = KEY.tournament_show_sets(tournament, 'ultimate-singles', page)
        # end while
    # end for
    return players
# end def

def printElligiblePlayers(players):
    table = []
    for i in range(len(players)):
        row = []
        row.append(players[i].tag)
        row.append(players[i].attendance)
        table.append(row)
    # end for

    print(tabulate(table, headers = ["Players", "Attendance"]))
# end def

def writeToExcel(players):
    try:
        os.remove('H2HData.xlsx')
    except:
        print("xlsx file could not be removed")

    wbk = xlsxwriter.Workbook('H2HData.xlsx')
    sheet = wbk.add_worksheet()

    sheet.set_column(0, 0, 25)
    sheet.set_row(0, 25)

    row = 1
    for i in range(len(players)):
        sheet.set_row(i+1, 30)
        sheet.write(row, 0, players[i].tag)
        row += 1
    #sheet.write('B1', 'Test')

    wbk.close()
# end def

if __name__ == "__main__":
    with open(FILE_NAME) as file:
        tournaments = file.read().splitlines()

    players = getElligiblePlayers(tournaments)
    players = getH2H(players, tournaments)
    printElligiblePlayers(players)
    writeToExcel(players)
