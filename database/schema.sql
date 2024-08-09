DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS results;

CREATE TABLE IF NOT EXISTS users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    userid INTEGER,
    playdate DATETIME,
    correct INTEGER,
    questions INTEGER,
    ratio FLOAT
);
