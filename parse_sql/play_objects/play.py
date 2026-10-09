class Play:
    TABLE_CREATE = """
        CREATE TABLE Plays (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Inning INT NOT NULL,
            Half INT NOT NULL,
            Outs INT NOT NULL,
            Batter CHAR(8) NOT NULL,
            Pitcher CHAR(8) NOT NULL,
            Play VARCHAR(2) NOT NULL,
            Runner1 CHAR(8),
            Runner2 CHAR(8),
            Runner3 CHAR(8),
            AdvanceB INT,
            Advance1 INT,
            Advance2 INT,
            Advance3 INT,
            RunV INT NOT NULL,
            RunH INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Plays;"
    TABLE_INSERT = "INSERT INTO Plays VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

    def __init__(self, id, playNum, inning, half, outs, batter, pitcher, play, runners, advances, runs):
        self.id = str(id)
        self.playNum = int(playNum)
        self.inning = int(inning)
        self.half = int(half)
        self.outs = int(outs)
        self.batter = str(batter)
        self.pitcher = str(pitcher)
        self.play = str(play)
        self.runner1 = str(runners[1])
        self.runner2 = str(runners[2])
        self.runner3 = str(runners[3])
        self.advanceB = str(advances[0])
        self.advance1 = str(advances[1])
        self.advance2 = str(advances[2])
        self.advance3 = str(advances[3])
        self.runV = int(runs[0])
        self.runH = int(runs[1])
    
    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.inning), str(self.half), str(self.outs), str(self.batter), str(self.pitcher), str(self.play), str(self.runner1), str(self.runner2), str(self.runner3), str(self.advanceB), str(self.advance1), str(self.advance2), str(self.advance3), str(self.runV), str(self.runH))
