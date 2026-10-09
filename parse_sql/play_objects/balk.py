class Balk:
    TABLE_CREATE = """
        CREATE TABLE Balks (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Balks;"
    TABLE_INSERT = "INSERT INTO Balks VALUES (?, ?);"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        return (str(self.id), str(self.playNum))