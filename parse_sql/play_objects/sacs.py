class Sacs:
    TABLE_CREATE = """
        CREATE TABLE Sacs (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Sacs;"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        sql_str = f"INSERT INTO Sacs VALUES ('{self.id}', '{self.playNum}');"
        return sql_str