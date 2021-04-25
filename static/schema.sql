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
  cost            INTEGER DEFAULT 0,
  contact_name    TEXT NOT NULL,
  contact_email   TEXT NOT NULL,
  contact_phone   TEXT NOT NULL,
  facebook        TEXT DEFAULT NULL,
  twitter         TEXT DEFAULT NULL,
  instagram       TEXT DEFAULT NULL,
  url             TEXT DEFAULT NULL,
  photo           TEXT DEFAULT '',
  password        TEXT NOT NULL,
  verified        INTEGER DEFAULT 0,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS category;
CREATE TABLE category
(
  id              VARCHAR(12) PRIMARY KEY, /* random */
  title           TEXT NOT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS event_category;
CREATE TABLE event_category
(
  event_id       VARCHAR(12) REFERENCES event (id),
  category_id    VARCHAR(12) REFERENCES category (id),
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);


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
  cost            INTEGER DEFAULT 0,
  contact_name    TEXT NOT NULL,
  contact_email   TEXT NOT NULL,
  contact_phone   TEXT NOT NULL,
  facebook        TEXT DEFAULT NULL,
  twitter         TEXT DEFAULT NULL,
  instagram       TEXT DEFAULT NULL,
  url             TEXT DEFAULT NULL,
  photo           TEXT DEFAULT '',
  password        TEXT NOT NULL,
  verified        INTEGER DEFAULT 0,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS faq;
CREATE TABLE faq
(
  id              VARCHAR(12) PRIMARY KEY, /* random */
  question        TEXT NOT NULL,
  answer          TEXT NOT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS setting;
CREATE TABLE setting
(
  id              VARCHAR(14) PRIMARY KEY, /* random */
  about_title     TEXT NOT NULL,
  about_content   TEXT NOT NULL,
  faq_title       TEXT NOT NULL,
  faq_content     TEXT DEFAULT NULL,
  contact_title   TEXT NOT NULL,
  contact_email   TEXT NOT NULL,
  contact_phone   TEXT NOT NULL,
  contact_content TEXT NOT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
