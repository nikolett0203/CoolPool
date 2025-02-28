import phylib;
import os
import random
import sqlite3
import math

#################################################################################
# SVG constants
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect id="green-square" width="1350" height="2700" x="0" y="0" fill="#C0D0C0"/>"""
FOOTER = """</svg>\n"""

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER

HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH

SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON

DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME

MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS

FRAME_INTERVAL = 0.01

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/
BALL_COLOURS = [ 
    "WHITE",
    "GOLD",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "GOLD",
    "BLUE",
    "RED",        # no LIGHTRED
    "PURPLE",     # no LIGHTPURPLE
    "ORANGE",      # no LIGHTORANGE
    "GREEN",
    "BROWN",       # no LIGHTBROWN 
    ]

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass


################################################################################
# still ball class that calls constructor from phylib.c and generates svg string
class StillBall(phylib.phylib_object):
    """
    Python StillBall class.
    """

    def __init__(self, number, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_STILL_BALL, 
                                      number, 
                                      pos, None, None, 
                                      0.0, 0.0 )
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall


    def svg (self):

        if (self.obj.still_ball.number == 0):
            svg = """ <circle id="cue" onmousedown="followme(event)" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x,
                                                                        self.obj.still_ball.pos.y,
                                                                        BALL_RADIUS,
                                                                        BALL_COLOURS[self.obj.still_ball.number])
        elif (0 < self.obj.still_ball.number < 9):
            svg = """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x,
                                                                        self.obj.still_ball.pos.y,
                                                                        BALL_RADIUS,
                                                                        BALL_COLOURS[self.obj.still_ball.number])
        else:        
            stripe_height = BALL_RADIUS * 0.5

            svg = """<circle cx="%d" cy="%d" r="%d" fill="white" />\n
                    <rect x="%d" y="%d" width="%d" height="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x,
                                                                        self.obj.still_ball.pos.y,
                                                                        BALL_RADIUS,
                                                                        self.obj.still_ball.pos.x - BALL_RADIUS,
                                                                        self.obj.still_ball.pos.y - stripe_height / 2,
                                                                        BALL_RADIUS * 2,
                                                                        stripe_height,
                                                                        BALL_COLOURS[self.obj.still_ball.number])

        # add outline to make it more visible
        svg += """<circle cx="%d" cy="%d" r="%d" fill="none" stroke="black" stroke-width="4" />\n""" % (
                                                                    self.obj.still_ball.pos.x,
                                                                    self.obj.still_ball.pos.y,
                                                                    BALL_RADIUS)
        
        return svg
        
    

