import pysmashgg
from tabulate import tabulate
from time import sleep
import xlsxwriter
import os
import Player

KEY = pysmashgg.SmashGG('2429ea2ccddc1718cc121120d210722e', True)
FILE_NAME = 'events.txt'
ATTENDANCE_REQ = 3

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

    return players
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

                if winner not in players[0].h2h.keys() and loser not in players[0].h2h.keys():
                    page += 1
                    sets = KEY.tournament_show_sets(tournament, 'ultimate-singles', page)
                    break
                # end if

                # if a dq then dont count set
                if set['entrant1Score'] == -1 or set['entrant2Score'] == -1:
                    continue

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
    for player in players:
        if player.attendance >= ATTENDANCE_REQ:
            row = []
            row.append(player.tag)
            row.append(player.attendance)
            table.append(row)
        # end if
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

    sheet.set_column(0, 0, 17)
    sheet.set_column(1, len(players), 14)
    sheet.set_row(0, 30)

    colFormat = wbk.add_format(); colFormat.set_align('right')
    rowFormat = wbk.add_format(); rowFormat.set_align('center')

    row = 1
    col = 1
    for player in players:
        if player.attendance < ATTENDANCE_REQ:
            continue
        sheet.set_row(row, 30)
        sheet.write(row, 0, player.tag, colFormat)
        sheet.write(0, col, player.tag, rowFormat)
        row += 1
        col += 1
    # end for

    # Setting spreadsheet styles for h2h values
    red = wbk.add_format(); red.set_bg_color('#ffb3b3'); red.set_border(1); red.set_border_color('#999999'); red.set_font_color('#7d0000'); red.set_align('center'); red.set_align('vcenter')
    green = wbk.add_format(); green.set_bg_color('#9effa6'); green.set_border(1); green.set_border_color('#999999'); green.set_font_color('#005707'); green.set_align('center'); green.set_align('vcenter')
    yellow = wbk.add_format(); yellow.set_bg_color('#fdff8f'); yellow.set_border(1); yellow.set_border_color('#999999'); yellow.set_font_color('#918a00'); yellow.set_align('center'); yellow.set_align('vcenter')
    white = wbk.add_format(); white.set_bg_color('#ebebeb'); white.set_border(1); white.set_border_color('#999999'); white.set_font_color('#2e2e2e'); white.set_align('center'); white.set_align('vcenter')

    # Create array of tags of elligible players
    ePlayers = []
    for player in players:
        if player.attendance >= ATTENDANCE_REQ:
            ePlayers.append(player.tag)

    row = 1
    for player in players:
        if player.attendance < ATTENDANCE_REQ:
            continue

        col = 1
        for key in player.h2h:
            if key in ePlayers:
                if player.h2h[key][0] == 0 and player.h2h[key][1] == 0:
                    sheet.write(row, col, "{0} - {1}".format(player.h2h[key][0], player.h2h[key][1]), white)
                elif player.h2h[key][0] > player.h2h[key][1]:
                    sheet.write(row, col, "{0} - {1}".format(player.h2h[key][0], player.h2h[key][1]), green)
                elif player.h2h[key][0] < player.h2h[key][1]:
                    sheet.write(row, col, "{0} - {1}".format(player.h2h[key][0], player.h2h[key][1]), red)
                elif player.h2h[key][0] == player.h2h[key][1]:
                    sheet.write(row, col, "{0} - {1}".format(player.h2h[key][0], player.h2h[key][1]), yellow)
                col += 1
        # end for
        row += 1
    # end for

    wbk.close()
# end def

if __name__ == "__main__":
    with open(FILE_NAME) as file:
        tournaments = file.read().splitlines()

    players = getElligiblePlayers(tournaments)
    players = getH2H(players, tournaments)
    printElligiblePlayers(players)
    writeToExcel(players)
