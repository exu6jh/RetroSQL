class PassedBall:
    TABLE_CREATE = """
        CREATE TABLE PassedBalls (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS PassedBalls;"
    TABLE_INSERT = "INSERT INTO PassedBalls VALUES (?, ?);"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        return (str(self.id), str(self.playNum))