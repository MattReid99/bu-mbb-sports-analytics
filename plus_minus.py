''' plus_minus.py
'''

# Standard imports
import untangle

# For bokeh
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20, d3
from bokeh.plotting import figure

import pandas as pd

# =========================================================================================
# Utility functions for turning strings in format "mm:ss" into integer secs, and vice versa
# =========================================================================================
def minutes_str2secs(time_string):
    '''
    '''
    (mins, secs) = time_string.split(':')
    seconds = int(mins) * 60 + int(secs)
    return seconds

def minutes_secs2str(seconds):
    '''
    '''
    minutes = str(int(seconds / 60)).zfill(2) + ":" + str(int(seconds % 60)).zfill(2)
    return minutes

def tuple_2_str(tup):
    s = "5"
    for t in tup:
       s += "-"
       s += t[:4] 
    return s

# ==================
# Stint Class
# ==================
class Stint(object):
    '''
        A Stint object represents a linuep's time on the court.
    '''
    def __init__(self, begin_time, half):
        '''
        '''
        self.begin_time_secs = begin_time
        ''' self.begin_time_secs is an integer representing the number of seconds remaining in the half
                when this stint began
        '''

        self.end_time_secs = -1
        ''' self.end_time_secs is an integer representing the number of seconds remaining in the half
                when this stint began
        '''

        self.half = half
        ''' self.half == 1 for first half, self.half == 2 for 2nd half
        ''' 

        self.plusminus = 0
        ''' self.plusminus is point differential during this stint
        '''
        return

    def update_points(self, points):
        ''' Updates the plus-minus for this stint and returns the new value
            Points are assumed to be negative for opponent buckets, positive for this team's buckets.
        '''
        # TODO: Assert points should be 1, 2, 3, -1, -2, or -3 because we update a basket at a time.

        self.plusminus += points 
        return self.plusminus

    def show(self):
        ''' Prints the information stored in the stint object
        '''
        print("            Began: %s  Ended: %s [half:%d] Length: %s  +/1: %d" % \
            (minutes_secs2str(self.begin_time_secs), minutes_secs2str(self.end_time_secs), \
             self.half, minutes_secs2str(self.begin_time_secs - self.end_time_secs), \
             self.plusminus))
        return
 
# ==========
# Five Class
# ==========
class Five(object):
    ''' A Five object stores information about a single group of five's performance
    '''

    def __init__(self):
        '''
        '''
        self.plusminus = 0
        ''' The overall plus-minus for the group of five. Also stored per stint so technically
            we could just calculate overall plus-minus from the stints and not store it here.
        '''

        self.seconds_on_court = 0
        ''' The overall amount of time on the court for this group of five. Again, this is also
            stored redundantly in the stints.
        '''

        self.stints = []
        ''' An array of Stint objects representing the times this group of five appeared on the 
            court together
        '''
        return
    
    def update_points(self, points):
        ''' Updates the plus-minus for this group of five, and returns the new value.
            Points are assumed to be negative for opponent buckets, positive for this team's buckets.
            This function does NOT update the stint's plus minus. That is done insided FiveTracker,
            and then the stint is added to this Five when it completes.
        '''
        if points not in range(-3, 4) or points == 0:
            print("Five::update_points() points == %d, expecting -3, -2, -1, 1, 2, or 3." % points)
            exit()
        self.plusminus += points
        return self.plusminus

    def log_stint(self, stint):
        ''' Log the stint in the Python list of stints and update the time on court for this Five
        '''
        self.stints.append(stint) 
        self.seconds_on_court += stint.begin_time_secs - stint.end_time_secs
        return

    def minutes(self):
        ''' Return the minutes this group of five played as a formatted string
        '''
        return minutes_secs2str(self.seconds_on_court)

    def show_stints(self):
        ''' Print the stints for this group of five
        ''' 
        for stint in self.stints:
            stint.show()

