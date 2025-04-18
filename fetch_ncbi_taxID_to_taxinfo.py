#!/usr/bin/env python3
"""
fetch_ncbi_taxID_to_taxinfo.py

This script reads a TSV file containing a "TaxID" column and retrieves the corresponding
taxonomy data for each TaxID from NCBI. It extracts the lineage information, including
the ID and name for each taxonomic level (e.g., kingdom, phylum, class, etc.).

Usage:
    python fetch_ncbi_taxID_to_taxinfo.py --input input_file.tsv --output output_file.tsv

Dependencies:
    - pandas
    - subprocess
    - argparse
    - time
    - sys
    - io
"""

import subprocess
import pandas as pd
from io import StringIO
import time
import argparse
import sys

def fetch_taxonomy_data(taxid):
    """
    Fetch taxonomy lineage data for a given TaxID using NCBI's datasets command.

    Args:
        taxid (str): The NCBI Taxonomy ID.

    Returns:
        dict: A dictionary containing taxonomy levels with their corresponding IDs and names.
              Example:
              {
                  'kingdom_id': '2759',
                  'kingdom_name': 'Eukaryota',
                  'phylum_id': '33154',
                  'phylum_name': 'Proteobacteria',
                  ...
              }
              Returns None if an error occurs.
    """
    try:
        # Construct the command to fetch taxonomy data
        command = [
            'datasets', 'summary', 'taxonomy', 'taxon', str(taxid), '--as-json-lines'
        ]

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # print(result)

        if result.returncode != 0:
            print(f"Command failed for TaxID {taxid} with exit status {result.returncode}", file=sys.stderr)
            print(f"stderr: {result.stderr}", file=sys.stderr)
            return None

        # Parse the JSON output
        import json
        taxonomy_json = json.loads(result.stdout)

        # print(f'Taxonomy JSON for TaxID {taxid}:' + str(taxonomy_json))

        taxonomy = taxonomy_json.get('taxonomy', [])
        classification = taxonomy.get('classification', {})
        print(f'Lineage for TaxID {taxid}:' + str(classification))

        taxonomy_info = {}
        # Define the taxonomic ranks of interest in hierarchical order
        taxonomic_ranks = ['superkingdom', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']

        for rank in taxonomic_ranks:
            print(f"Rank: {rank}")
            # Find the taxon in the lineage matching the current rank
            taxon = classification.get(rank)
            print(f"Taxon: {taxon}")
            if taxon:
                taxonomy_info[f"{rank}_id"] = taxon['id']
                taxonomy_info[f"{rank}_name"] = taxon['name']
                # print(f"ID: {taxonomy_info[f'{rank}_id']}, Name: {taxonomy_info[f'{rank}_name']}")
            else:
                taxonomy_info[f"{rank}_id"] = 'None'
                taxonomy_info[f"{rank}_name"] = 'None'
                # print(f"ID: {taxonomy_info[f'{rank}_id']}, Name: {taxonomy_info[f'{rank}_name']}")

        return taxonomy_info

    except subprocess.CalledProcessError as e:
        print(f"Error fetching data for TaxID {taxid}: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error for TaxID {taxid}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error for TaxID {taxid}: {e}", file=sys.stderr)
        return None

def process_taxids(taxids, max_retries=3, delay=2):
    """
    Process a list of TaxIDs to fetch their taxonomy data with retries.

    Args:
        taxids (list): List of TaxIDs to process.
        max_retries (int): Maximum number of retries for failed TaxIDs.
        delay (int): Delay in seconds before retrying.

    Returns:
        pd.DataFrame: A DataFrame containing taxonomy information for each TaxID.
    """
    final_data = []
    failed_taxids = {taxid: 0 for taxid in taxids}

    while failed_taxids:
        current_failed = {}
        for taxid, retries in failed_taxids.items():
            if retries < max_retries:
                taxonomy_info = fetch_taxonomy_data(taxid)
                if taxonomy_info:
                    taxonomy_info['TaxID'] = taxid
                    final_data.append(taxonomy_info)
                else:
                    current_failed[taxid] = retries + 1
            else:
                # Append None values after exhausting retries
                taxonomy_info = {
                    'kingdom_id': 'None', 'kingdom_name': 'None',
                    'phylum_id': 'None', 'phylum_name': 'None',
                    'class_id': 'None', 'class_name': 'None',
                    'order_id': 'None', 'order_name': 'None',
                    'family_id': 'None', 'family_name': 'None',
                    'genus_id': 'None', 'genus_name': 'None',
                    'species_id': 'None', 'species_name': 'None',
                    'TaxID': taxid
                }
                final_data.append(taxonomy_info)
        failed_taxids = current_failed
        if failed_taxids:
            print(f"Retrying {len(failed_taxids)} failed TaxIDs after {delay} seconds...")
            time.sleep(delay)

    return pd.DataFrame(final_data)

def main():
    """
    Main function to parse arguments and execute the taxonomy data fetching process.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Fetch taxonomy information for given TaxIDs.")
    parser.add_argument('--input', required=True, help='Path to the input TSV file containing "TaxID" column.')
    parser.add_argument('--output', required=True, help='Path to the output TSV file to save taxonomy information.')
    args = parser.parse_args()

    # Read the input TSV file
    try:
        df_input = pd.read_csv(args.input, sep='\t')
    except FileNotFoundError:
        print(f"Input file {args.input} not found.", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Input file {args.input} is empty.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if "TaxID" column exists
    if 'TaxID' not in df_input.columns:
        print(f'"TaxID" column not found in the input file.', file=sys.stderr)
        sys.exit(1)

    # Extract unique TaxIDs and drop NaN values
    unique_taxids = df_input['TaxID'].dropna().unique().tolist()

    if not unique_taxids:
        print("No valid TaxIDs found in the input file.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(unique_taxids)} unique TaxIDs...")

    # Process TaxIDs to fetch taxonomy information
    taxonomy_df = process_taxids(unique_taxids)

    # Merge the taxonomy information back to the original DataFrame
    df_output = pd.merge(df_input, taxonomy_df, on='TaxID', how='left')

    # Replace NaN values with 'None' for taxonomy columns
    taxonomy_columns = [col for col in df_output.columns if col not in df_input.columns]
    df_output[taxonomy_columns] = df_output[taxonomy_columns].fillna('None')

    # Save the output to a TSV file
    try:
        df_output.to_csv(args.output, sep='\t', index=False)
        print(f"Taxonomy information successfully saved to {args.output}")
    except Exception as e:
        print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
