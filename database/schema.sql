CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_name TEXT NOT NULL,
    neutral_citation TEXT UNIQUE,
    judge TEXT,
    court TEXT,
    decision_date TEXT,
    parties TEXT,
    keywords TEXT,
    content TEXT,
    source TEXT DEFAULT 'Sample dataset',
    source_url TEXT,
    fetch_date TEXT DEFAULT (date('now'))
);

CREATE INDEX IF NOT EXISTS idx_cases_judge ON cases(judge);
CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);
CREATE INDEX IF NOT EXISTS idx_cases_date ON cases(decision_date);
CREATE INDEX IF NOT EXISTS idx_cases_source ON cases(source);
