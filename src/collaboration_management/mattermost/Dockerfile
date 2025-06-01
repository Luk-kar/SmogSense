FROM mattermost/mattermost-team-edition:10.0

# Switch to root user to perform administrative tasks
USER root

# Install gosu
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Copy the entrypoint script into the container
COPY mattermost-entry.sh /mattermost-entry.sh

# Make the script executable
RUN chmod +x /mattermost-entry.sh

# Switch back to the mattermost user
USER mattermost

# (Optional) Expose port 8065 if not already exposed
EXPOSE 8065

# Set the entrypoint to your script
ENTRYPOINT ["/mattermost-entry.sh"]
