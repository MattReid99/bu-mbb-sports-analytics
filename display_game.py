'''
    '''
import untangle

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

# ======
# main()
# ======
def main():
    '''
        '''
    print("Begin display_game.py")
    print("")
    game = untangle.parse("GameEventData/MensBBXML/M2017-18/17-10.XML")
    show_source(game)
    show_venue(game)
    show_plays(game)
    print("")
    show_starters(game)
    print("End display_game.py.")

if __name__ == "__main__":
    main()
