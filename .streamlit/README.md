# Streamlit Secrets Configuration

This directory contains the `secrets.toml` file required for the application to access API keys, user credentials, and other sensitive configuration values.

## Format

The `secrets.toml` file should follow the TOML format with key-value pairs:

```toml
# API Keys for various LLM providers
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
GOOGLE_API_KEY="your-google-api-key"
TAVILY_API_KEY="your-tavily-api-key"
GROQ_API_KEY="your-groq-api-key"
PERPLEXITY_API_KEY="your-perplexity-api-key"

# LangSmith configuration (optional, for tracing)
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your-langsmith-api-key"
LANGSMITH_PROJECT="your-project-name"

# User authentication credentials
# These should be SHA-256 hashed passwords
[usernames]
admin = "hashed-password-for-admin"
user1 = "hashed-password-for-user1"
user2 = "hashed-password-for-user2"
```

## Authentication Credentials

User passwords are stored as SHA-256 hashes for security. To generate a new hashed password, you can use the following Python code:

```python
import hashlib

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Example:
make_hash("admin123")  # Returns the SHA-256 hash for "admin123"
```

## Deployment

When deploying to Streamlit Cloud, you'll need to add these same secrets to the Streamlit Cloud secrets manager in your application settings.
