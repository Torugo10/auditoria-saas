-- SISTEMA CONTÁBIL AUTOMATIZADO - SCHEMA

-- Tabela de Usuários Admin
CREATE TABLE IF NOT EXISTS usuarios_admin (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    cnpj_cpf VARCHAR(20) UNIQUE NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_acesso TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Gerentes
CREATE TABLE IF NOT EXISTS usuarios_gerentes (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES usuarios_admin(id) ON DELETE CASCADE,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cnpj_cpf VARCHAR(20) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_acesso TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Usuários Finais
CREATE TABLE IF NOT EXISTS usuarios_finais (
    id SERIAL PRIMARY KEY,
    gerente_id INTEGER NOT NULL REFERENCES usuarios_gerentes(id) ON DELETE CASCADE,
    admin_id INTEGER NOT NULL REFERENCES usuarios_admin(id) ON DELETE CASCADE,
    login VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cnpj_cpf VARCHAR(20) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) DEFAULT 'usuario_final',
    ativo BOOLEAN DEFAULT TRUE,
    bloqueado_por_atraso BOOLEAN DEFAULT FALSE,
    data_bloqueio TIMESTAMP,
    ultimo_acesso TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Contas Recorrentes
CREATE TABLE IF NOT EXISTS contas_recorrentes (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES usuarios_admin(id) ON DELETE CASCADE,
    gerente_id INTEGER REFERENCES usuarios_gerentes(id) ON DELETE SET NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuarios_finais(id) ON DELETE CASCADE,
    cnpj_cpf_usuario VARCHAR(20) NOT NULL,
    valor_fixo DECIMAL(15, 2) NOT NULL,
    dia_vencimento INTEGER NOT NULL,
    descricao TEXT,
    ativa BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Auditoria (Logs)
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    tipo_usuario VARCHAR(50) NOT NULL,
    cnpj_cpf VARCHAR(20),
    acao VARCHAR(255) NOT NULL,
    dados_novos TEXT,
    dados_antigos TEXT,
    ip_origem VARCHAR(45),
    user_agent TEXT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_expiracao TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '2 years')
);

-- Tabela de Tickets de Suporte
CREATE TABLE IF NOT EXISTS tickets_suporte (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios_finais(id) ON DELETE CASCADE,
    usuario_login VARCHAR(255) NOT NULL,
    usuario_email VARCHAR(255) NOT NULL,
    tipo_problema VARCHAR(100) NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'ABERTO',
    prioridade VARCHAR(50) DEFAULT 'MEDIA',
    resposta_admin TEXT,
    admin_id INTEGER REFERENCES usuarios_admin(id) ON DELETE SET NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resposta TIMESTAMP,
    data_fechamento TIMESTAMP
);

-- Tabela de Alíquotas Padrão
CREATE TABLE IF NOT EXISTS aliquotas_padrao (
    id SERIAL PRIMARY KEY,
    imposto VARCHAR(50) NOT NULL,
    cfop VARCHAR(10),
    cst VARCHAR(10),
    aliquota_padrao DECIMAL(5, 2),
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Análises de Conformidade
CREATE TABLE IF NOT EXISTS analises_conformidade (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios_finais(id) ON DELETE CASCADE,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    operacoes_auditadas INTEGER,
    desvios_detectados INTEGER,
    economia_potencial DECIMAL(15, 2),
    score_conformidade DECIMAL(5, 2),
    alertas TEXT,
    recomendacoes TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Uploads de Arquivos
CREATE TABLE IF NOT EXISTS uploads_arquivos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios_finais(id) ON DELETE CASCADE,
    nome_arquivo VARCHAR(255) NOT NULL,
    tipo_arquivo VARCHAR(50) NOT NULL,
    tamanho_bytes INTEGER,
    hash_arquivo VARCHAR(255),
    status_processamento VARCHAR(50) DEFAULT 'PENDENTE',
    resultado_processamento TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMP
);

-- Índices para Performance
CREATE INDEX IF NOT EXISTS idx_usuarios_admin_login ON usuarios_admin(login);
CREATE INDEX IF NOT EXISTS idx_usuarios_gerentes_admin_id ON usuarios_gerentes(admin_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_finais_gerente_id ON usuarios_finais(gerente_id);
CREATE INDEX IF NOT EXISTS idx_logs_auditoria_usuario_id ON logs_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_auditoria_data_hora ON logs_auditoria(data_hora);
CREATE INDEX IF NOT EXISTS idx_tickets_usuario_id ON tickets_suporte(usuario_id);
CREATE INDEX IF NOT EXISTS idx_uploads_usuario_id ON uploads_arquivos(usuario_id);