# rolling ball class that calls constructor from phylib.c and generates svg string
class RollingBall(phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__(self, number, pos, vel, acc):

        phylib.phylib_object.__init__(self,
                                      phylib.PHYLIB_ROLLING_BALL,
                                      number,
                                      pos, vel, acc,
                                      0.0, 0.0)
        
        self.__class__ = RollingBall

    def svg(self):

        if (self.obj.still_ball.number == 0):
            svg = """ <circle id="cue" onmousedown="followme(event)" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, 
                                                                        self.obj.rolling_ball.pos.y, 
                                                                        BALL_RADIUS, 
                                                                        BALL_COLOURS[self.obj.rolling_ball.number])
        elif(0 < self.obj.still_ball.number < 9):
            svg = """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, 
                                                                        self.obj.rolling_ball.pos.y, 
                                                                        BALL_RADIUS, 
                                                                        BALL_COLOURS[self.obj.rolling_ball.number])
        
        else:
            stripe_height = BALL_RADIUS * 0.5

            svg = """<circle cx="%d" cy="%d" r="%d" fill="white" />\n
                    <rect x="%d" y="%d" width="%d" height="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x,
                                                                        self.obj.rolling_ball.pos.y,
                                                                        BALL_RADIUS,
                                                                        self.obj.rolling_ball.pos.x - BALL_RADIUS,
                                                                        self.obj.rolling_ball.pos.y - stripe_height / 2,
                                                                        BALL_RADIUS * 2,
                                                                        stripe_height,
                                                                        BALL_COLOURS[self.obj.rolling_ball.number])

        # add outline to make it more visible
        svg += """<circle cx="%d" cy="%d" r="%d" fill="none" stroke="black" stroke-width="4" />\n""" % (
                                                                    self.obj.rolling_ball.pos.x,
                                                                    self.obj.rolling_ball.pos.y,
                                                                    BALL_RADIUS)
        
        return svg            


        svg += """<circle cx="%d" cy="%d" r="%d" fill="none" stroke="black" stroke-width="4" />\n""" % (
                                                                        self.obj.still_ball.pos.x,
                                                                        self.obj.still_ball.pos.y,
                                                                        BALL_RADIUS)
        return svg


# hole class that calls constructor from phylib.c and generates svg string
class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__(self, pos):

        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_HOLE, 
                                      0,
                                      pos, None, None, 
                                      0.0, 0.0)
      
        self.__class__ = Hole

    def svg(self):

        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, 
                                                                          self.obj.hole.pos.y, 
                                                                          HOLE_RADIUS)


# hcushion class that calls constructor from phylib.c and generates svg string
class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):

        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_HCUSHION, 
                                      0, 
                                      None, None, None, 
                                      0.0, y)
      
        self.__class__ = HCushion

    def svg(self):

        if self.obj.hcushion.y == 0:
            coord = -25
        else:
            coord = self.obj.hcushion.y

        return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (coord)

# vcushion class that calls constructor from phylib.c and generates svg string
class VCushion(phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__(self, x):

        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_VCUSHION, 
                                      0, 
                                      None, None, None, 
                                      x, 0.0)
      
        self.__class__ = VCushion

    def svg(self):

        if self.obj.vcushion.x == 0:
            coord = -25
        else:
            coord = self.obj.vcushion.x
        
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (coord)

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    def svg(self):
        
        svgstr = HEADER
        for object in self:
            if object is not None:
                svgstr += object.svg()
        svgstr += FOOTER
        return svgstr

    def roll(self, t):
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                # create a new ball with the same number as the old ball
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                                       Coordinate(0,0),
                                       Coordinate(0,0),
                                       Coordinate(0,0))
                # compute where it rolls to
                phylib.phylib_roll(new_ball, ball, t)
                # add ball to table
                new += new_ball
            if isinstance(ball, StillBall):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                                    Coordinate(ball.obj.still_ball.pos.x,
                                               ball.obj.still_ball.pos.y))
                # add ball to table
                new += new_ball
        # return table
        return new
    
    # function that returns cue ball to original position if it is sunk
    # also calculates balls left on the table
    def replace_cue_find_sunk(self, t):
        cue_found = 0
        new = Table()
        low_left = []
        high_left = []
        eight = False
        i = 0
        for ball in self:
            # if ball is still (all of them should be for the last frame)
            if isinstance(ball, StillBall):
                # if still, don't have to replace cue
                if ball.obj.still_ball.number == 0:
                    cue_found = 1
                # if low-numbered ball, put in low array
                elif ball.obj.still_ball.number < 8:
                    low_left.append(ball.obj.still_ball.number)
                # if eight ball found, track that
                elif ball.obj.still_ball.number == 8:
                    eight = True
                # if high-numbered ball, then high array
                else:
                    high_left.append(ball.obj.still_ball.number)
                # add all non-none balls to new table
                new += ball
            # if cue not found by last iteration, add it back
            if i == 25 and not cue_found:
                pos = Coordinate(TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                TABLE_LENGTH - TABLE_WIDTH/2.0 );
                sb  = StillBall( 0, pos );
                new += sb
            i+=1
        # update new table time
        new.time = t
        return new, low_left, high_left, eight




                    
# database class to create SQL tables for all table objects + control read/write operations
class Database:

    # helper method to compute acceleration in writeTable
    def computeAcc(self, rb_dx, rb_dy):

        speed = (rb_dx*rb_dx + rb_dy*rb_dy)**0.5

        acc_x = acc_y = 0.0

        if speed > VEL_EPSILON:
            acc_x = (-1*rb_dx/speed)*DRAG
            acc_y = (-1*rb_dy/speed)*DRAG

        return acc_x, acc_y

    # constructor to intialise database
    def __init__(self, reset=False):

        if reset:
            # we want our database file to be fresh so rm previous versions
            if os.path.exists('phylib.db'):
                os.remove('phylib.db')

        # open a database connection to allow sqlite3 to work with it
        # connection object represents connection to on-disk database file
        self.conn = sqlite3.connect('phylib.db', check_same_thread=False)

    # method to create tables for ball, time, games, player, and shot info
    def createDB(self):
        self.cur = self.conn.cursor()
        self.cur.execute(""" CREATE TABLE IF NOT EXISTS Ball (
                        BALLID      INTEGER PRIMARY KEY AUTOINCREMENT,
                        BALLNO      INTEGER NOT NULL,
                        XPOS        FLOAT NOT NULL,
                        YPOS        FLOAT NOT NULL,
                        XVEL        FLOAT,
                        YVEL        FLOAT);""")
        
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ball_number ON Ball(BALLNO);")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS TTable (
                        TABLEID     INTEGER PRIMARY KEY AUTOINCREMENT,
                        TIME        FLOAT NOT NULL);""")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS BallTable (
                        BALLID      INTEGER NOT NULL,
                        TABLEID     INTEGER NOT NULL,
                        FOREIGN KEY (BALLID) REFERENCES Ball,
                        FOREIGN KEY (TABLEID) REFERENCES TTable);""")
        
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_table_id ON BallTable(TABLEID);")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS Game (
                        GAMEID      INTEGER NOT NULL,
                        GAMENAME    VARCHAR(64) NOT NULL,
                        PRIMARY KEY (GAMEID));""")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS Player (
                        PLAYERID    INTEGER NOT NULL,
                        GAMEID      INTEGER NOT NULL,
                        PLAYERNAME  VARCHAR(64) NOT NULL,
                        PRIMARY KEY (PLAYERID),
                        FOREIGN KEY (GAMEID) REFERENCES Game);""")

        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_player_game ON Player(GAMEID);")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS Shot (
                        SHOTID      INTEGER NOT NULL,
                        PLAYERID    INTEGER NOT NULL,
                        GAMEID      INTEGER NOT NULL,
                        PRIMARY KEY (SHOTID),
                        FOREIGN KEY (PLAYERID) REFERENCES Player,
                        FOREIGN KEY (GAMEID) REFERENCES Game);""")
        
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_shot_player ON Shot(PLAYERID);")

        self.cur.execute(""" CREATE TABLE IF NOT EXISTS TableShot (
                        TABLEID     INTEGER NOT NULL,
                        SHOTID      INTEGER NOT NULL,
                        FOREIGN KEY (TABLEID) REFERENCES TTable,
                        FOREIGN KEY (SHOTID) REFERENCES Shot);""")
        
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_balltable_ballid ON BallTable(BALLID);")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_ttable_time ON TTable(TIME);")

        
        self.conn.commit()
        self.cur.close()


    def writeManyTables(self, tables):

        if tables is None:
            return None

        tableIDs = []   # track table IDs
        ballData = []   # track ballIDs
        ballTableData = []  # correspond table IDs to ballIDs

        self.cur = self.conn.cursor()  

        # find the previous max table ID
        self.cur.execute("""SELECT max(ROWID) from TTable""")
        oldMaxTT = self.cur.fetchone()[0] or 0

        # fill TTable with times
        table_data = [(table.time,) for table in tables]
        self.cur.executemany("""INSERT INTO TTable (TIME) VALUES (?);""", table_data)

        # get IDs of new times
        self.cur.execute("""SELECT TABLEID FROM TTable WHERE ROWID > ? ORDER BY ROWID ASC""", (oldMaxTT,))
        tableIDs = [row[0] for row in self.cur.fetchall()]

        # get previous highest ball ID
        self.cur.execute("""SELECT max(ROWID) from Ball""")
        oldMaxB = self.cur.fetchone()[0] or 0

        # collect data on balls per time
        for table, tableID in zip(tables, tableIDs):
            for object in table:
                if isinstance(object, StillBall):
                    ballData.append((object.obj.still_ball.number, 
                                     object.obj.still_ball.pos.x, 
                                     object.obj.still_ball.pos.y, 
                                     None, 
                                     None))
                    # track the ID associated with each ball
                    ballTableData.append(tableID)
                elif isinstance(object, RollingBall):
                    ballData.append((object.obj.rolling_ball.number, 
                                     object.obj.rolling_ball.pos.x, 
                                     object.obj.rolling_ball.pos.y, 
                                     object.obj.rolling_ball.vel.x, 
                                     object.obj.rolling_ball.vel.y))
                    ballTableData.append(tableID)
                    
        # now we insert our ball data
        self.cur.executemany("""INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?);""", ballData)

        # then we collect all the ball IDs associated with them 
        self.cur.execute("""SELECT BALLID FROM Ball WHERE ROWID > ? ORDER BY ROWID ASC""", (oldMaxB,))
        ballIDs = [row[0] for row in self.cur.fetchall()]
        
        print("error check: ", len(ballIDs), "    ", len(ballTableData))

        # finally we fill the balltable with the ids
        ballTablePairs = list(zip(ballIDs, ballTableData))
        self.cur.executemany("""INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?);""", ballTablePairs)

        # # commit once at the end
        self.conn.commit()
        self.cur.close()

        # need to return -1 for ids adjusted by table nums
        tableIDs = [id - 1 for id in tableIDs]
        return tableIDs

    # method for writing table data into SQL database
    def writeTable(self, table):

        # check if table is null
        if table is None:
            return None

        self.cur = self.conn.cursor()

        # get table time and insert
        time = table.time

        self.cur.execute(""" INSERT INTO TTable (TIME)
                             VALUES (?);""", (time,))

        # get table id
        tableID = self.cur.lastrowid

        # iterate through all of the balls, store attributes in SQL tables
        for object in table:

            # still ball accessed differently than rolling
            if isinstance(object, StillBall):

                ballNum = object.obj.still_ball.number
                posX = object.obj.still_ball.pos.x
                posY = object.obj.still_ball.pos.y  
                self.cur.execute(""" INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL)
                                     VALUES (?, ?, ?, NULL, NULL);""", (ballNum, posX, posY))
                
                ballID = self.cur.lastrowid     
                self.cur.execute(""" INSERT INTO BallTable (BALLID, TABLEID)
                                     VALUES (?, ?);""", (ballID, tableID))

            # rolling ball accessed differently than still
            if isinstance(object, RollingBall):
                
                ballNum = object.obj.rolling_ball.number
                posX = object.obj.rolling_ball.pos.x
                posY = object.obj.rolling_ball.pos.y
                velX = object.obj.rolling_ball.vel.x
                velY = object.obj.rolling_ball.vel.y    
                self.cur.execute(""" INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL)
                                     VALUES (?, ?, ?, ?, ?);""", (ballNum, posX, posY, velX, velY))
                
                ballID = self.cur.lastrowid     
                self.cur.execute(""" INSERT INTO BallTable (BALLID, TABLEID)
                                     VALUES (?, ?);""", (ballID, tableID))

        self.conn.commit()
        self.cur.close()

        return tableID - 1

    # method for obtaining table data from SQL database and storing it in table object
    def readTable(self, tableID):

        self.cur = self.conn.cursor()
        table = Table()

        # find time of table
        self.cur.execute("""SELECT TIME FROM TTable 
                            WHERE TABLEID = ?;""", (tableID+1,))

        time = self.cur.fetchall()

        # if tableID not found in table, return None
        if not time: 
            self.cur.close()
            return None

        # find balls associated with given tableID
        self.cur.execute("""SELECT * FROM Ball 
                            INNER JOIN BallTable ON (Ball.BALLID = BallTable.BALLID)
                            WHERE BallTable.TABLEID = ?;""", (tableID+1,))    

        balls = self.cur.fetchall()          

        # obtain all the positions, velocities, and numbers of the balls to store in table
        for row in balls:

            ballID, ballNum, posX, posY, velX, velY, _, _  = row
            pos = Coordinate(posX, posY)

            # if no velocity returned, we know we have a still ball
            if velX is None or velY is None:  # possible problem line
                sb = StillBall(ballNum, pos)
                table += sb
            # else it's a rolling ball
            else: 
                vel = Coordinate(velX, velY)
                accX, accY = self.computeAcc(velX, velY)
                acc = Coordinate(accX, accY)               
                rb = RollingBall(ballNum, pos, vel, acc)
                table += rb

        table.time = time[0][0]

        self.cur.close()
        return table
    
    # helper method to retrieve game information from SQL database
    def getGame(self, gameID):

        self.cur = self.conn.cursor()

        # retrieve players associated with particular gameID
        self.cur.execute("""SELECT * FROM Player 
                            INNER JOIN Game ON (Player.GAMEID = Game.GAMEID)
                            WHERE Game.GAMEID = ?
                            ORDER BY Player.PLAYERID;""", (gameID+1,))
        
        data = self.cur.fetchall()

        self.conn.commit()
        self.cur.close()
        return data
    
    # helper method for inserting new game data into database
    def setGame(self, gameName, player1Name, player2Name):

        self.cur = self.conn.cursor()

        self.cur.execute(""" INSERT INTO Game (GAMENAME)
                             VALUES (?);""", (gameName,))
        
        gameID = self.cur.lastrowid

        self.cur.execute(""" INSERT INTO Player (GAMEID, PLAYERNAME)
                             VALUES (?, ?);""", (gameID, player1Name))
        self.cur.execute(""" INSERT INTO Player (GAMEID, PLAYERNAME)
                             VALUES (?, ?);""", (gameID, player2Name))       

        self.conn.commit()
        self.cur.close()
        return gameID
    
    # helper method to insert shot info to SQL database
    def newShot (self, gameName, playerName):

        self.cur = self.conn.cursor()

        self.cur.execute("""SELECT * FROM Player 
                            INNER JOIN Game ON (Player.GAMEID = Game.GAMEID)
                            WHERE Player.PLAYERNAME = ? AND Game.GAMENAME = ?;""", (playerName, gameName))  
        
        data = self.cur.fetchall()

        playerID, gameID, _, _, _ = data[0]

        self.cur.execute(""" INSERT INTO Shot (PLAYERID, GAMEID)
                             VALUES (?, ?);""", (playerID, gameID))        

        shotID = self.cur.lastrowid

        self.conn.commit()
        self.cur.close()
        return shotID
    
    # helper method to store shot and table data in SQL database
    def newShotTable (self, shotID, tableID):
                
        if shotID is None or tableID is None:
            return

        self.cur = self.conn.cursor()

        self.cur.execute(""" INSERT INTO TableShot (TABLEID, SHOTID)
                        VALUES (?, ?);""", (tableID, shotID))

        self.conn.commit()
        self.cur.close()

    # method for writing many table ids into shotTable on one commit
    def manyNewShotTables(self, tableIDs, shotID):

        if shotID is None or not tableIDs:
            return

        self.cur = self.conn.cursor()

        # prepare data for insertion with execute many
        data = [(tableID, shotID) for tableID in tableIDs]

        self.cur.executemany("""INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?);""", data)

        # commit once
        self.conn.commit()
        self.cur.close()

    # method to get tableIDs associated with particular shot from the database
    def getTableIDs(self, shotID):
        if shotID is None:
            return []

        self.cur = self.conn.cursor()
        self.cur.execute("SELECT TABLEID FROM TableShot WHERE SHOTID = ?", (shotID,))
        tableIDs = [row[0] for row in self.cur.fetchall()]
        self.cur.close()

        return tableIDs

    # method to commit and close database connection
    def close (self):
        self.conn.commit()
        self.conn.close()     
        