# =================
# FiveTracker Class
# =================
class FiveTracker(object):
    '''
    '''
    def __init__(self):
        '''
        '''
        self.all_fives = dict()
        ''' A dictionary of all the groups of five that have played in this game.
            The dictionary maps a 5-tuple to a Five object.
        ''' 

        self.reset()
        return 

    def reset(self, half=1):
        ''' Reset the clock 
        '''
        self.current_five = []

        # TODO: This won't work for overtime! Let's find an overtime game and see how they code it.
        self.current_time_str = "20:00"
        self.current_time_secs = minutes_str2secs(self.current_time_str)

        self.current_stint = Stint(self.current_time_secs, half)

    def new_stint(self, sub_time_str, half):
        '''
        '''
        sub_time_secs = minutes_str2secs(sub_time_str)
        if self.current_stint.begin_time_secs != sub_time_secs:
            self.current_stint.end_time_secs = sub_time_secs
            self.current_stint.show()
            t = tuple(self.current_five)
            if t in self.all_fives.keys():
                self.all_fives[t].log_stint(self.current_stint)
            else:
                self.all_fives[t] = Five()
                self.all_fives[t].log_stint(self.current_stint)
            self.current_stint = Stint(sub_time_secs, half)
        else: 
            self.current_stint = Stint(sub_time_secs, half)
        return True

    def set_lineup(self, five):
        '''
        '''
        if len(five) != 5:
            print("FiveTracker::set_lineup() requires a list of 5 players.")
            print("    Received: ",)
            print(five)
            exit()
        self.current_five = five
        self.current_five.sort() 
        return True

    def sub_out(self, player):
        '''
        '''
        if player in self.current_five:
            self.current_five.remove(player)
            self.current_five.sort() 
            return True
        else:
            return False

    def sub_in(self, player):
        '''
        '''
        if player in self.current_five:
            return False
        else:
            self.current_five.append(player) 
            self.current_five.sort() 
            return True

    def update_plusminus(self, points):
        '''
        '''
        if points not in range(-3, 4) or points == 0:
            print("FiveTracker::update_plusminus() points == %d, expecting -3, -2, -1, 1, 2, or 3." \
                % points)
            exit()
        self.current_stint.update_points(points)
        t = tuple(self.current_five)
        if t not in self.all_fives.keys():
            self.all_fives[t] = Five()
        self.all_fives[t].update_points(points)
        return True

    def show_current_five(self):
        '''
        '''
        print("FIVE: ", end='')
        print(self.current_five)

    def show_tracking_data(self):
        '''
        '''
        print()
        print("LINEUPS ±")
        for lineup in self.all_fives.keys():
            print("")
            print(lineup)
            print("Plus/Minus: %d" % self.all_fives[lineup].plusminus)
            print("   Minutes: %s" % self.all_fives[lineup].minutes())
            print("  # Stints: %d" % len(self.all_fives[lineup].stints))
            print("    Stints:")
            self.all_fives[lineup].show_stints()

