class HitByPitch:
    TABLE_CREATE = """
        CREATE TABLE HitByPitches (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS HitByPitches;"
    TABLE_INSERT = "INSERT INTO HitByPitches VALUES (?, ?);"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        return (str(self.id), str(self.playNum))