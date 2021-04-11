
DROP TABLE IF EXISTS edit_event;
CREATE TABLE edit_event
(
  id              VARCHAR(12) PRIMARY KEY, /* random */
  event_id        VARCHAR(12) REFERENCES event (id),
  title           TEXT NOT NULL,
  organization    TEXT NOT NULL,
  description     TEXT NOT NULL,
  location        TEXT NOT NULL,
  start_date      DATE NOT NULL,
  start_time      TIME NOT NULL,
  end_date        DATE NOT NULL,
  end_time        TIME NOT NULL,
  cost            TEXT DEFAULT NULL,
  contact_name    TEXT NOT NULL,
  contact_email   TEXT NOT NULL,
  contact_phone   TEXT DEFAULT NULL,
  url             TEXT DEFAULT NULL,
  photo           TEXT DEFAULT '',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS event;
CREATE TABLE event
(
  id              VARCHAR(12) PRIMARY KEY, /* random */
  title           TEXT NOT NULL,
  organization    TEXT NOT NULL,
  description     TEXT NOT NULL,
  location        TEXT NOT NULL,
  start_date      DATE NOT NULL,
  start_time      TIME NOT NULL,
  end_date        DATE NOT NULL,
  end_time        TIME NOT NULL,
  cost            TEXT DEFAULT NULL,
  contact_name    TEXT NOT NULL,
  contact_email   TEXT NOT NULL,
  contact_phone   TEXT DEFAULT NULL,
  url             TEXT DEFAULT NULL,
  photo           TEXT DEFAULT '',
  password        TEXT NOT NULL,
  verified        INTEGER DEFAULT 0,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);