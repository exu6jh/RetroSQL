class Interference:
    TABLE_CREATE = """
        CREATE TABLE Interferences (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Fielder INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Interferences;"

    def __init__(self, id, playNum, fielder):
        self.id = str(id)
        self.playNum = int(playNum)
        self.fielder = int(fielder)

    def __call__(self):
        sql_str = f"INSERT INTO Interferences VALUES ('{self.id}', '{self.playNum}', '{self.fielder}');"
        return sql_str