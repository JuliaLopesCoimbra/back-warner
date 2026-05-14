-- Super FA — tabela própria (30 perguntas), separada do quiz principal.
-- Rode no PostgreSQL (psql, Railway Query, etc.).

CREATE TABLE IF NOT EXISTS super_fa_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt TEXT NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_choice CHAR(1) NOT NULL,
    category VARCHAR(80),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_super_fa_questions_correct_choice CHECK (correct_choice IN ('A', 'B', 'C', 'D'))
);

-- Tabelas criadas só pelo SQLAlchemy podem não ter DEFAULT em id; corrige sem recriar a tabela.
ALTER TABLE super_fa_questions
    ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- Evita duplicar linhas se o script for executado de novo (opcional).
-- DELETE FROM super_fa_questions WHERE category = 'Super FA';

-- Gera id no INSERT (não depende do DEFAULT da coluna).
INSERT INTO super_fa_questions (id, prompt, option_a, option_b, option_c, option_d, correct_choice, category)
SELECT gen_random_uuid(), v.prompt, v.option_a, v.option_b, v.option_c, v.option_d, v.correct_choice, v.category
FROM (VALUES
('Em Friends, qual é o nome do café favorito do grupo?', 'Central Perk', 'Central Park', 'Blue Bottle', 'Luke''s Diner', 'A', 'Super FA'),
('Qual instrumento musical Lisa Simpson toca na série?', 'Guitarra', 'Saxofone', 'Bateria', 'Violoncelo', 'B', 'Super FA'),
('No filme Matrix, qual pílula Neo escolhe para descobrir a verdade?', 'Verde', 'Azul', 'Vermelha', 'Amarela', 'C', 'Super FA'),
('Qual é o nome do dragão amigo de Hiccup em Como Treinar o Seu Dragão?', 'Banguela', 'Fúria da Noite', 'Smaug', 'Mushu', 'A', 'Super FA'),
('Em Harry Potter, qual casa valoriza lealdade e trabalho duro?', 'Sonserina', 'Corvinal', 'Lufa-Lufa', 'Grifinória', 'C', 'Super FA'),
('Quem interpretou Jack em Titanic (1997)?', 'Brad Pitt', 'Leonardo DiCaprio', 'Tom Cruise', 'Johnny Depp', 'B', 'Super FA'),
('Qual série se passa em Hawkins e envolve o Mundo Invertido?', 'Dark', 'Stranger Things', 'The OA', 'Lost', 'B', 'Super FA'),
('Em O Senhor dos Anéis, quantos anéis foram dados aos reis-anões, segundo o poema inicial?', 'Três', 'Sete', 'Nove', 'Um', 'B', 'Super FA'),
('Qual é o nome do cachorro da família Simpson?', 'Snowball II', 'Apu', 'Ajudante de Papai Noel', 'Barto', 'C', 'Super FA'),
('Em Breaking Bad, qual é o apelido de Walter White no tráfico?', 'Heisenberg', 'Gus', 'Tuco', 'Pinkman', 'A', 'Super FA'),
('Qual franquia tem o personagem Dom Toretto?', 'Missão Impossível', 'Velozes e Furiosos', 'John Wick', 'Top Gun', 'B', 'Super FA'),
('Em Game of Thrones, qual é o lema da Casa Stark?', 'O inverno está chegando', 'Fogo e sangue', 'Crescendo forte', 'Não esquecemos', 'A', 'Super FA'),
('Qual cantora lançou o álbum 1989 (versão pop) originalmente em 2014?', 'Adele', 'Taylor Swift', 'Lady Gaga', 'Beyoncé', 'B', 'Super FA'),
('Em Shrek, qual animal fala e vira melhor amigo do ogro?', 'Burro', 'Gato de Botas', 'Dragão', 'Lobo', 'A', 'Super FA'),
('Qual filme tem a frase: Eu sou seu pai?', 'Star Wars: O Império Contra-Ataca', 'Jurassic Park', 'Blade Runner', 'Alien', 'A', 'Super FA'),
('Em The Office (US), em qual cidade fica o escritório da Dunder Mifflin que acompanhamos?', 'Nova York', 'Scranton', 'Chicago', 'Austin', 'B', 'Super FA'),
('Qual super-herói é conhecido como o Cavaleiro das Trevas em Gotham?', 'Superman', 'Batman', 'Flash', 'Aquaman', 'B', 'Super FA'),
('Em Senhor dos Anéis, quem carrega o Um Anel até a Montanha da Perdição?', 'Aragorn', 'Gandalf', 'Frodo', 'Legolas', 'C', 'Super FA'),
('Em The Mandalorian, quem é o protagonista armado que cuida de Grogu?', 'Din Djarin', 'Boba Fett', 'Kylo Ren', 'Finn', 'A', 'Super FA'),
('Em Frozen, qual música ficou famosa com um solo poderoso no refrão?', 'Let It Go', 'Into the Unknown', 'Do You Want to Build a Snowman', 'Hakuna Matata', 'A', 'Super FA'),
('Qual ator interpretou Tony Stark no MCU até Vingadores: Ultimato?', 'Chris Evans', 'Chris Hemsworth', 'Robert Downey Jr.', 'Mark Ruffalo', 'C', 'Super FA'),
('Em Friends, Ross trabalha com qual área da ciência?', 'Química', 'Paleontologia', 'Astronomia', 'Biologia marinha', 'B', 'Super FA'),
('Qual é o nome do hotel isolado em O Iluminado?', 'Hotel Bates', 'Overlook Hotel', 'Grand Budapest', 'Hotel Transilvânia', 'B', 'Super FA'),
('Em Piratas do Caribe, qual é o nome do capitão interpretado por Johnny Depp?', 'Barba Negra', 'Jack Sparrow', 'Hector Barbossa', 'Davy Jones', 'B', 'Super FA'),
('Em O Poderoso Chefão, qual é o nome da família central da trama?', 'Corleone', 'Soprano', 'Gambino', 'Montana', 'A', 'Super FA'),
('Qual filme de animação da Pixar se passa dentro da mente de uma menina?', 'Soul', 'Divertida Mente', 'Viva: A Vida é uma Festa', 'Luca', 'B', 'Super FA'),
('Em O Senhor dos Anéis, qual criatura enfrenta Gandalf na ponte de Khazad-dûm?', 'Dragão', 'Troll', 'Balrog', 'Olho de Sauron', 'C', 'Super FA'),
('Qual é o nome do esporte jogado com vassouras voadoras em Harry Potter?', 'Quadribol', 'Gooblestone', 'Bludgerball', 'Snitch Run', 'A', 'Super FA'),
('Em The Big Bang Theory, qual é a profissão de Sheldon Cooper?', 'Engenheiro', 'Físico teórico', 'Astrônomo', 'Matemático aplicado', 'B', 'Super FA'),
('Qual franquia tem o slogan: Que a Força esteja com você?', 'Star Trek', 'Star Wars', 'Stargate', 'Duna', 'B', 'Super FA')
) AS v(prompt, option_a, option_b, option_c, option_d, correct_choice, category);
