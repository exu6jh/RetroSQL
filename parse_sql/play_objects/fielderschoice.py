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
    TABLE_INSERT = "INSERT INTO FieldersChoices VALUES (?, ?, ?, ?);"

    def __init__(self, id, playNum, fielder, location):
        self.id = str(id)
        self.playNum = int(playNum)
        self.fielder = int(fielder)
        self.location = str(location)

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.fielder), str(self.location))