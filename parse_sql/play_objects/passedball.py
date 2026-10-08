class PassedBall:
    TABLE_CREATE = """
        CREATE TABLE PassedBalls (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS PassedBalls;"

    def __init__(self, id, playNum):
        self.id = str(id)
        self.playNum = int(playNum)

    def __call__(self):
        sql_str = f"INSERT INTO PassedBalls VALUES ('{self.id}', '{self.playNum}');"
        return sql_str