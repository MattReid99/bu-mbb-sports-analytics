'''
'''
import untangle

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
    print("End display_game.py.")

if __name__ == "__main__":
    main()
