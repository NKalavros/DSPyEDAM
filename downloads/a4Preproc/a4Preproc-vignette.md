::: {.container-fluid .main-container}
::: row
::: {.col-xs-12 .col-sm-4 .col-md-3}
::: {#TOC .tocify}
:::
:::

::: {.toc-content .col-xs-12 .col-sm-8 .col-md-9}
::: {#header}
# Vignette of the a4Preproc package {#vignette-of-the-a4preproc-package .title .toc-ignore}

#### 2025-04-15 {#section .date}
:::

::: {#introduction .section .level1}
# [1]{.header-section-number} Introduction

This document explains the functionalities available in the
**a4Preproc** package.

This package contains utility functions to pre-process data for the
Automated Affymetrix Array Analysis suite of packages.
:::

::: {#get-feature-annotation-for-an-expressionset .section .level1}
# [2]{.header-section-number} Get feature annotation for an ExpressionSet

The feature annotation for a specific dataset, as required by the
pipeline is extracted with the `addGeneInfo` function.

``` r
library(ALL)
data(ALL)
a4ALL <- addGeneInfo(eset = ALL)
print(head(fData(a4ALL)))
```

    ##           ENTREZID       ENSEMBLID  SYMBOL
    ## 1000_at       5595 ENSG00000102882   MAPK3
    ## 1001_at       7075 ENSG00000066056    TIE1
    ## 1002_f_at     1557 ENSG00000165841 CYP2C19
    ## 1003_s_at      643 ENSG00000160683   CXCR5
    ## 1004_at        643 ENSG00000160683   CXCR5
    ## 1005_at       1843 ENSG00000120129   DUSP1
    ##                                                                  GENENAME
    ## 1000_at                                mitogen-activated protein kinase 3
    ## 1001_at   tyrosine kinase with immunoglobulin like and EGF like domains 1
    ## 1002_f_at                  cytochrome P450 family 2 subfamily C member 19
    ## 1003_s_at                                C-X-C motif chemokine receptor 5
    ## 1004_at                                  C-X-C motif chemokine receptor 5
    ## 1005_at                                    dual specificity phosphatase 1

``` r
print(head(featureData(a4ALL)))
```

    ## An object of class 'AnnotatedDataFrame'
    ##   featureNames: 1000_at 1001_at ... 1005_at (6 total)
    ##   varLabels: ENTREZID ENSEMBLID SYMBOL GENENAME
    ##   varMetadata: labelDescription
:::

::: {#appendix .section .level1}
# [3]{.header-section-number} Appendix

::: {#session-information .section .level2}
## [3.1]{.header-section-number} Session information

    ## R version 4.5.0 RC (2025-04-04 r88126)
    ## Platform: x86_64-pc-linux-gnu
    ## Running under: Ubuntu 24.04.2 LTS
    ## 
    ## Matrix products: default
    ## BLAS:   /home/biocbuild/bbs-3.21-bioc/R/lib/libRblas.so 
    ## LAPACK: /usr/lib/x86_64-linux-gnu/lapack/liblapack.so.3.12.0  LAPACK version 3.12.0
    ## 
    ## locale:
    ##  [1] LC_CTYPE=en_US.UTF-8       LC_NUMERIC=C              
    ##  [3] LC_TIME=en_GB              LC_COLLATE=C              
    ##  [5] LC_MONETARY=en_US.UTF-8    LC_MESSAGES=en_US.UTF-8   
    ##  [7] LC_PAPER=en_US.UTF-8       LC_NAME=C                 
    ##  [9] LC_ADDRESS=C               LC_TELEPHONE=C            
    ## [11] LC_MEASUREMENT=en_US.UTF-8 LC_IDENTIFICATION=C       
    ## 
    ## time zone: America/New_York
    ## tzcode source: system (glibc)
    ## 
    ## attached base packages:
    ## [1] stats4    stats     graphics  grDevices utils     datasets  methods  
    ## [8] base     
    ## 
    ## other attached packages:
    ##  [1] hgu95av2.db_3.13.0   org.Hs.eg.db_3.21.0  AnnotationDbi_1.70.0
    ##  [4] IRanges_2.42.0       S4Vectors_0.46.0     ALL_1.49.0          
    ##  [7] Biobase_2.68.0       BiocGenerics_0.54.0  generics_0.1.3      
    ## [10] a4Preproc_1.56.0    
    ## 
    ## loaded via a namespace (and not attached):
    ##  [1] bit_4.6.0               jsonlite_2.0.0          compiler_4.5.0         
    ##  [4] crayon_1.5.3            blob_1.2.4              Biostrings_2.76.0      
    ##  [7] jquerylib_0.1.4         png_0.1-8               yaml_2.3.10            
    ## [10] fastmap_1.2.0           R6_2.6.1                XVector_0.48.0         
    ## [13] GenomeInfoDb_1.44.0     knitr_1.50              GenomeInfoDbData_1.2.14
    ## [16] DBI_1.2.3               bslib_0.9.0             rlang_1.1.6            
    ## [19] KEGGREST_1.48.0         cachem_1.1.0            xfun_0.52              
    ## [22] sass_0.4.10             bit64_4.6.0-1           RSQLite_2.3.9          
    ## [25] memoise_2.0.1           cli_3.6.4               digest_0.6.37          
    ## [28] lifecycle_1.0.4         vctrs_0.6.5             evaluate_1.0.3         
    ## [31] rmarkdown_2.29          httr_1.4.7              pkgconfig_2.0.3        
    ## [34] tools_4.5.0             htmltools_0.5.8.1       UCSC.utils_1.4.0
:::
:::
:::
:::
:::
