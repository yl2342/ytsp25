-- Yale Trading Simulation Platform (YTSP) Database Setup Script
-- This script will drop and recreate the database and user

-- Check if database exists and drop it if it does
DROP DATABASE IF EXISTS ytsp;

-- Check if user exists and drop it if it does
DROP USER IF EXISTS ytsp_server;

-- Create fresh database and user
CREATE USER ytsp_server WITH PASSWORD 'cpsc519sp25';
CREATE DATABASE ytsp;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ytsp TO ytsp_server;

-- Connect to the ytsp database to set schema privileges
\c ytsp

-- Grant schema privileges (this needs to be run after connecting to the database)
GRANT ALL ON SCHEMA public TO ytsp_server;

-- Completion message
\echo 'Database setup complete. The ytsp database and ytsp_server user have been created.'
\echo 'Remember to update your .env file with:'
\echo 'DATABASE_URL=postgresql://ytsp_server:cpsc519sp25@localhost:5432/ytsp' 