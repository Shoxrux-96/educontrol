-- EDU Control Pro Database Schema
-- PostgreSQL 16+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUM TYPES
-- ============================================
CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'viewer');
CREATE TYPE computer_status AS ENUM ('online', 'offline', 'busy', 'locked', 'maintenance');
CREATE TYPE policy_type AS ENUM ('internet', 'application', 'usb', 'print_screen');
CREATE TYPE policy_target_type AS ENUM ('computer', 'group', 'all');
CREATE TYPE command_status AS ENUM ('pending', 'sent', 'delivered', 'executed', 'failed');
CREATE TYPE message_type AS ENUM ('info', 'warning', 'critical');
CREATE TYPE event_severity AS ENUM ('info', 'warning', 'critical');

-- ============================================
-- USERS
-- ============================================
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        user_role NOT NULL DEFAULT 'viewer',
    full_name   VARCHAR(100),
    is_active   BOOLEAN DEFAULT TRUE,
    last_login  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    created_by  UUID REFERENCES users(id)
);

-- ============================================
-- COMPUTER GROUPS
-- ============================================
CREATE TABLE computer_groups (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    color       VARCHAR(7),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- COMPUTERS
-- ============================================
CREATE TABLE computers (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    hostname    VARCHAR(255),
    ip_address  INET,
    mac_address MACADDR,
    group_id    UUID REFERENCES computer_groups(id),
    os_version  VARCHAR(100),
    agent_version VARCHAR(20),
    status      computer_status DEFAULT 'offline',
    last_seen   TIMESTAMPTZ,
    cpu_model   VARCHAR(200),
    ram_gb      SMALLINT,
    disk_gb     SMALLINT,
    current_user VARCHAR(100),
    cpu_usage   SMALLINT,
    ram_usage   SMALLINT,
    disk_usage  SMALLINT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_computers_status ON computers(status);
CREATE INDEX idx_computers_group ON computers(group_id);

-- ============================================
-- POLICIES
-- ============================================
CREATE TABLE policies (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    policy_type policy_type NOT NULL,
    config      JSONB NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE policy_assignments (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_id   UUID REFERENCES policies(id) ON DELETE CASCADE,
    target_type policy_target_type NOT NULL,
    target_id   UUID,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_policy_assignments_target ON policy_assignments(target_type, target_id);

-- ============================================
-- COMMANDS
-- ============================================
CREATE TABLE commands (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    computer_id UUID REFERENCES computers(id) ON DELETE CASCADE,
    command_type VARCHAR(50) NOT NULL,
    payload     JSONB,
    status      command_status DEFAULT 'pending',
    sent_by     UUID REFERENCES users(id),
    sent_at     TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    result      JSONB
);

CREATE INDEX idx_commands_computer ON commands(computer_id);
CREATE INDEX idx_commands_status ON commands(status);

-- ============================================
-- MESSAGES
-- ============================================
CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       VARCHAR(200),
    body        TEXT NOT NULL,
    message_type message_type DEFAULT 'info',
    sender_id   UUID REFERENCES users(id),
    target_type policy_target_type NOT NULL,
    target_id   UUID,
    sent_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SCREENSHOTS
-- ============================================
CREATE TABLE screenshots (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    computer_id UUID REFERENCES computers(id) ON DELETE CASCADE,
    file_path   VARCHAR(500) NOT NULL,
    file_size   INTEGER,
    taken_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_screenshots_computer ON screenshots(computer_id, taken_at);

-- ============================================
-- AUDIT LOGS (immutable, partitioned)
-- ============================================
CREATE TABLE audit_logs (
    id          BIGSERIAL,
    event_type  VARCHAR(50) NOT NULL,
    severity    event_severity DEFAULT 'info',
    computer_id UUID REFERENCES computers(id),
    user_id     UUID REFERENCES users(id),
    description TEXT NOT NULL,
    extra_data  JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE audit_logs_2025_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE audit_logs_2025_02 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
CREATE TABLE audit_logs_2025_03 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
CREATE TABLE audit_logs_2025_04 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE audit_logs_2025_05 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
CREATE TABLE audit_logs_2025_06 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');
CREATE TABLE audit_logs_2025_07 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE audit_logs_2025_08 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
CREATE TABLE audit_logs_2025_09 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE audit_logs_2025_10 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
CREATE TABLE audit_logs_2025_11 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
CREATE TABLE audit_logs_2025_12 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Create a default partition for future data
CREATE TABLE audit_logs_default PARTITION OF audit_logs DEFAULT;

CREATE INDEX idx_audit_logs_computer_created ON audit_logs(computer_id, created_at);
CREATE INDEX idx_audit_logs_event_created ON audit_logs(event_type, created_at);

-- ============================================
-- SEED DATA
-- ============================================
INSERT INTO users (username, email, password_hash, role, full_name)
VALUES (
    'admin',
    'admin@educontrol.local',
    -- Password: Admin123! (argon2 hash, replace with actual)
    '$argon2id$v=19$m=65536,t=3,p=4$...replace...',
    'super_admin',
    'System Administrator'
);
