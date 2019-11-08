FROM mindsdb:latest

RUN pip install --no-cache-dir mindsdb_server

# Use bash cmd entry point
CMD ["bash"]
CMD python -c "exec(\"import mindsdb_server \nmindsdb_server.start_server()\")"
