#!/bin/bash

# ================================================================
# Script: fetch_taxID.sh
# Purpose: Fetch the TaxID and Scientific Name for protein IDs using
#          NCBI E-utilities (esearch, elink, efetch, and xtract).
# 
# Input: A text file containing a list of protein IDs (one per line).
# Output: A TSV file with columns: ProteinID, ScientificName, TaxID.
# 
# Note: This script is distinct from other taxonomy-fetching scripts
#       that utilize the NCBI CLI toolkit.
# ================================================================

# ------------------------------
# Check for Proper Usage
# ------------------------------

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $0 <input_file.txt> [output_file.tsv]"
    exit 1
fi

# ------------------------------
# Assign Input and Output Files
# ------------------------------

# Input file containing protein IDs
input_file="$1"

# Output file: Use provided output file, or create one based on input basename
if [ "$#" -eq 2 ]; then
    output_file="$2"
else
    # Extract basename without extension and append .tsv
    base_name=$(basename "$input_file")
    output_file="${base_name%.*}.tsv"
fi

# ------------------------------
# Initialize Output and Log Files
# ------------------------------

# Empty the output file if it exists or create a new one
> "$output_file"

# Write header to the output file
echo -e "ProteinID\tScientificName\tTaxID" > "$output_file"

# Initialize a log file to capture processing details and errors
log_file="fetch_taxID.log"
> "$log_file"

# ------------------------------
# Read All Protein IDs into an Array
# ------------------------------

mapfile -t protein_ids < "$input_file"

# ------------------------------
# Iterate Over the Array
# ------------------------------

for protein_id in "${protein_ids[@]}"; do
    # Remove any carriage return characters
    protein_id=$(echo "$protein_id" | tr -d '\r')

    # Skip empty lines
    if [ -z "$protein_id" ]; then
        echo "Info: Skipping empty line." >> "$log_file"
        continue
    fi

    echo "Info: Processing Protein ID: $protein_id" >> "$log_file"

    # Fetch ScientificName and TaxID
    result=$(esearch -db protein -query "$protein_id" \
             | elink -target taxonomy \
             | efetch -format docsum \
             | xtract -pattern DocumentSummary -element ScientificName,TaxId 2>>"$log_file")

    # Check if the result is non-empty
    if [ -z "$result" ]; then
        echo "Error: No data found for Protein ID: $protein_id" >> "$log_file"
        echo -e "$protein_id\tError\tError" >> "$output_file"
        continue
    fi

    # Split the result into ScientificName and TaxID
    scientific_name=$(echo "$result" | awk -F'\t' '{print $1}')
    taxid=$(echo "$result" | awk -F'\t' '{print $2}')

    # Validate extracted data
    if [ -z "$scientific_name" ] || [ -z "$taxid" ]; then
        echo "Error: Incomplete data for Protein ID: $protein_id" >> "$log_file"
        echo -e "$protein_id\tError\tError" >> "$output_file"
        continue
    fi

    # Append the fetched data to the output file
    echo -e "$protein_id\t$scientific_name\t$taxid" >> "$output_file"
    echo "Success: Fetched data for Protein ID: $protein_id" >> "$log_file"
done

# ------------------------------
# Completion Message
# ------------------------------

echo "Processing complete. Results saved to '$output_file'. See '$log_file' for details."