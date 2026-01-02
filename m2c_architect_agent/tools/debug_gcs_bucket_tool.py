import os
import sys
from dotenv import load_dotenv

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# --- Pre-flight Check ---
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
if not GCS_BUCKET_NAME:
    print("--- ERROR: Missing GCS_BUCKET_NAME ---", file=sys.stderr)
    print(f"Attempted to load .env file from: {dotenv_path}", file=sys.stderr)
    print("Please ensure GCS_BUCKET_NAME is set in your .env file (e.g., GCS_BUCKET_NAME='adk-agent-test').", file=sys.stderr)
    sys.exit(1)

# Import the tool function directly
from m2c_architect_agent.tools.gcs_bucket_tool import upload_docx_to_gcs

def run_tool_test():
    """
    Runs a direct test of the upload_docx_to_gcs tool outside the agent framework.
    """
    print("--- Starting Direct Tool Test for gcs_bucket_tool.py ---")

    # --- Mock Data ---
    test_title = "GCS Direct Tool Test Document"
    test_content = """
## GCS Test Section
This is a test document created by a standalone debug script for GCS upload.

- Item 1: GCS Upload
- Item 2: Success

If you see this document in the GCS bucket, the tool's core functionality is working.
"""
    destination_folder = "DAT"

    print(f"Attempting to upload document '{test_title}' to gs://{GCS_BUCKET_NAME}/{destination_folder}/")

    try:
        result = upload_docx_to_gcs(
            document_title=test_title, 
            document_content=test_content,
            bucket_name=GCS_BUCKET_NAME,
            destination_folder=destination_folder
        )
        if "an error occurred" in result.lower():
            raise Exception(result)
        print("\n--- Tool Execution Successful ---")
        print(f"Result: {result}")
    except Exception as e:
        print("\n--- Tool Execution FAILED ---")
        print(f"An error occurred: {e}")
        print("\nTroubleshooting tips:\n1. **Permissions**: Ensure the authenticated user/service account has the 'Storage Object Creator' role on the bucket.\n2. **Bucket Name**: Verify that GCS_BUCKET_NAME in your .env file matches an existing bucket.\n3. **Authentication**: Ensure you have run `gcloud auth application-default login`.")
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    run_tool_test()