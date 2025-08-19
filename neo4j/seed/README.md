# Neo4j Seed Directory

This directory can contain a `graph.dump` file that will be automatically loaded when the Neo4j container starts with an empty database.

## Usage

To pre-populate the database with data:

1. Create a Neo4j dump file using:
   ```bash
   neo4j-admin database dump --database=neo4j --to-path=/path/to/output graph.dump
   ```

2. Place the `graph.dump` file in this directory

3. When the container starts, it will automatically load this data if the database is empty

## Note

This is optional. The Auto-KG application can work with an empty database and will populate it as needed through the web interface or API calls.