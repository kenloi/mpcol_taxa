Code and Software Submission: Taxa analysis pipeline
=====================================================

1. System requirements
   --------------------
   • OS: Linux (tested on Ubuntu 20.04/22.04-compatible; actual: 5.15.0-135-generic kernel on Ubuntu, x86_64)
   • Shell: Bash (default: /bin/bash)
   • NCBI Datasets CLI ≥ 16.3.0
   • Python ≥ 3.8
   – Required packages: requests (≥ 2.25), pandas (≥ 1.2), biopython (≥ 1.79)
   – Install via: pip install -r requirements.txt
   • RAM: ≥ 4 GB
   • CPU: x86_64 architecture (tested on multi-core Intel system)

2. Installation guide
   --------------------
   1. Clone this repo (or unzip the submission archive).  
   2. (Optional) Create and activate a conda environment:  
      ```bash
      conda create -n taxa python=3.9
      conda activate taxa
      pip install -r requirements.txt
      ```
   3. Install NCBI Datasets CLI per NCBI docs at https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/download-and-install/.  
   **Typical install time:** ~5 min on a “normal” desktop.

3. Demo
   ------
   1. Prepare a small test list of protein IDs, e.g. `sample_ids.txt`.  
   2. Run taxID fetch:  
      ```bash
      ./fetch_taxID.sh sample_ids.txt sample_taxIDs.tsv
      ```  
      **Expected output:** tab‑delimited `sample_taxIDs.tsv`; log in `fetch_taxID.log`.  
   3. Run taxinfo lookup:  
      ```bash
      python fetch_ncbi_taxID_to_taxinfo.py sample_taxIDs.tsv \
          --out sample_taxinfo.json
      ```  
      **Expected output:** JSON with full lineage for each ID.  
   4. Open `mcpol_taxa.ipynb` to see parsing, locus‑tag annotation and summary tables.  
   **Demo run time:** ~2 min on 4‑core, 8 GB RAM.

4. Instructions for use
   ----------------------
   1. Edit `fetch_taxID.sh` to point at your own ID file.  
   2. After `fetch_taxID.sh` completes, any missing IDs can be added manually in the TSV.  
   3. Run `fetch_ncbi_taxID_to_taxinfo.py` on the complete ID list.  
   4. Open the notebook to merge lineage info and add locus tags.  
   5. Outputs (`*.tsv`, `*.json`, notebook HTML) can be downstream‑parsed or visualized.

5. (OPTIONAL) Reproduction
   ------------------------
   To reproduce all figures and tables in the manuscript, run the full notebook:
   ```bash
   jupyter nbconvert --to html mcpol_taxa.ipynb