class PickOffCaughtStealing:
    TABLE_CREATE = """
        CREATE TABLE PickOffCaughtStealings (
            Id CHAR(12) NOT NULL,
            PlayNum INT NOT NULL,
            Pickoff1 BOOLEAN NOT NULL,
            Pickoff2 BOOLEAN NOT NULL,
            Pickoff3 BOOLEAN NOT NULL,
            Caught2 BOOLEAN NOT NULL,
            Caught3 BOOLEAN NOT NULL,
            CaughtH BOOLEAN NOT NULL,
            PRIMARY KEY (Id, PlayNum)
        );
    """
    TABLE_DELETE = "DROP TABLE IF EXISTS PickOffCaughtStealings;"

    def __init__(self, id, playNum, pos, css):
        self.id = str(id)
        self.playNum = int(playNum)
        self.pos = pos
        self.css = css

    def __call__(self):
        sql_str = f"INSERT INTO PickOffCaughtStealings VALUES ('{self.id}', '{self.playNum}', '{self.pos[0]}', '{self.pos[1]}', '{self.pos[2]}', '{self.css[0]}', '{self.css[1]}', '{self.css[2]}');"
        return sql_str