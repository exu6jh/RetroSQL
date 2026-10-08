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

    def __init__(self, id, playNum, sbs):
        self.id = str(id)
        self.playNum = int(playNum)
        self.sbs = sbs

    def __call__(self):
        sql_str = f"INSERT INTO StolenBases VALUES ('{self.id}', '{self.playNum}', '{self.sbs[0]}', '{self.sbs[1]}', '{self.sbs[2]}');"
        return sql_str