class Hit:
    TABLE_CREATE = """
        CREATE TABLE Hits (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Type CHAR(1) NOT NULL,
            Location VARCHAR(10),
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS Hits;"

    def __init__(self, id, playNum, tpe, location):
        self.id = str(id)
        self.playNum = int(playNum)
        self.tpe = str(tpe)
        self.location = str(location)

    def __call__(self):
        sql_str = f"INSERT INTO Hits VALUES ('{self.id}', '{self.playNum}', '{self.tpe}', '{self.location}');"
        return sql_str