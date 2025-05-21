# Streamlit Cloud Deployment Instructions

This section explains how to deploy the MedCampus application to Streamlit Community Cloud.

## Prerequisites

1. Create a [Streamlit Community Cloud](https://streamlit.io/cloud) account
2. Link your GitHub account to Streamlit Cloud
3. Fork or push this repository to your GitHub account

## Deployment Steps

1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Click on "New app" button
3. Select your GitHub repository, branch, and the main file path:
   - Repository: Your fork of this repository
   - Branch: `main` (or your preferred branch)
   - Main file path: `src/app.py`
4. In the "Advanced settings" section:
   - Add your secret variables (same as in .streamlit/secrets.toml)
   - The system will automatically detect and install dependencies from:
     - requirements.txt (Python dependencies)
     - packages.txt (System packages)

## Required Files for Deployment

The repository includes these essential files for deployment:

1. `requirements.txt` - Lists all Python package dependencies
2. `packages.txt` - Lists minimal system dependencies
3. `.streamlit/config.toml` - Streamlit configuration
4. `.streamlit/secrets.toml` - Secret variables (not included in repo; you'll add these in the Streamlit Cloud settings)

## Setting Up Secrets in Streamlit Cloud

In the Streamlit Cloud deployment interface, add the following secrets:

```
OPENAI_API_KEY = "your-openai-key"
ANTHROPIC_API_KEY = "your-anthropic-key"
GOOGLE_API_KEY = "your-google-key"
TAVILY_API_KEY = "your-tavily-key"
# Add other API keys as needed

# User authentication credentials
[usernames]
admin = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # admin
professor = "1c4a19e75e705aee9894355a1d5c81c93e9ad6339e7e3a36b8c8192b6c79c8cf"  # professor123
aluno = "0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c"  # aluno123
```

## Troubleshooting

### Common Issues

#### HTML Reports Instead of PDF

The application now uses HTML reports instead of PDF generation to avoid dependency issues with libraries like WeasyPrint that require system libraries such as libpango. This approach has several benefits:

1. More reliable deployment with fewer dependencies
2. HTML reports can be easily converted to PDF using any web browser's print function
3. HTML reports can be styled and customized more easily
4. Avoids issues with missing system libraries on Streamlit Cloud

Users can download the HTML report and convert it to PDF by:

1. Opening the HTML file in any web browser
2. Using the browser's print function (Ctrl+P or Cmd+P)
3. Selecting "Save as PDF" option

#### Other Troubleshooting Steps

- If the app fails to deploy, check the build logs for errors
- Ensure all dependencies are correctly listed in requirements.txt
- Make sure all system dependencies are listed in packages.txt
- Verify that all necessary secrets are added in the Streamlit Cloud settings
