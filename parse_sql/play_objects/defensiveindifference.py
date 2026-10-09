class DefensiveIndifference:
    TABLE_CREATE = """
        CREATE TABLE DefensiveIndifferences (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS DefensiveIndifferences;"
    TABLE_INSERT = "INSERT INTO DefensiveIndifferences VALUES (?, ?);"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        return (str(self.id), str(self.playNum))