CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    birth_date DATE,
    position VARCHAR(100),
    debut_date DATE
);

INSERT INTO members (name, birth_date, position, debut_date) VALUES
('Minji', '2004-05-07', 'Leader, Lead Vocalist', '2022-07-22'),
('Hanni', '2004-10-06', 'Main Rapper, Sub Vocalist', '2022-07-22'),
('Danielle', '2005-04-11', 'Lead Rapper, Sub Vocalist', '2022-07-22'),
('Haerin', '2006-05-15', 'Main Vocalist', '2022-07-22'),
('Hyein', '2008-04-21', 'Maknae, Sub Vocalist', '2022-07-22');

CREATE TABLE songs (
    song_id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    release_date DATE,
    duration INT,
    genre VARCHAR(100)
);

INSERT INTO songs (title, release_date, duration, genre) VALUES
('Attention', '2022-07-22', 180, 'Pop'),
('Hype Boy', '2022-08-23', 200, 'Pop'),
('Cookie', '2022-09-23', 190, 'Pop'),
('Ditto', '2022-12-19', 185, 'Baltimore Club'),
('OMG', '2023-01-02', 210, 'Pop'),
('Super Shy', '2023-07-07', 154, 'Liquid Drum and Bass'),
('Bubble Gum', '2024-05-24', 200, 'Pop, R&B'),
('How Sweet', '2024-05-24', 219, 'Miami Bass, Electropop'),
('Supernatural', '2024-06-21', 191, 'New Jack Swing');
