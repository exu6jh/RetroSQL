class FieldersChoice:
    TABLE_CREATE = """
        CREATE TABLE FieldersChoices (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Fielder INT NOT NULL,
            Location VARCHAR(10),
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS FieldersChoices;"

    def __init__(self, id, playNum, fielder, location):
        self.id = str(id)
        self.playNum = int(playNum)
        self.fielder = int(fielder)
        self.location = str(location)

    def __call__(self):
        sql_str = f"INSERT INTO FieldersChoices VALUES ('{self.id}', '{self.playNum}', '{self.fielder}', '{self.location}');"
        return sql_str