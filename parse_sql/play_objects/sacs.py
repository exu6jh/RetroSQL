class Sacs:
    TABLE_CREATE = """
        CREATE TABLE Sacs (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Sacs;"
    TABLE_INSERT = "INSERT INTO Sacs VALUES (?, ?);"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        return (str(self.id), str(self.playNum))