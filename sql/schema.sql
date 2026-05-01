-- SISTEMA CONTABIL AUTOMATIZADO - SCHEMA ALINHADO AO APP

CREATE TABLE IF NOT EXISTS administradores (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cnpj_cpf VARCHAR(20),
    nome_completo VARCHAR(255),
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gerentes (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES administradores(id) ON DELETE CASCADE,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cnpj_cpf VARCHAR(20),
    nome_empresa VARCHAR(255),
    nome_completo VARCHAR(255),
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios_finais (
    id SERIAL PRIMARY KEY,
    gerente_id INTEGER NOT NULL REFERENCES gerentes(id) ON DELETE CASCADE,
    admin_id INTEGER,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cnpj_cpf VARCHAR(20),
    nome VARCHAR(255),
    nome_completo VARCHAR(255),
    perfil VARCHAR(50) DEFAULT 'usuario_final',
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contas_recorrentes (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES administradores(id) ON DELETE SET NULL,
    gerente_id INTEGER REFERENCES gerentes(id) ON DELETE SET NULL,
    cnpj_cpf_gerente VARCHAR(20),
    usuario_id INTEGER REFERENCES usuarios_finais(id) ON DELETE SET NULL,
    login_usuario VARCHAR(255),
    cnpj_cpf_usuario VARCHAR(20),
    valor_fixo NUMERIC(15, 2) NOT NULL,
    dia_vencimento INTEGER NOT NULL,
    descricao TEXT,
    ativa INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contas_receber (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios_finais(id) ON DELETE SET NULL,
    cnpj_cpf VARCHAR(20),
    login VARCHAR(255),
    valor_devido NUMERIC(15, 2),
    data_vencimento DATE,
    status VARCHAR(50) DEFAULT 'ABERTO',
    cfop VARCHAR(10),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorrente_id INTEGER REFERENCES contas_recorrentes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS logs_auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    tipo_usuario VARCHAR(50),
    cnpj_cpf VARCHAR(20),
    acao VARCHAR(255) NOT NULL,
    dados_novos TEXT,
    dados_antigos TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS aliquotas_padrao (
    id SERIAL PRIMARY KEY,
    cfop VARCHAR(10) NOT NULL,
    descricao TEXT,
    aliquota_icms_esperada NUMERIC(6, 2),
    aliquota_pis_esperada NUMERIC(6, 2),
    aliquota_cofins_esperada NUMERIC(6, 2),
    aliquota_ipi_esperada NUMERIC(6, 2),
    regime VARCHAR(100) DEFAULT 'Simples Nacional',
    anexo VARCHAR(20) DEFAULT 'III',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets_suporte (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios_finais(id) ON DELETE CASCADE,
    usuario_login VARCHAR(255) NOT NULL,
    usuario_email VARCHAR(255),
    tipo_problema VARCHAR(100) NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    prioridade VARCHAR(50) DEFAULT 'MEDIA',
    status VARCHAR(50) DEFAULT 'ABERTO',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resposta TIMESTAMP,
    resposta_admin TEXT,
    admin_id INTEGER REFERENCES administradores(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ticket_mensagens (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets_suporte(id) ON DELETE CASCADE,
    autor_tipo VARCHAR(50) NOT NULL,
    autor_id INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compatibilidade com schemas antigos do projeto.
ALTER TABLE administradores ADD COLUMN IF NOT EXISTS cnpj_cpf VARCHAR(20);
ALTER TABLE gerentes ADD COLUMN IF NOT EXISTS nome_empresa VARCHAR(255);
ALTER TABLE gerentes ADD COLUMN IF NOT EXISTS nome_completo VARCHAR(255);
ALTER TABLE usuarios_finais ADD COLUMN IF NOT EXISTS nome VARCHAR(255);
ALTER TABLE usuarios_finais ADD COLUMN IF NOT EXISTS nome_completo VARCHAR(255);
ALTER TABLE contas_recorrentes ADD COLUMN IF NOT EXISTS cnpj_cpf_gerente VARCHAR(20);
ALTER TABLE contas_recorrentes ADD COLUMN IF NOT EXISTS login_usuario VARCHAR(255);
ALTER TABLE contas_recorrentes ADD COLUMN IF NOT EXISTS cnpj_cpf_usuario VARCHAR(20);
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS aliquota_icms_esperada NUMERIC(6, 2);
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS aliquota_pis_esperada NUMERIC(6, 2);
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS aliquota_cofins_esperada NUMERIC(6, 2);
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS aliquota_ipi_esperada NUMERIC(6, 2);
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS regime VARCHAR(100) DEFAULT 'Simples Nacional';
ALTER TABLE aliquotas_padrao ADD COLUMN IF NOT EXISTS anexo VARCHAR(20) DEFAULT 'III';

CREATE INDEX IF NOT EXISTS idx_administradores_login ON administradores(login);
CREATE INDEX IF NOT EXISTS idx_gerentes_admin_id ON gerentes(admin_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_finais_gerente_id ON usuarios_finais(gerente_id);
CREATE INDEX IF NOT EXISTS idx_contas_recorrentes_gerente_id ON contas_recorrentes(gerente_id);
CREATE INDEX IF NOT EXISTS idx_contas_receber_usuario_id ON contas_receber(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_auditoria_usuario_id ON logs_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_auditoria_data_hora ON logs_auditoria(data_hora);
CREATE INDEX IF NOT EXISTS idx_tickets_suporte_usuario_id ON tickets_suporte(usuario_id);
CREATE INDEX IF NOT EXISTS idx_ticket_mensagens_ticket_id ON ticket_mensagens(ticket_id);
