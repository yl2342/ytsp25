Single-database configuration for Flask.

# Database Migrations

This directory contains database migrations for the Yale Trading Simulation Platform.

## About Migrations

Migrations allow for version control of the database schema. They provide a way to incrementally apply changes to the database structure while preserving existing data.

## How Migrations Work

1. When you make changes to the models in the application code
2. You generate a migration script that captures those changes
3. The migration script can be applied to update the database schema
4. The migration script can also be reversed to roll back changes

## Managing Migrations

### Creating a New Migration

After modifying models, create a new migration:

```bash
flask db migrate -m "Description of changes"
```

This will generate a new migration script in the `versions` directory.

### Applying Migrations

To apply pending migrations to the database:

```bash
flask db upgrade
```

### Rolling Back Migrations

To revert to a previous version:

```bash
flask db downgrade
```

### Viewing Migration Status

To see the current migration status:

```bash
flask db current
flask db history
```

## Migration Directory Structure

- `versions/`: Contains individual migration scripts
- `alembic.ini`: Configuration for the migration engine
- `env.py`: Environment configuration for migrations
- `script.py.mako`: Template for generating migration scripts

## Notes

- Always back up your database before applying migrations in production
- Review migration scripts before applying them
- Test migrations in a development environment first
- Don't modify existing migrations that have been applied to production

---

For more information on database migrations with Flask-Migrate, see:
https://flask-migrate.readthedocs.io/
