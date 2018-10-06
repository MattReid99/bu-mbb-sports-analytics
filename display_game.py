'''
    '''
import untangle
from bokeh.plotting import figure, output_file, show

starters = []
bench = []

def show_source(game):
    print("  SOURCE: %s" % game.bbgame['source'])
    print(" VERSION: %s" % game.bbgame['version'])
    print("GEN DATE: %s" % game.bbgame['generated'])

def show_venue(game):
    
    print("GAME ID: %s" % game.bbgame.venue['gameid'])
    print("VISITOR: %s" % game.bbgame.venue['visname'])
    print("   HOME: %s" % game.bbgame.venue['homename'])
    print("   DATE: %s" % game.bbgame.venue['date'])
    print("   TIME: %s" % game.bbgame.venue['time'])
    print("  WHERE: %s" % game.bbgame.venue['location'])
    print(" ATTEND: %s" % game.bbgame.venue['attend'])
    
    

def show_plays(game):
    for item in game.bbgame.plays:
        print (item['format'])
        for per in item.period:
            print ("")
            print ("BEGIN HALF %s" % per['number'])
            for play in per.play:
                if play['action'] == 'SUB' and play['team'] == 'BING':
                    print("[%s] %s %s %s (%s)." % \
                          (play['time'], play['action'], play['type'], play['checkname'], play['team']))
# print("[%s] %s %s (%s)." % (play['time'], play['action'], play['checkname'], play['team']))

def show_starters(game):
    global starters
    global bench
    isSet = False
    counter = 0
    
    for item in game.bbgame.plays:
        for per in item.period:
            for play in per.play:
                isSet = False
                if play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'IN':
                    for name in bench:
                        if name == play['checkname']:
                            isSet = True
                            break
                    for name in starters:
                        if name == play['checkname']:
                            isSet = True
                            break
                    else:
                        if (not isSet) :
                            bench.append(play['checkname'])
            
                if play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'OUT':
                    for name in bench:
                        if name == play['checkname']:
                            isSet = True
                            break
                    for name in starters:
                        if name == play['checkname']:
                            isSet = True
                            break # player has already been accounted for
                    else:
                        if (not isSet):   starters.append(play['checkname'])
                        counter += 1
    for player in starters:
        print("\n\n Starter:\t%s" % player)
    for player in bench:
        print("\n\n Bench:\t%s" % player)


#def convertMinutesToTime(minutes):
    # todo


