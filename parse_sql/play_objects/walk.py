class Walk:
    TABLE_CREATE = """
        CREATE TABLE Walks (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Intentional BOOLEAN NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Walks;"
    TABLE_INSERT = "INSERT INTO Walks VALUES (?, ?, ?);"

    def __init__(self, id, playNum, tpe):
        self.id = str(id)
        self.playNum = int(playNum)
        self.tpe = bool(tpe)

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.tpe))