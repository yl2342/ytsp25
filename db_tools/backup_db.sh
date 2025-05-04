#!/bin/bash

# Database backup script for Yale Trading Simulation Platform
# Creates a timestamped backup of the PostgreSQL database

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ytsp_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Get database connection info from .env file
if [ -f .env ]; then
    echo "Reading database configuration from .env file..."
    
    # Extract active DATABASE_URL line (not commented out)
    DB_URL=$(grep "^DATABASE_URL=" .env | sed 's/^DATABASE_URL=//' | sed 's/"//g' | sed "s/'//g" | sed 's/ //g')
    
    if [[ $DB_URL == postgresql://* ]]; then
        echo "PostgreSQL database detected"
        
        # Extract connection parameters from URL
        # Format: postgresql://username:password@host:port/dbname
        DB_USER=$(echo $DB_URL | sed -E 's/postgresql:\/\/([^:]+).*/\1/')
        DB_HOST=$(echo $DB_URL | sed -E 's/.*@([^:\/]+).*/\1/')
        DB_NAME=$(echo $DB_URL | sed -E 's/.*\/([^\/]+)$/\1/')
        
        echo "Creating backup of database '$DB_NAME' to $BACKUP_FILE"
        echo "You may be prompted for the database password"
        
        # Create the backup
        pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > $BACKUP_FILE
        
        if [ $? -eq 0 ]; then
            echo "Backup completed successfully!"
            echo "Backup saved to: $BACKUP_FILE"
            echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
        else
            echo "Error: Backup failed"
            exit 1
        fi
    else
        echo "Error: PostgreSQL database URL not found in .env file"
        echo "Make sure your .env file has an uncommented line like:"
        echo "DATABASE_URL=postgresql://username:password@localhost:5432/dbname"
        exit 1
    fi
else
    echo "Error: .env file not found"
    exit 1
fi
