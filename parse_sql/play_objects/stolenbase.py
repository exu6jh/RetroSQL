class StolenBase:
    TABLE_CREATE = """
        CREATE TABLE StolenBases (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Stole2 BOOLEAN NOT NULL,
            Stole3 BOOLEAN NOT NULL,
            StoleH BOOLEAN NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS StolenBases;"
    TABLE_INSERT = "INSERT INTO StolenBases VALUES (?, ?, ?, ?, ?);"

    def __init__(self, id, playNum, sbs):
        self.id = str(id)
        self.playNum = int(playNum)
        self.sbs = sbs

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.sbs[0]), str(self.sbs[1]), str(self.sbs[2]))