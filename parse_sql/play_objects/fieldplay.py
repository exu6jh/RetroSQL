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

    def __init__(self, id, playNum, location):
        self.id = str(id)
        self.playNum = int(playNum)
        self.location = str(location)

    def __call__(self):
        sql_str = f"INSERT INTO FieldPlays VALUES ('{self.id}', '{self.playNum}', '{self.location}');"
        return sql_str