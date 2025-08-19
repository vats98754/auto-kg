FROM neo4j:5.22
# Expect NEO4J_AUTH env var to be provided (e.g., neo4j/password)
COPY entrypoint.sh /entrypoint.sh
COPY seed/ /var/lib/neo4j/import/seed/
RUN chmod +x /entrypoint.sh
EXPOSE 7474 7687
ENTRYPOINT ["/entrypoint.sh"]