# class to initialise game and control game logic
class Game:

    # class variable to track if the first ball has been sunk

    def __init__ (self, gameID=None, gameName=None, player1Name=None, player2Name=None):

        # make db
        self.db = Database()
        self.db.createDB()

        # store game data in db
        if gameID is not None and isinstance(gameID, int) and gameName is player1Name is player2Name is None:
            data = self.db.getGame(gameID)
            _, _, player1Name, _, gameName = data[0]
            _, _, player2Name, _, _ = data[1]

        elif gameID is None and isinstance(gameName, str) and isinstance (player1Name, str) and isinstance(player2Name, str):
            gameID = self.db.setGame(gameName, player1Name, player2Name)

        else:
            raise TypeError("Invalid input")
        
        self.first = 0

        self.firstBall = False

        # current player?
        self.current = random.randint(1,2)

        # who gets which balls
        self.high = None
        self.low = None

        self.p1 = player1Name
        self.p2 = player2Name

        self.game_name = gameName

        self.prev_hi_len = 7
        self.prev_lo_len = 7

        self.low_balls = [1,2,3,4,5,6,7]
        self.high_balls = [9,10,11,12,13,14,15]

        self.table = self.initialiseTable()
        
        self.gameover = False

        self.winner = None
        self.loser = None


    # method to execute a single pool shot
    def shoot (self, gameName, playerName, table, xvel, yvel):

        firstBall = None

        if gameName is None or playerName is None or table is None or xvel is None or yvel is None:
            return

        # insert preliminary shot data into database and collect ID
        shotID = self.db.newShot(gameName, playerName)

        if shotID is None:
            return None

        # find and convert the cue ball (from still to rolling)
    
        cue_ball = None

        for object in table:
            if isinstance(object, StillBall):
                if object.obj.still_ball.number == 0:
                    cue_ball = object

        if cue_ball == None:
            return None

        posX = cue_ball.obj.still_ball.pos.x
        posY = cue_ball.obj.still_ball.pos.y

        cue_ball.type = phylib.PHYLIB_ROLLING_BALL

        cue_ball.obj.rolling_ball.number = 0
        cue_ball.obj.rolling_ball.pos.x = posX
        cue_ball.obj.rolling_ball.pos.y = posY
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel

        accX, accY = self.db.computeAcc(xvel, yvel)
        cue_ball.obj.rolling_ball.acc.x = accX
        cue_ball.obj.rolling_ball.acc.y = accY

        tableData = []

        # calculate segments until shot is complete (null table returned)
        while table is not None:
            start = table.time
            newTable = table.segment()

            # calculate number of frames in shot
            if newTable is not None:
                saveTable = newTable
                frames = math.floor((newTable.time - start) / FRAME_INTERVAL)
                # starting from original state of segment
                # increment time by frame interval and calculate ball positions at that increment
                # then write data into database
                for frame in range(frames):
                    time = FRAME_INTERVAL * frame
                    timeTable = table.roll(time)
                    timeTable.time = start + time
                    tableData.append(timeTable)

                # determine the first ball
                if not self.first:
                    i = 0
                    for object in newTable:
                        if object is None and i != 25:
                            firstBall = i - 10
                            self.first = 1
                        i+=1                 

            table = newTable

        tableData.append(saveTable)

        tableIDs = self.db.writeManyTables(tableData)
        self.db.manyNewShotTables(tableIDs, shotID)

        return shotID, firstBall

    # Kremer's nudge function
    def nudge(self):
        return random.uniform( -1.5, 1.5 );

    # method to add all 16 balls to the table
    def initialiseTable(self):

        table = Table(); 

        # 1 ball
        pos = Coordinate(TABLE_WIDTH / 2.0,
                        TABLE_WIDTH / 2.0,
                        );

        sb = StillBall( 1, pos );
        table += sb;

        # 2 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0)/2.0 + 
                        self.nudge(),
                        TABLE_WIDTH/2.0 - 
                        math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 2, pos );
        table += sb;

        # 3 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0)/2.0 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 - 
                        math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 3, pos );
        table += sb;

        # 4 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 4, pos );
        table += sb;

        # 5 ball
        pos = Coordinate(TABLE_WIDTH/2.0 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 5, pos );
        table += sb;

        # 6 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 6, pos );
        table += sb;

        # 7 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0)*3/2 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        1.5*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 7, pos );
        table += sb;

        # 8 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0)/2 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        1.5*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 8, pos );
        table += sb;

        # 9 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0)/2 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        1.5*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 9, pos );
        table += sb;

        # 10 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0)*3/2 +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        1.5*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 10, pos );
        table += sb;

        # 11 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - 2*(BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        2*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 11, pos );
        table += sb;

        # # 12 ball
        pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        2*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 12, pos );
        table += sb;

        # 13 ball
        pos = Coordinate(TABLE_WIDTH/2.0,
                        TABLE_WIDTH/2.0 -
                        2*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 13, pos );
        table += sb;

        # 14 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        2*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 14, pos );
        table += sb;

        # 15 ball
        pos = Coordinate(TABLE_WIDTH/2.0 + 2*(BALL_DIAMETER+4.0) +
                        self.nudge(),
                        TABLE_WIDTH/2.0 -
                        2*math.sqrt(3.0)*(BALL_DIAMETER+4.0) +
                        self.nudge()
                        );
        sb = StillBall( 15, pos );
        table += sb;       

        # cue ball also still
        pos = Coordinate(TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                TABLE_LENGTH - TABLE_WIDTH/2.0 );
        sb  = StillBall( 0, pos );

        table += sb;

        return table

    # method to get tables based on shotIDs and generate svgs
    def getShotTables(self, shotID):
        tableIDs = self.db.getTableIDs(shotID)
        svg_frames = []
        table = None 
        for id in tableIDs:
            table = self.db.readTable(id)
            frame = table.svg()
            svg_frames.append(frame)

        return svg_frames, table
    
    def get_table(self):
        return self.table
    
    def get_current(self):
        return self.current
    
    def assign_hilo(self, firstBall):

        if 1<= firstBall <=  7:
            if self.current == 1:
                self.low = 1
                self.high = 2
            else:
                self.low = 2
                self.high = 1
        else:
            if self.current == 1:
                self.low = 2
                self.high = 1
            else:
                self.low = 1
                self.high = 2
        
    def game_state(self, low_left, high_left, eight):

        if self.current == self.low:
            if not eight:
                if not low_left:
                    self.gameover = True
                    self.winner = self.current
                    self.loser = 2 if self.current == 1 else 1
                    return True
                else: 
                    self.gameover = True
                    self.loser = self.current
                    self.winner = 2 if self.current == 1 else 1
                    return True       
        elif self.current == self.high:
            if not eight:
                if not high_left:
                    self.gameover = True
                    self.winner = self.current
                    self.loser = 2 if self.current == 1 else 1
                    return True # game over 
                else: 
                    self.gameover = True
                    self.loser = self.current
                    self.winner = 2 if self.current == 1 else 1
                    return True # game over 
        else:
            if not eight: 
                self.gameover = True
                self.loser = self.current
                self.winner = 2 if self.current == 1 else 1  

    def game_logic(self, vX, vY):

        curr_player = self.p1 if self.current == 1 else self.p2

        print("CURRENT 3: ", self.current)

        pass_table = self.table

        shotID, firstBall = self.shoot(self.game_name, curr_player, pass_table, vX, vY)
        svg_frames, self.table = self.getShotTables(shotID)

        if firstBall is not None:
            print(firstBall)
            self.assign_hilo(firstBall)
            self.firstBall = True

        self.table, self.low_balls, self.high_balls, eight = self.table.replace_cue_find_sunk(self.table.time)
        self.game_state(self.low_balls, self.high_balls, eight)

        print(self.high_balls, self.low_balls)

        if self.firstBall:
            print("here 11")
            if self.current == self.low:
                print("here 12")
                if self.prev_lo_len == len(self.low_balls):
                    self.current = 2 if self.current == 1 else 1
            elif self.current == self.high:
                print("here 13")
                if self.prev_hi_len == len(self.high_balls):
                    self.current = 2 if self.current == 1 else 1  

        else:
            # if balls not assigned yet, just switch normally
            print("B4: ", self.current)
            self.current = 2 if self.current == 1 else 1  
            print("AFTER: ", self.current)
    #                 print("here 12", MyHandler.current)
    #                 # PLAYER 1 HIT PLAYER 2 BALL AND IT SUNK

        self.prev_lo_len = len(self.low_balls)         
        self.prev_hi_len = len(self.high_balls) 

        svg_frames.append(self.table.svg())

        if self.gameover:

            if self.winner == 1:
                wins = self.p1
            else:
                wins = self.p2

            final_frame=f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                                <svg width="700" height="1375" viewBox="-25 -25 1400 2750"
                                xmlns="http://www.w3.org/2000/svg"
                                xmlns:xlink="http://www.w3.org/1999/xlink">
                                <rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" /> 
                                <rect width="1400" height="25" x="-25" y="-25" fill="darkgreen" />
                                <text x="50%" y="33%" text-anchor="middle" font-family="Title" font-size="150" fill="green">GAME OVER!</text>
                                <text x="50%" y="66%" text-anchor="middle" font-family="Title" font-size="150" fill="green">{wins} Wins!</text>
                                <rect width="1400" height="25" x="-25" y="2700" fill="darkgreen" />
                                <rect width="25" height="2750" x="-25" y="-25" fill="darkgreen" />
                                <rect width="25" height="2750" x="1350" y="-25" fill="darkgreen" />
                                <circle cx="0" cy="0" r="114" fill="black" />
                                <circle cx="0" cy="1350" r="114" fill="black" />
                                <circle cx="0" cy="2700" r="114" fill="black" />
                                <circle cx="1350" cy="0" r="114" fill="black" />
                                <circle cx="1350" cy="1350" r="114" fill="black" />
                                <circle cx="1350" cy="2700" r="114" fill="black" />
                                </svg>"""
            svg_frames.append(final_frame)

        return svg_frames

    def get_gamestatus(self):
        return self.gameover
    
    def get_currentplayer(self):
        return self.current
    
    def get_highballs(self):
        return len(self.high_balls)
    
    def get_lowballs(self):
        return len(self.low_balls)
    
    def get_assignment(self):
        if self.firstBall:
            return self.high
        else:
            return None
    
    def get_low_assignment(self):
        if self.firstBall:
            if self.low == 1:
                return self.p1
            else:
                return self.p2
        else:
            return "Unassigned"
    
    def get_high_assignment(self):
        if self.firstBall:
            if self.high == 1:
                return self.p1
            else:
                return self.p2
        else:
            return "Unassigned"