class Game(object):
    ''' 
    ''' 
    def get_starters(self, half=1):
        '''
        '''
        starters = []
        if half == 1: 
            starting_attr = 'gs'
            starting_label = '1'
        elif half == 2:
            starting_attr = 'oncourt'
            starting_label = 'Y'
        else:
            print("Game::get_starters() must be called with half == 1 or 2.")

        for team in self.game_info.bbgame.team:
            if team['id'] == 'BING':
                for player in team.player:
                    if player[starting_attr] == starting_label:
                        starters.append(player['checkname']) 
        return starters

    def __init__(self, file):
        '''
        '''
        # TODO: Error checking on file name
        self.game_info = untangle.parse(file) 
        self.on_court = FiveTracker()
    
    def show_source(self):
        '''
        '''
        print("  SOURCE: %s" % self.game_info.bbgame['source'])
        print(" VERSION: %s" % self.game_info.bbgame['version'])
        print("GEN DATE: %s" % self.game_info.bbgame['generated'])

    def show_venue(self):
        '''
        '''
        print("GAME ID: %s" % self.game_info.bbgame.venue['gameid'])
        print("VISITOR: %s" % self.game_info.bbgame.venue['visname'])
        print("   HOME: %s" % self.game_info.bbgame.venue['homename'])
        print("   DATE: %s" % self.game_info.bbgame.venue['date'])
        print("   TIME: %s" % self.game_info.bbgame.venue['time'])
        print("  WHERE: %s" % self.game_info.bbgame.venue['location'])
        print(" ATTEND: %s" % self.game_info.bbgame.venue['attend'])

    def log_play(self, per, play):
        ''' 
        ''' 
        if play['action'] == 'SUB' and play['team'] == 'BING':

            # TODO: We might as well do this for the opponent, too, right? So we can see which 
            # groups of five we had success or struggled against.

            self.on_court.new_stint(play['time'], half=int(per['number']))

            #print("[%s] %s %s %s (%s)." % \
            #   (play['time'], play['action'], play['type'], 
            #   play['checkname'], play['team']))

            if play['type'] == 'IN': 
                if not self.on_court.sub_in(play['checkname']):
                    print("Tried to sub in a player already in the game.")
                    exit()
            elif play['type'] == 'OUT': 
                if not self.on_court.sub_out(play['checkname']):
                    print("Tried to sub out a player who was not in the game.")
                    exit()
            self.on_court.show_current_five()

        elif play['action'] == 'GOOD':
            if play['vh'] == 'H':
                points = int(play['hscore']) - self.hscore
                self.hscore = int(play['hscore'])
            if play['vh'] == 'V':
                points = int(play['vscore']) - self.vscore
                self.vscore = int(play['vscore'])

            #print("[SCORE]: Home: %s  Away: %s " % (play['hscore'], play['vscore']))

            if play['team'] != "BING":
                points *= -1

            self.on_court.update_plusminus(points); 
        else:
            print("Not doing anything with: ", end='')
            print("[%s] %s %s %s (%s)." % \
               (play['time'], play['action'], play['type'], 
               play['checkname'], play['team']))

    def process_plays(self):
        '''
        '''
        self.vscore = 0;
        self.hscore = 0;
        self.time = "20:00";

        for item in self.game_info.bbgame.plays:
            for per in item.period:
                self.on_court.reset(int(per['number']))
                starters = self.get_starters(int(per['number']))
                self.on_court.set_lineup(starters)
                print ("")
                print ("BEGIN HALF %s" % per['number'])
                self.on_court.show_current_five()
                for play in per.play:
                    self.log_play(per,play)
                self.on_court.new_stint('00:00', half=int(per['number']))
            
        print("[FINAL] Home: %d Away %d " % (self.hscore, self.vscore))

    def plot_game(self):
        '''
        '''
        output_file("simple_plus_minus.html")    

        pms = []
        fvs = []
        print("PLOT GAME")

        fives = self.on_court.all_fives.keys()
        for f in fives:
            name5 = tuple_2_str(f)
            fvs.append(name5)
            pms.append(self.on_court.all_fives[f].plusminus)

        print(fvs)
        print(pms)
        #source = ColumnDataSource(data=dict(fvs=fvs, pms=pms, color=d3['Category20'][len(pms)])) 
        source = ColumnDataSource(data=dict(fvs=fvs, pms=pms, 
           color=["green" if x > 0 else "red" for x in pms])) 

        p = figure(y_range=fvs, x_range=(min(pm for pm in pms) - 2, max(pm for pm in pms) + 2), 
           plot_height=500, title="Plus Minus for All Groups of Five",
           toolbar_location=None, tools="")

        #p.hbar(y='fvs', right='pms', height=0.9, color='color', legend="fvs", source=source)
        p.hbar(y='fvs', right='pms', height=0.9, color='color', legend=None, source=source)

        p.xgrid.grid_line_color = None
        p.legend.orientation = "vertical"
        p.legend.location = "top_center"

        show(p)

# ======
# main()
# ======
def main():
    ''' 
    '''
    game = Game("GameEventData/MensBBXML/M2017-18/17-10.XML")

    game.show_source()
    game.show_venue()
    game.process_plays()

    game.on_court.show_tracking_data()
    game.plot_game()

if __name__ == "__main__":
    main()

