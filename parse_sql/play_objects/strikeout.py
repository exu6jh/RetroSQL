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

    def __init__(self, id, playNum, tpe):
        self.id = str(id)
        self.playNum = int(playNum)
        self.tpe = str(tpe)

    def __call__(self):
        sql_str = f"INSERT INTO Strikeouts VALUES ('{self.id}', '{self.playNum}', '{self.tpe}');"
        return sql_str