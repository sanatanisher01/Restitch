FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory and make scripts executable
RUN mkdir -p uploads && \
    chmod +x entrypoint.sh deploy.sh

# Set environment variables
ENV FLASK_APP=restitch.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Create non-root user
RUN useradd -m -u 1000 restitch && chown -R restitch:restitch /app
USER restitch

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "restitch:app"]