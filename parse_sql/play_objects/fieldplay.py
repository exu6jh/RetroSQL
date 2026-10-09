class FieldPlay:
    TABLE_CREATE = """
        CREATE TABLE FieldPlays (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Location VARCHAR(10),
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS FieldPlays;"
    TABLE_INSERT = "INSERT INTO FieldPlays VALUES (?, ?, ?);"

    def __init__(self, id, playNum, location):
        self.id = str(id)
        self.playNum = int(playNum)
        self.location = str(location)

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.location))