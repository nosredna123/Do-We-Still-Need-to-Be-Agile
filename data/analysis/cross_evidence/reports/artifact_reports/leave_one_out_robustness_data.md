## What it is
- **Artifact ID**: leave_one_out_robustness_data  
- **Unit of Analysis**: analysis_result  
- **Row Count (n_total)**: 7  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-figure-data-v1  

## How it was built
The artifact was constructed by processing data from a CSV file located at `data/analysis/cross_evidence/figure_data/leave_one_out_robustness.csv` using the script `08_cross_evidence_engine.py`. It includes 9 columns and 7 rows of data related to various analysis results.

## Narrative binding
The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the robustness of the analysis results.

## What the current data actually shows
- **Original Coefficient**:  
  - Max: -0.2647382010005621  
  - Mean: -0.5207027851032128  
  - Median: -0.5207396621025063  
  - Min: -0.7284815485795703  
  - n_valid: 7  
- **Coefficient Min**:  
  - Max: -0.5699124492412846  
  - Mean: -0.6725534806053813  
  - Median: -0.6795816917193728  
  - Min: -0.7810117949610702  
  - n_valid: 7  
- **Coefficient Max**:  
  - Max: -0.174630713288139  
  - Mean: -0.43426754742467366  
  - Median: -0.448223234903528  
  - Min: -0.6725037594933305  
  - n_valid: 7  
- **P-value Max**:  
  - Max: 0.5682629857514974  
  - Mean: 0.19260818765647383  
  - Median: 0.1245124600803049  
  - Min: 0.0117870367777658  
  - n_valid: 7  
- **LOO Support Share**:  
  - Max: 1.0  
  - Mean: 0.4795918367346938  
  - Median: 0.1428571428571428  
  - Min: 0.0714285714285714  
  - n_valid: 7  

## Contribution assessment
The contribution assessment is inconclusive due to the variability in the p-values and the range of coefficients. The maximum p-value of 0.5682629857514974 suggests a lack of statistical significance in the findings.

## Known limitations
- The data is based on a small sample size (n_total = 7), which may limit the generalizability of the results.
- All data points are valid, but the maximum p-value indicates potential non-significance in the results.
