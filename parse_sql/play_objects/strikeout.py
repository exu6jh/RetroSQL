class Strikeout:
    TABLE_CREATE = """
        CREATE TABLE Strikeouts (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Type CHAR(1) NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Strikeouts;"
    TABLE_INSERT = "INSERT INTO Strikeouts VALUES (?, ?, ?);"

    def __init__(self, id, playNum, tpe):
        self.id = str(id)
        self.playNum = int(playNum)
        self.tpe = str(tpe)

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.tpe))