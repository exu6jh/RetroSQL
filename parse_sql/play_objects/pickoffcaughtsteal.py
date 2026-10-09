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
    TABLE_INSERT = "INSERT INTO PickOffCaughtStealings VALUES (?, ?, ?, ?, ?, ?, ?, ?);"

    def __init__(self, id, playNum, pos, css):
        self.id = str(id)
        self.playNum = int(playNum)
        self.pos = pos
        self.css = css

    def __call__(self):
        return (str(self.id), str(self.playNum), str(self.pos[0]), str(self.pos[1]), str(self.pos[2]), str(self.css[0]), str(self.css[1]), str(self.css[2]))