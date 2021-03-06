''' plus_minus.py
'''

# Standard imports
import untangle
import sys
import os
import pathlib

# For bokeh
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20, d3
from bokeh.plotting import figure

#exclude_dirs = ["M2015-16"]
exclude_dirs = []
exclude_files = ["TEAM.XML", ".DS_Store"]

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
    '''
    Concatenates first 4 letters of each player to string s
    '''
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
        
        self.reb_pm = 0
        ''' self.reb_pm is rebound differential during this stint
        '''
        
        self.tos_pm = 0
        ''' self.tos_pm is TO differential during this stint
        '''
        
        self.possessions = 0
        ''' self.possessions is # of offensive possessions
        '''
        return
    
    def update_possessions(self, possessions):
    
        return self.possessions


    def update_points(self, points):
        ''' Updates the plus-minus for this stint and returns the new value
            Points are assumed to be negative for opponent buckets, positive for this team's buckets.
        '''
        # TODO: Assert points should be 1, 2, 3, -1, -2, or -3 because we update a basket at a time.

        self.plusminus += points 
        return self.plusminus
    
    ''' Updates the rebound plus-minus for this stint and returns the new value
        Rebounds are assumed to be negative for opponent rebounds, positive for this team's rebounds.
    '''
    def update_rebs(self, rebs):
        self.reb_pm += rebs
        return self.reb_pm
    
    def update_tos(self, tos):
        self.tos_pm += tos
        return self.tos_pm


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
        
        self.reb_pm = 0
        ''' The overall rebound plus-minus for the group of five. Also stored per stint so technically
            we could just calculate overall reb plus-minus from the stints and not store it here.
        '''
        
        self.tos_pm = 0
        ''' The overall TO plus-minus for the group of five. Also stored per stint so technically
            we could just calculate overall TO plus-minus from the stints and not store it here.
        '''


        self.seconds_on_court = 0
        ''' The overall amount of time on the court for this group of five. Again, this is also
            stored redundantly in the stints.
        '''

        self.stints = []
        ''' An array of Stint objects representing the times this group of five appeared on the 
            court together
        '''
        
        self.possessions = 0
        ''' Number of offensive Binghamton possessions
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
            
    def update_rebs(self, rebs):
        ''' Updates the reb plus-minus for this group of five, and returns the new value.
            Rebs are assumed to be negative for opponent, positive for this team.
            This function does NOT update the stint's reb plus minus. That is done insided FiveTracker,
            and then the stint is added to this Five when it completes.
        '''
        if rebs > 0:
            self.reb_pm += 1
        else:
            self.reb_pm -= 1
        return self.reb_pm


    def update_tos(self, tos):
        ''' Updates the TO plus-minus for this group of five, and returns the new value.
            Turnovers are assumed to be negative for opponent, positive for this team.
            This function does NOT update the stint's reb plus minus. That is done insided FiveTracker,
            and then the stint is added to this Five when it completes.
        '''
        if tos > 0:
            self.tos_pm += 1
        else:
            self.tos_pm -= 1
        return self.tos_pm


    def update_possessions(self, possessions):
        ''' Updates number of offensive possessions
        '''
        self.possessions += 1
        return


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
            return False
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
            
    def update_rebs(self, rebs):
        '''
        '''
        self.current_stint.update_rebs(rebs)
        t = tuple(self.current_five)
        if t not in self.all_fives.keys():
            self.all_fives[t] = Five()
        self.all_fives[t].update_rebs(rebs)
        return True

    def update_tos(self, tos):
        '''
        '''
        self.current_stint.update_tos(tos)
        t = tuple(self.current_five)
        if t not in self.all_fives.keys():
            self.all_fives[t] = Five()
        self.all_fives[t].update_tos(tos)
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
            print("Rebound Plus/Minus: %d" % self.all_fives[lineup].reb_pm)
            print("Turnover Plus/Minus: %d" % self.all_fives[lineup].tos_pm)
            print("   Minutes: %s" % self.all_fives[lineup].minutes())
            print("  # Stints: %d" % len(self.all_fives[lineup].stints))
            print("    Stints:")
            self.all_fives[lineup].show_stints()

class Game(object):
    ''' 
    '''
    
    def get_starters_h2(self):
        '''
        '''
        not_starters = []
        starters = []
        counter = 0
        subOccured = False
        #    gets second half starters
        for item in self.game_info.bbgame.plays:

            for per in item.period:
                if per['number'] == '2':

                    for play in per.play:
#                        before any subs occur, record any instances of player activity
                        if play['team'] == 'BING' and play['action'] != 'SUB' and play['checkname'] not in not_starters and play['checkname'] not in starters and play['checkname'] != 'TEAM' and counter < 5:
                            starters.append(play['checkname'])
                            counter += 1

                        elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'IN' and play['checkname'] not in starters:
                            not_starters.append(play['checkname'])
                        elif play['action'] == 'SUB' and play['team'] == 'BING' and play['type'] == 'OUT' and counter < 5:
                            if play['checkname'] not in not_starters and play['checkname'] not in starters:
                                starters.append(play['checkname'])
                                counter += 1
        print("\n SECOND HALF STARTERS:\t %s \n" % starters)
        return starters




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
                    return False
            elif play['type'] == 'OUT': 
                if not self.on_court.sub_out(play['checkname']):
                    print("Tried to sub out a player who was not in the game.")
                    return False
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
                
        elif play['action'] == 'REBOUND':
            rebs = 1
            if play['vh'] == 'H':
                self.hrebs += 1
            if play['vh'] == 'V':
                self.vrebs += 1
            
            if play['team'] != "BING":
                rebs *= -1
            
            self.on_court.update_rebs(rebs);

        elif play['action'] == 'TURNOVER':
            tos = 1
            if play['vh'] == 'H':
                self.htos += 1
            if play['vh'] == 'V':
                self.vtos += 1
    
            if play['team'] != "BING":
                tos *= -1
            
            self.on_court.update_tos(tos);

#        else:

#            print("Not doing anything with: ", end='')
#            print("[%s] %s %s %s (%s)." % \
#               (play['time'], play['action'], play['type'],
#               play['checkname'], play['team']))
        return True

    def process_plays(self):
        '''
        '''
        self.vscore = 0;
        self.hscore = 0;
        self.hrebs = 0;
        self.vrebs = 0;
        self.htos = 0;
        self.vtos = 0;
        self.time = "20:00";

        for item in self.game_info.bbgame.plays:
            for per in item.period:
                self.on_court.reset(int(per['number']))
                
#                only get starters for first half, second half set to last []
                if int(per['number']) == 1:
                    starters = self.get_starters(int(per['number']))
                if int(per['number']) == 2:
                    starters = self.get_starters_h2()
                
                set_lineup = self.on_court.set_lineup(starters)
                if set_lineup:
                    print ("")
                    print ("BEGIN HALF %s" % per['number'])
                    self.on_court.show_current_five()
                    for play in per.play:
                        logged = self.log_play(per,play)
                        if not logged: 
                            return False
                    self.on_court.new_stint('00:00', half=int(per['number']))
                else: 
                    return False
        print("[FINAL] Home: %d Away %d " % (self.hscore, self.vscore))
        print("[FINAL *REBOUNDS*] Home: %d Away %d " % (self.hrebs, self.vrebs))
        print("[FINAL *TURNOVERS*] Home: %d Away %d " % (self.htos, self.vtos))
        return True

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
           color=["blue" if x > 0 else "red" for x in pms]))

        p = figure(y_range=fvs, x_range=(min(pm for pm in pms) - 2, max(pm for pm in pms) + 2), 
           plot_height=350, title="Plus Minus for All Lineups",
           toolbar_location=None, tools="")

        #p.hbar(y='fvs', right='pms', height=0.9, color='color', legend="fvs", source=source)
        p.hbar(y='fvs', right='pms', height=0.9, color='color', legend=None, source=source)

        p.xgrid.grid_line_color = None
        p.legend.orientation = "vertical"
        p.legend.location = "top_center"

        show(p)


# generates array of all game XML files, 
def build_game_file_list(top_level_directory):
    '''
    '''
    game_file_list = []
    for root, dirs, files in os.walk(top_level_directory, topdown=True):
        for name in dirs:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            if name not in exclude_files:
                game_file = os.path.join(root, name) 
                game_file_list.append(game_file) 

    return game_file_list 


# ======
# main()
# ======
def main():
    ''' 
    '''
    game_file_list = build_game_file_list("GameEventData/MensBBXML")

    good_count = 0
    bad_count = 0
    for game_file in game_file_list:
        game = Game(game_file)
        game.show_source()
        game.show_venue()
        good_game = game.process_plays()
        if good_game:
           good_count += 1
           game.on_court.show_tracking_data()
        else:
           bad_count += 1  

    print("%d Total Games" % len(game_file_list))
    print("%d Games successfully processed." % good_count)
    print("%d Games NOT successfully processed." % bad_count)
    game.plot_game()

    return

if __name__ == "__main__":
    main()

