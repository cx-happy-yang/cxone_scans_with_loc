import json
import csv
from CheckmarxPythonSDK.api_client import ApiClient
from CheckmarxPythonSDK.configuration import Configuration
from CheckmarxPythonSDK.CxOne.scansAPI import ScansAPI
from CheckmarxPythonSDK.CxOne.sastScanMetadataServiceAPI import SastScanMetadataServiceAPI


def get_all_scans(scans_api):
    """
    Get all scans with pagination
    """
    all_scans = []
    offset = 0
    limit = 100  # Number of items per page

    while True:
        print(f"Fetching scans, offset={offset}, limit={limit}")
        scans_collection = scans_api.get_a_list_of_scans(offset=offset, limit=limit)

        if not scans_collection.scans:
            break

        for scan in scans_collection.scans:
            scan_dict = {
                "id": scan.id,
                "status": scan.status,
                "project_id": scan.project_id,
                "project_name": scan.project_name,
                "branch": scan.branch,
                "commit_id": scan.commit_id,
                "commit_tag": scan.commit_tag,
                "created_at": scan.created_at,
                "updated_at": scan.updated_at,
                "initiator": scan.initiator,
                "user_agent": scan.user_agent,
                "source_type": scan.source_type,
                "source_origin": scan.source_origin,
                "tags": scan.tags,
                "metadata": scan.metadata,
                "engines": scan.engines,
                "loc": None,  # Will be filled later
                "file_count": None,  # Will be filled later
            }
            all_scans.append(scan_dict)

        print(f"Fetched {len(scans_collection.scans)} scans, total {scans_collection.total_count} scans")

        # Check if there are more pages
        if offset + limit >= scans_collection.total_count:
            break

        offset += limit

    return all_scans


def add_loc_to_scans(scans, metadata_api):
    """
    Get LOC information for each scan and add it to scan data
    Only get LOC for scans that have 'sast' in their engines list
    """
    
    # Filter scans that have 'sast' in engines
    sast_scans = [scan for scan in scans if scan["engines"] and "sast" in scan["engines"]]
    print(f"Found {len(sast_scans)} scans with 'sast' engine out of {len(scans)} total scans")
    
    # Get metadata in batches of 20 scan_ids (API limit)
    batch_size = 20
    for i in range(0, len(sast_scans), batch_size):
        batch_scans = sast_scans[i:i + batch_size]
        scan_ids = [scan["id"] for scan in batch_scans]

        print(f"Getting LOC information for scans {i + 1} to {i + len(batch_scans)}")

        try:
            scan_info_collection = metadata_api.get_metadata_of_scans(scan_ids=scan_ids)

            # Create mapping from scan_id to loc
            loc_map = {}
            file_count_map = {}
            for scan_info in scan_info_collection.scans:
                loc_map[scan_info.scan_id] = scan_info.loc
                file_count_map[scan_info.scan_id] = scan_info.file_count

            # Update scans data
            for scan in batch_scans:
                scan["loc"] = loc_map.get(scan["id"])
                scan["file_count"] = file_count_map.get(scan["id"])

        except Exception as e:
            print(f"Error getting metadata: {e}")
            # If error, try to get one by one
            for scan in batch_scans:
                try:
                    scan_info = metadata_api.get_metadata_of_scan(scan_id=scan["id"])
                    scan["loc"] = scan_info.loc
                    scan["file_count"] = scan_info.file_count
                except Exception as e2:
                    print(f"Error getting metadata for scan {scan['id']}: {e2}")
                    scan["loc"] = None
                    scan["file_count"] = None

    return scans


def save_to_csv(scans, output_file="scans_with_loc.csv"):
    """
    Save scans to CSV file, excluding the 'metadata' column
    """
    if not scans:
        print("No scans to save to CSV")
        return
    
    # Get all field names except 'metadata'
    fieldnames = [key for key in scans[0].keys() if key != "metadata"]
    
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for scan in scans:
            # Create a copy of scan data without 'metadata'
            row = {key: value for key, value in scan.items() if key != "metadata"}
            
            # Convert list fields to string for CSV
            if row.get("engines"):
                row["engines"] = ",".join(row["engines"])
            if row.get("tags"):
                row["tags"] = json.dumps(row["tags"])
            
            writer.writerow(row)
    
    print(f"Data saved to {output_file}")


def main():
    print("Starting to get all scans...")
    
    # Create Configuration object
    configuration = Configuration(
        server_base_url="https://sng.ast.checkmarx.net",  # Replace with your CxOne server URL
        iam_base_url="https://sng.iam.checkmarx.net",  # Replace with your IAM URL
        token_url="https://sng.iam.checkmarx.net/auth/realms/happy/protocol/openid-connect/token",  # Token URL
        tenant_name="happy",  # Replace with your tenant name
        grant_type="client_credentials",
        client_id="checkmarx-python-sdk",  # Replace with your client ID
        client_secret="***"  # Replace with your client secret
    )
    
    # Put configuration in a list
    config_list = [configuration]
    
    # Use the first configuration from the list
    configuration = config_list[0]
    
    # Create api_client
    api_client = ApiClient(configuration=configuration)
    
    # Create API instances with api_client
    scans_api = ScansAPI(api_client=api_client)
    metadata_api = SastScanMetadataServiceAPI(api_client=api_client)
    
    all_scans = get_all_scans(scans_api)
    print(f"Total {len(all_scans)} scans fetched")

    if all_scans:
        print("Starting to get LOC information...")
        all_scans = add_loc_to_scans(all_scans, metadata_api)

        # Save to JSON file
        json_output_file = "scans_with_loc.json"
        with open(json_output_file, "w", encoding="utf-8") as f:
            json.dump(all_scans, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {json_output_file}")

        # Save to CSV file (excluding metadata column)
        csv_output_file = "scans_with_loc.csv"
        save_to_csv(all_scans, csv_output_file)

        # Print statistics
        scans_with_loc = [s for s in all_scans if s["loc"] is not None]
        print(f"\nStatistics:")
        print(f"  - Total scans: {len(all_scans)}")
        print(f"  - Scans with LOC info: {len(scans_with_loc)}")
        if scans_with_loc:
            total_loc = sum(s["loc"] for s in scans_with_loc)
            print(f"  - Total lines of code (LOC): {total_loc:,}")
    else:
        print("No scans fetched")


if __name__ == "__main__":
    main()
