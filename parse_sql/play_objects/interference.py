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
    TABLE_INSERT = "INSERT INTO Interferences VALUES (?, ?, ?);"

    def __init__(self, id, playNum, fielder):
        self.id = str(id)
        self.playNum = int(playNum)
        self.fielder = int(fielder)

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.fielder))