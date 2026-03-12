# CxOne Scans with LOC

This project retrieves scan information from Checkmarx CxOne, including Lines of Code (LOC) metadata, and saves the data in both JSON and CSV formats.

## Prerequisites

- Python 3.9 or higher
- Checkmarx CxOne account with API access
- API key for CxOne API authentication

## Installation

1. **Clone the repository** (or create the project directory):
   ```bash
   mkdir -p E:\github.com\HappyY19\cxone_scans_with_loc
   cd E:\github.com\HappyY19\cxone_scans_with_loc
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment (Windows PowerShell)
   .venv\Scripts\Activate.ps1
   
   # Activate virtual environment (Windows Command Prompt)
   .venv\Scripts\activate.bat
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit the `get_scans_with_loc.py` file to configure your CxOne API credentials:

```python
configuration = Configuration(
    server_base_url="https://sng.ast.checkmarx.net",  # Replace with your CxOne server URL
    iam_base_url="https://sng.iam.checkmarx.net",  # Replace with your IAM URL
    token_url="https://sng.iam.checkmarx.net/auth/realms/happy/protocol/openid-connect/token",  # Token URL
    tenant_name="happy",  # Replace with your tenant name
    grant_type="refresh_token",
    api_key="***",  # Replace with your API key
)
```

### Required Configuration Parameters

- `server_base_url`: Your CxOne server URL (e.g., `https://your-region.ast.checkmarx.net`)
- `iam_base_url`: Your IAM server URL (e.g., `https://your-region.iam.checkmarx.net`)
- `token_url`: Full token endpoint URL (e.g., `https://your-region.iam.checkmarx.net/auth/realms/your-tenant/protocol/openid-connect/token`)
- `tenant_name`: Your CxOne tenant name
- `client_id`: Your API client ID
- `client_secret`: Your API client secret

## Usage

### Run the script

```bash
python get_scans_with_loc.py
```

## Results

The script will:

1. **Fetch all scans** from CxOne (with pagination)
2. **Filter scans** that have 'sast' in their engines list
3. **Retrieve LOC metadata** for SAST scans
4. **Save data** in two formats:
   - `scans_with_loc.json`: Complete data in JSON format
   - `scans_with_loc.csv`: Data in CSV format (excluding metadata column)

## Output Files

### JSON File (`scans_with_loc.json`)

Contains all scan information with the following fields:

- `id`: Scan ID
- `status`: Scan status (Queued, Running, Completed, Failed, Partial, Canceled)
- `project_id`: Project ID
- `project_name`: Project name
- `branch`: Git branch
- `commit_id`: Git commit ID
- `commit_tag`: Git commit tag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `initiator`: Scan initiator
- `user_agent`: User agent that initiated the scan
- `source_type`: Source type (github, zip, etc.)
- `source_origin`: Source origin (webapp, cli, jenkins, etc.)
- `tags`: Scan tags (dictionary)
- `metadata`: Scan metadata (dictionary)
- `engines`: List of engines used in the scan
- `loc`: Lines of Code (from SAST metadata)
- `file_count`: Number of files scanned (from SAST metadata)

### CSV File (`scans_with_loc.csv`)

Contains the same information as the JSON file **except the `metadata` column**.

### CSV Columns

```
id,status,project_id,project_name,branch,commit_id,commit_tag,created_at,updated_at,initiator,user_agent,source_type,source_origin,tags,engines,loc,file_count
```

## Statistics

After running, the script will display statistics such as:

- Total number of scans
- Number of scans with SAST engine
- Number of scans with LOC information
- Total lines of code across all scans

## Troubleshooting

### Common Issues

1. **Authentication errors**: Check your api_key, and token URL
2. **API rate limits**: The script handles batching to avoid rate limits
3. **Timeouts**: Increase the `timeout` parameter in the Configuration if needed

### Error Messages

- "Too many ids in url": This error is handled by the script by reducing batch size
- "Scan not found": Some scans may not have metadata available

## Dependencies

- `CheckmarxPythonSDK==1.7.9`
- `requests>=2.13.0`
- `zeep>=4.1.0`
- `typing-extensions>=3.6.2`
- `inflection>=0.5.1`
- `Deprecated>=1.2.13`