def recordScores(game):
    
    onCourt = []
    
    # x values - minutes in half when lineup took the court - minutes in half when lineup was next adjusted
    # y values -
    
    ptsBing = [0]
    ptsOpp = [0]
    
    counter = 0
    xVals = []
    yVals = []
    
    allLineups = []
    
    homeScore = 0
    awayScore = 0
    time = ""
    isHome = False
    
    # check whether hscore corresponds to Binghamton or opponent
    isHome = (game.bbgame.venue['homeid'] == 'BING')
    
    # gets game starters
    for team in game.bbgame.team:
        if team['id'] == 'BING':
            for player in team.player:
                if player['gs'] == '1':
                    onCourt.append(player['checkname'])

    if isHome:
        print("Time: 20:00\tHome: 0\tBinghamton: 0\n")
    else:
        print("Time: 20:00\tHome: 0\tBinghamton: 0\n")
    for temp in onCourt:
        print(" [%s] " % temp)


    # prints score and lineup after rotation changes in 1st half
    for item in game.bbgame.plays:
        for per in item.period:
            if per['number'] == '1':
                for play in per.play:
                    time = play['time']
                    # sub in comes before sub out
                    if play['action'] == 'GOOD':
                        homeScore = int(play['hscore'])
                        awayScore = int(play['vscore'])
                    elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'IN':
                        onCourt.append(play['checkname'])
                    elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'OUT':
                        if play['checkname'] in onCourt: onCourt.remove(play['checkname'])
                        if len(onCourt) == 5:
                            print("\n\n")
                            allLineups.append(onCourt)
                            counter += 1
                            xVals.append(counter)
                            
                            if isHome:
                                print("Time: %s\tBinghamton: %d\tAway: %d\n" % (time, homeScore, awayScore))
                                ptsBing.append(homeScore)
                                ptsOpp.append(awayScore)
                                yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))
                            else:
                                print("Time: %s\tHome: %d\tBinghamton: %d\n" % (time, homeScore, awayScore))
                                ptsBing.append(awayScore)
                                ptsOpp.append(homeScore)
                                yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))
                            for temp in onCourt:
                                print(" [%s] " % temp)



    print("\n\nHALF 2\n\n")
    # gets 2nd half starters
    onCourt.clear()
    for team in game.bbgame.team:
        if team['id'] == 'BING':
            for player in team.player:
                if player['oncourt'] == 'Y':
                    onCourt.append(player['checkname'])
    if isHome:
        print("Time: 20:00\tBinghamton: %d\tHome: %d\n" % (homeScore, awayScore))
        ptsBing.append(homeScore)
        ptsOpp.append(awayScore)

    else:
        print("Time: 20:00\tHome: 0\tBinghamton: 0\n" % (homeScore, awayScore))
        ptsBing.append(awayScore)
        ptsOpp.append(homeScore)
    for temp in onCourt:
        print(" [%s] " % temp)




    # prints score and lineup after rotation changes in 2nd half
    for item in game.bbgame.plays:
        for per in item.period:
            if per['number'] == '2':
                for play in per.play:
                    time = play['time']
                    # sub in comes before sub out
                    if play['action'] == 'GOOD':
                        homeScore = int(play['hscore'])
                        awayScore = int(play['vscore'])
                    elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'IN':
                        onCourt.append(play['checkname'])
                    elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'OUT':
                        if play['checkname'] in onCourt: onCourt.remove(play['checkname'])
                        if len(onCourt) == 5:
                            print("\n\n")
                            allLineups.append(onCourt)
                            counter += 1
                            xVals.append(counter)

                            if isHome:
                                print("Time: %s\tBinghamton: %d\tAway: %d\n" % (time, homeScore, awayScore))
                                ptsBing.append(homeScore)
                                ptsOpp.append(awayScore)
                                yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))
                            else:
                                print("Time: %s\tHome: %d\tBinghamton: %d\n" % (time, homeScore, awayScore))
                                ptsBing.append(awayScore)
                                ptsOpp.append(homeScore)
                                yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))
                            for temp in onCourt:
                                print(" [%s] " % temp)

    counter += 1
    xVals.append(counter)

    # record final lineups +/-
    if isHome:
        print("Final Score:\t\tBinghamton: %d\tAway: %d\n" % (homeScore, awayScore))
        ptsBing.append(homeScore)
        ptsOpp.append(awayScore)
        yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))
    else:
        print("\n\n\nFinal Score:\t\tHome: %d\tBinghamton: %d\n\n" % (homeScore, awayScore))
        ptsBing.append(awayScore)
        ptsOpp.append(homeScore)
        yVals.append((ptsBing[counter]-ptsBing[counter-1])-(ptsOpp[counter]-ptsOpp[counter-1]))


    temp = 1
    for val in yVals:
        print("[yVals] Value %d:\t%d" % (temp, val))
        temp += 1



    # output to static HTML file
    output_file("graph.html")

    # create a new plot with a title and axis labels
    p = figure(title="Plus/Minus by Lineup", x_axis_label='lineup number', y_axis_label='+/-')

    # add a line renderer with legend and line thickness
    p.line(xVals, yVals, legend="+/-", line_width=2)

    # show the results
    show(p)



        
# ======
# main()
# ======
def main():
    '''
        '''
    print("Begin display_game.py")
    print("")
    game = untangle.parse("GameEventData/MensBBXML/M2017-18/17-10.XML")
#    show_source(game)
#    show_venue(game)
#    show_plays(game)
    print("")
    #show_starters(game)
    recordScores(game)
    print("End display_game.py.")


if __name__ == "__main__":
    main()

