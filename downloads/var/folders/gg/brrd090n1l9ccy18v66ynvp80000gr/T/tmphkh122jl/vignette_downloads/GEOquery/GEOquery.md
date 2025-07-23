::: {.container-fluid .main-container}
::: {#header}
# Using the GEOquery Package {#using-the-geoquery-package .title .toc-ignore}

#### Sean Davis {#sean-davis .author}

#### September 21, 2014 {#september-21-2014 .date}
:::

::: {#TOC}
-   [[1]{.toc-section-number} Overview of GEO](#overview-of-geo)
    -   [[1.1]{.toc-section-number} Platforms](#platforms)
    -   [[1.2]{.toc-section-number} Samples](#samples)
    -   [[1.3]{.toc-section-number} Series](#series)
    -   [[1.4]{.toc-section-number} Datasets](#datasets)
-   [[2]{.toc-section-number} Getting Started using
    GEOquery](#getting-started-using-geoquery)
-   [[3]{.toc-section-number} GEOquery Data
    Structures](#geoquery-data-structures)
    -   [[3.1]{.toc-section-number} The GDS, GSM, and GPL
        classes](#the-gds-gsm-and-gpl-classes)
    -   [[3.2]{.toc-section-number} The GSE class](#the-gse-class)
-   [[4]{.toc-section-number} Converting to BioConductor ExpressionSets
    and limma
    MALists](#converting-to-bioconductor-expressionsets-and-limma-malists)
    -   [[4.1]{.toc-section-number} Getting GSE Series Matrix files as
        an
        ExpressionSet](#getting-gse-series-matrix-files-as-an-expressionset)
    -   [[4.2]{.toc-section-number} Converting GDS to an
        ExpressionSet](#converting-gds-to-an-expressionset)
    -   [[4.3]{.toc-section-number} Converting GDS to an
        MAList](#converting-gds-to-an-malist)
    -   [[4.4]{.toc-section-number} Converting GSE to an
        ExpressionSet](#converting-gse-to-an-expressionset)
-   [[5]{.toc-section-number} Accessing Raw Data from
    GEO](#accessing-raw-data-from-geo)
-   [[6]{.toc-section-number} Use Cases](#use-cases)
    -   [[6.1]{.toc-section-number} Getting all Series Records for a
        Given
        Platform](#getting-all-series-records-for-a-given-platform)
-   [[7]{.toc-section-number} Conclusion](#conclusion)
    -   [[7.1]{.toc-section-number} Citing GEOquery](#citing-geoquery)
    -   [[7.2]{.toc-section-number} Reporting problems or
        bugs](#reporting-problems-or-bugs)
-   [[8]{.toc-section-number} Session info](#session-info)
:::

::: {#overview-of-geo .section .level1}
# [1]{.header-section-number} Overview of GEO

The NCBI Gene Expression Omnibus (GEO) serves as a public repository for
a wide range of high-throughput experimental data. These data include
single and dual channel microarray-based experiments measuring mRNA,
genomic DNA, and protein abundance, as well as non-array techniques such
as serial analysis of gene expression (SAGE), mass spectrometry
proteomic data, and high-throughput sequencing data.

At the most basic level of organization of GEO, there are four basic
entity types. The first three (Sample, Platform, and Series) are
supplied by users; the fourth, the dataset, is compiled and curated by
GEO staff from the user-submitted data. See [the GEO home
page](https://www.ncbi.nlm.nih.gov/geo/) for more information.

::: {#platforms .section .level2}
## [1.1]{.header-section-number} Platforms

A Platform record describes the list of elements on the array (e.g.,
cDNAs, oligonucleotide probesets, ORFs, antibodies) or the list of
elements that may be detected and quantified in that experiment (e.g.,
SAGE tags, peptides). Each Platform record is assigned a unique and
stable GEO accession number (GPLxxx). A Platform may reference many
Samples that have been submitted by multiple submitters.
:::

::: {#samples .section .level2}
## [1.2]{.header-section-number} Samples

A Sample record describes the conditions under which an individual
Sample was handled, the manipulations it underwent, and the abundance
measurement of each element derived from it. Each Sample record is
assigned a unique and stable GEO accession number (GSMxxx). A Sample
entity must reference only one Platform and may be included in multiple
Series.
:::

::: {#series .section .level2}
## [1.3]{.header-section-number} Series

A Series record defines a set of related Samples considered to be part
of a group, how the Samples are related, and if and how they are
ordered. A Series provides a focal point and description of the
experiment as a whole. Series records may also contain tables describing
extracted data, summary conclusions, or analyses. Each Series record is
assigned a unique and stable GEO accession number (GSExxx). Series
records are available in a couple of formats which are handled by
GEOquery independently. The smaller and new GSEMatrix files are quite
fast to parse; a simple flag is used by GEOquery to choose to use
GSEMatrix files (see below).
:::

::: {#datasets .section .level2}
## [1.4]{.header-section-number} Datasets

GEO DataSets (GDSxxx) are curated sets of GEO Sample data. A GDS record
represents a collection of biologically and statistically comparable GEO
Samples and forms the basis of GEO's suite of data display and analysis
tools. Samples within a GDS refer to the same Platform, that is, they
share a common set of probe elements. Value measurements for each Sample
within a GDS are assumed to be calculated in an equivalent manner, that
is, considerations such as background processing and normalization are
consistent across the dataset. Information reflecting experimental
design is provided through GDS subsets.
:::
:::

::: {#getting-started-using-geoquery .section .level1}
# [2]{.header-section-number} Getting Started using GEOquery

Getting data from GEO is really quite easy. There is only one command
that is needed, `getGEO`. This one function interprets its input to
determine how to get the data from GEO and then parse the data into
useful R data structures. Usage is quite simple. This loads the GEOquery
library.

::: {#cb1 .sourceCode}
``` {.sourceCode .r}
library(GEOquery)
```
:::

Now, we are free to access any GEO accession. *Note that in the
following, I use a file packaged with the GEOquery package. In general,
you will use only the GEO accession, as noted in the code comments.*

::: {#cb2 .sourceCode}
``` {.sourceCode .r}
# If you have network access, the more typical way to do this
# would be to use this:
# gds <- getGEO("GDS507")
gds <- getGEO(filename=system.file("extdata/GDS507.soft.gz",package="GEOquery"))
```
:::

Now, `gds` contains the R data structure (of class `GDS`) that
represents the GDS507 entry from GEO. You'll note that the filename used
to store the download was output to the screen (but not saved anywhere)
for later use to a call to `getGEO(filename=...)`.

We can do the same with any other GEO accession, such as `GSM11805`, a
GEO sample.

::: {#cb3 .sourceCode}
``` {.sourceCode .r}
# If you have network access, the more typical way to do this
# would be to use this:
# gds <- getGEO("GSM11805")
gsm <- getGEO(filename=system.file("extdata/GSM11805.txt.gz",package="GEOquery"))
```
:::
:::

::: {#geoquery-data-structures .section .level1}
# [3]{.header-section-number} GEOquery Data Structures

The GEOquery data structures really come in two forms. The first,
comprising `GDS`, `GPL`, and `GSM` all behave similarly and accessors
have similar effects on each. The fourth GEOquery data structure, `GSE`
is a composite data type made up of a combination of `GSM` and `GPL`
objects. I will explain the first three together first.

::: {#the-gds-gsm-and-gpl-classes .section .level2}
## [3.1]{.header-section-number} The GDS, GSM, and GPL classes

Each of these classes is comprised of a metadata header (taken nearly
verbatim from the SOFT format header) and a GEODataTable. The
GEODataTable has two simple parts, a Columns part which describes the
column headers on the Table part. There is also a `show` method for each
class. For example, using the gsm from above:

::: {#cb4 .sourceCode}
``` {.sourceCode .r}
# Look at gsm metadata:
head(Meta(gsm))
```
:::

    ## $channel_count
    ## [1] "1"
    ## 
    ## $comment
    ## [1] "Raw data provided as supplementary file"
    ## 
    ## $contact_address
    ## [1] "715 Albany Street, E613B"
    ## 
    ## $contact_city
    ## [1] "Boston"
    ## 
    ## $contact_country
    ## [1] "USA"
    ## 
    ## $contact_department
    ## [1] "Genetics and Genomics"

::: {#cb6 .sourceCode}
``` {.sourceCode .r}
# Look at data associated with the GSM:
# but restrict to only first 5 rows, for brevity
Table(gsm)[1:5,]
```
:::

    ##           ID_REF  VALUE ABS_CALL
    ## 1 AFFX-BioB-5_at  953.9        P
    ## 2 AFFX-BioB-M_at 2982.8        P
    ## 3 AFFX-BioB-3_at 1657.9        P
    ## 4 AFFX-BioC-5_at 2652.7        P
    ## 5 AFFX-BioC-3_at 2019.5        P

::: {#cb8 .sourceCode}
``` {.sourceCode .r}
# Look at Column descriptions:
Columns(gsm)
```
:::

    ##     Column
    ## 1         
    ## 2    VALUE
    ## 3 ABS_CALL
    ##                                                                  Description
    ## 1                                                                   ID_REF =
    ## 2                         MAS 5.0 Statistical Algorithm (mean scaled to 500)
    ## 3 MAS 5.0 Absent, Marginal, Present call  with Alpha1 = 0.05, Alpha2 = 0.065

The `GPL` class behaves exactly as the `GSM` class. However, the `GDS`
class has a bit more information associated with the `Columns` method:

::: {#cb10 .sourceCode}
``` {.sourceCode .r}
Columns(gds)[,1:3]
```
:::

    ##      sample disease.state individual
    ## 1  GSM11815           RCC        035
    ## 2  GSM11832           RCC        023
    ## 3  GSM12069           RCC        001
    ## 4  GSM12083           RCC        005
    ## 5  GSM12101           RCC        011
    ## 6  GSM12106           RCC        032
    ## 7  GSM12274           RCC          2
    ## 8  GSM12299           RCC          3
    ## 9  GSM12412           RCC          4
    ## 10 GSM11810        normal        035
    ## 11 GSM11827        normal        023
    ## 12 GSM12078        normal        001
    ## 13 GSM12099        normal        005
    ## 14 GSM12269        normal          1
    ## 15 GSM12287        normal          2
    ## 16 GSM12301        normal          3
    ## 17 GSM12448        normal          4
:::

::: {#the-gse-class .section .level2}
## [3.2]{.header-section-number} The GSE class

The `GSE` entity is the most confusing of the GEO entities. A GSE entry
can represent an arbitrary number of samples run on an arbitrary number
of platforms. The `GSE` class has a metadata section, just like the
other classes. However, it doesn't have a GEODataTable. Instead, it
contains two lists, accessible using the `GPLList` and `GSMList`
methods, that are each lists of `GPL` and `GSM` objects. To show an
example:

::: {#cb12 .sourceCode}
``` {.sourceCode .r}
# Again, with good network access, one would do:
# gse <- getGEO("GSE781",GSEMatrix=FALSE)
gse <- getGEO(filename=system.file("extdata/GSE781_family.soft.gz",package="GEOquery"))
head(Meta(gse))
```
:::

    ## $contact_address
    ## [1] "715 Albany Street, E613B"
    ## 
    ## $contact_city
    ## [1] "Boston"
    ## 
    ## $contact_country
    ## [1] "USA"
    ## 
    ## $contact_department
    ## [1] "Genetics and Genomics"
    ## 
    ## $contact_email
    ## [1] "mlenburg@bu.edu"
    ## 
    ## $contact_fax
    ## [1] "617-414-1646"

::: {#cb14 .sourceCode}
``` {.sourceCode .r}
# names of all the GSM objects contained in the GSE
names(GSMList(gse))
```
:::

    ##  [1] "GSM11805" "GSM11810" "GSM11814" "GSM11815" "GSM11823" "GSM11827"
    ##  [7] "GSM11830" "GSM11832" "GSM12067" "GSM12069" "GSM12075" "GSM12078"
    ## [13] "GSM12079" "GSM12083" "GSM12098" "GSM12099" "GSM12100" "GSM12101"
    ## [19] "GSM12105" "GSM12106" "GSM12268" "GSM12269" "GSM12270" "GSM12274"
    ## [25] "GSM12283" "GSM12287" "GSM12298" "GSM12299" "GSM12300" "GSM12301"
    ## [31] "GSM12399" "GSM12412" "GSM12444" "GSM12448"

::: {#cb16 .sourceCode}
``` {.sourceCode .r}
# and get the first GSM object on the list
GSMList(gse)[[1]]
```
:::

    ## An object of class "GSM"
    ## channel_count 
    ## [1] "1"
    ## comment 
    ## [1] "Raw data provided as supplementary file"
    ## contact_address 
    ## [1] "715 Albany Street, E613B"
    ## contact_city 
    ## [1] "Boston"
    ## contact_country 
    ## [1] "USA"
    ## contact_department 
    ## [1] "Genetics and Genomics"
    ## contact_email 
    ## [1] "mlenburg@bu.edu"
    ## contact_fax 
    ## [1] "617-414-1646"
    ## contact_institute 
    ## [1] "Boston University School of Medicine"
    ## contact_name 
    ## [1] "Marc,E.,Lenburg"
    ## contact_phone 
    ## [1] "617-414-1375"
    ## contact_state 
    ## [1] "MA"
    ## contact_web_link 
    ## [1] "http://gg.bu.edu"
    ## contact_zip/postal_code 
    ## [1] "02130"
    ## data_row_count 
    ## [1] "22283"
    ## description 
    ## [1] "Age = 70; Gender = Female; Right Kidney; Adjacent Tumor Type = clear cell; Adjacent Tumor Fuhrman Grade = 3; Adjacent Tumor Capsule Penetration = true; Adjacent Tumor Perinephric Fat Invasion = true; Adjacent Tumor Renal Sinus Invasion = false; Adjacent Tumor Renal Vein Invasion = true; Scaling Target = 500; Scaling Factor = 7.09; Raw Q = 2.39; Noise = 2.60; Background = 55.24."
    ## [2] "Keywords = kidney"                                                                                                                                                                                                                                                                                                                                                                           
    ## [3] "Keywords = renal"                                                                                                                                                                                                                                                                                                                                                                            
    ## [4] "Keywords = RCC"                                                                                                                                                                                                                                                                                                                                                                              
    ## [5] "Keywords = carcinoma"                                                                                                                                                                                                                                                                                                                                                                        
    ## [6] "Keywords = cancer"                                                                                                                                                                                                                                                                                                                                                                           
    ## [7] "Lot batch = 2004638"                                                                                                                                                                                                                                                                                                                                                                         
    ## geo_accession 
    ## [1] "GSM11805"
    ## last_update_date 
    ## [1] "May 28 2005"
    ## molecule_ch1 
    ## [1] "total RNA"
    ## organism_ch1 
    ## [1] "Homo sapiens"
    ## platform_id 
    ## [1] "GPL96"
    ## series_id 
    ## [1] "GSE781"
    ## source_name_ch1 
    ## [1] "Trizol isolation of total RNA from normal tissue adjacent to Renal Cell Carcinoma"
    ## status 
    ## [1] "Public on Nov 25 2003"
    ## submission_date 
    ## [1] "Oct 20 2003"
    ## supplementary_file 
    ## [1] "ftp://ftp.ncbi.nih.gov/pub/geo/DATA/supplementary/samples/GSM11nnn/GSM11805/GSM11805.CEL.gz"
    ## title 
    ## [1] "N035 Normal Human Kidney U133A"
    ## type 
    ## [1] "RNA"
    ## An object of class "GEODataTable"
    ## ****** Column Descriptions ******
    ##     Column
    ## 1         
    ## 2    VALUE
    ## 3 ABS_CALL
    ##                                                                  Description
    ## 1                                                                   ID_REF =
    ## 2                         MAS 5.0 Statistical Algorithm (mean scaled to 500)
    ## 3 MAS 5.0 Absent, Marginal, Present call  with Alpha1 = 0.05, Alpha2 = 0.065
    ## ****** Data Table ******

::: {#cb18 .sourceCode}
``` {.sourceCode .r}
# and the names of the GPLs represented
names(GPLList(gse))
```
:::

    ## [1] "GPL96" "GPL97"

*See below for an additional, preferred method of obtaining GSE
information.*
:::
:::

::: {#converting-to-bioconductor-expressionsets-and-limma-malists .section .level1}
# [4]{.header-section-number} Converting to BioConductor ExpressionSets and limma MALists

GEO datasets are (unlike some of the other GEO entities), quite similar
to the `limma` data structure `MAList` and to the `Biobase` data
structure `ExpressionSet`. Therefore, there are two functions, `GDS2MA`
and `GDS2eSet` that accomplish that task.

::: {#getting-gse-series-matrix-files-as-an-expressionset .section .level2}
## [4.1]{.header-section-number} Getting GSE Series Matrix files as an ExpressionSet

GEO Series are collections of related experiments. In addition to being
available as SOFT format files, which are quite large, NCBI GEO has
prepared a simpler format file based on tab-delimited text. The `getGEO`
function can handle this format and will parse very large GSEs quite
quickly. The data structure returned from this parsing is a list of
ExpressionSets. As an example, we download and parse GSE2553.

::: {#cb20 .sourceCode}
``` {.sourceCode .r}
# Note that GSEMatrix=TRUE is the default
gse2553 <- getGEO('GSE2553',GSEMatrix=TRUE)
show(gse2553)
```
:::

    ## $GSE2553_series_matrix.txt.gz
    ## ExpressionSet (storageMode: lockedEnvironment)
    ## assayData: 12600 features, 181 samples 
    ##   element names: exprs 
    ## protocolData: none
    ## phenoData
    ##   sampleNames: GSM48681 GSM48682 ... GSM48861 (181 total)
    ##   varLabels: title geo_accession ... data_row_count (30 total)
    ##   varMetadata: labelDescription
    ## featureData
    ##   featureNames: 1 2 ... 12600 (12600 total)
    ##   fvarLabels: ID PenAt ... Chimeric_Cluster_IDs (13 total)
    ##   fvarMetadata: Column Description labelDescription
    ## experimentData: use 'experimentData(object)'
    ##   pubMedIds: 16230383 
    ## Annotation: GPL1977

::: {#cb22 .sourceCode}
``` {.sourceCode .r}
show(pData(phenoData(gse2553[[1]]))[1:5,c(1,6,8)])
```
:::

    ##                                                                  title type
    ## GSM48681                      Patient sample ST18, Dermatofibrosarcoma  RNA
    ## GSM48682                           Patient sample ST410, Ewing Sarcoma  RNA
    ## GSM48683                            Patient sample ST130, Sarcoma, NOS  RNA
    ## GSM48684 Patient sample ST293, Malignant Peripheral Nerve Sheath Tumor  RNA
    ## GSM48685                             Patient sample ST367, Liposarcoma  RNA
    ##                                  source_name_ch1
    ## GSM48681                     Dermatofibrosarcoma
    ## GSM48682                           Ewing Sarcoma
    ## GSM48683                            Sarcoma, NOS
    ## GSM48684 Malignant Peripheral Nerve Sheath Tumor
    ## GSM48685                             Liposarcoma
:::

::: {#converting-gds-to-an-expressionset .section .level2}
## [4.2]{.header-section-number} Converting GDS to an ExpressionSet

Taking our `gds` object from above, we can simply do:

::: {#cb24 .sourceCode}
``` {.sourceCode .r}
eset <- GDS2eSet(gds,do.log2=TRUE)
```
:::

Now, `eset` is an `ExpressionSet` that contains the same information as
in the GEO dataset, including the sample information, which we can see
here:

::: {#cb25 .sourceCode}
``` {.sourceCode .r}
eset
```
:::

    ## ExpressionSet (storageMode: lockedEnvironment)
    ## assayData: 22645 features, 17 samples 
    ##   element names: exprs 
    ## protocolData: none
    ## phenoData
    ##   sampleNames: GSM11815 GSM11832 ... GSM12448 (17 total)
    ##   varLabels: sample disease.state individual description
    ##   varMetadata: labelDescription
    ## featureData
    ##   featureNames: 200000_s_at 200001_at ... AFFX-TrpnX-M_at (22645 total)
    ##   fvarLabels: ID Gene title ... GO:Component ID (21 total)
    ##   fvarMetadata: Column labelDescription
    ## experimentData: use 'experimentData(object)'
    ##   pubMedIds: 14641932 
    ## Annotation:

::: {#cb27 .sourceCode}
``` {.sourceCode .r}
pData(eset)[,1:3]
```
:::

    ##            sample disease.state individual
    ## GSM11815 GSM11815           RCC        035
    ## GSM11832 GSM11832           RCC        023
    ## GSM12069 GSM12069           RCC        001
    ## GSM12083 GSM12083           RCC        005
    ## GSM12101 GSM12101           RCC        011
    ## GSM12106 GSM12106           RCC        032
    ## GSM12274 GSM12274           RCC          2
    ## GSM12299 GSM12299           RCC          3
    ## GSM12412 GSM12412           RCC          4
    ## GSM11810 GSM11810        normal        035
    ## GSM11827 GSM11827        normal        023
    ## GSM12078 GSM12078        normal        001
    ## GSM12099 GSM12099        normal        005
    ## GSM12269 GSM12269        normal          1
    ## GSM12287 GSM12287        normal          2
    ## GSM12301 GSM12301        normal          3
    ## GSM12448 GSM12448        normal          4
:::

::: {#converting-gds-to-an-malist .section .level2}
## [4.3]{.header-section-number} Converting GDS to an MAList

No annotation information (called platform information by GEO) was
retrieved from because `ExpressionSet` does not contain slots for gene
information, typically. However, it is easy to obtain this information.
First, we need to know what platform this GDS used. Then, another call
to `getGEO` will get us what we need.

::: {#cb29 .sourceCode}
``` {.sourceCode .r}
#get the platform from the GDS metadata
Meta(gds)$platform
```
:::

    ## [1] "GPL97"

::: {#cb31 .sourceCode}
``` {.sourceCode .r}
#So use this information in a call to getGEO
gpl <- getGEO(filename=system.file("extdata/GPL97.annot.gz",package="GEOquery"))
```
:::

So, `gpl` now contains the information for GPL5 from GEO. Unlike
`ExpressionSet`, the limma `MAList` does store gene annotation
information, so we can use our newly created `gpl` of class `GPL` in a
call to `GDS2MA` like so:

::: {#cb32 .sourceCode}
``` {.sourceCode .r}
MA <- GDS2MA(gds,GPL=gpl)
class(MA)
```
:::

    ## [1] "MAList"
    ## attr(,"package")
    ## [1] "limma"

Now, `MA` is of class `MAList` and contains not only the data, but the
sample information and gene information associated with GDS507.
:::

::: {#converting-gse-to-an-expressionset .section .level2}
## [4.4]{.header-section-number} Converting GSE to an ExpressionSet

*First, make sure that using the method described above in the section
\`\`Getting GSE Series Matrix files as an ExpressionSet'' for using GSE
Series Matrix files is not sufficient for the task, as it is much faster
and simpler.* If it is not (i.e., other columns from each GSM are
needed), then this method will be needed.

Converting a `GSE` object to an `ExpressionSet` object currently takes a
bit of R data manipulation due to the varied data that can be stored in
a `GSE` and the underlying `GSM` and `GPL` objects. However, using a
simple example will hopefully be illustrative of the technique.

First, we need to make sure that all of the `GSMs` are from the same
platform:

::: {#cb34 .sourceCode}
``` {.sourceCode .r}
gsmplatforms <- lapply(GSMList(gse),function(x) {Meta(x)$platform_id})
head(gsmplatforms)
```
:::

    ## $GSM11805
    ## [1] "GPL96"
    ## 
    ## $GSM11810
    ## [1] "GPL97"
    ## 
    ## $GSM11814
    ## [1] "GPL96"
    ## 
    ## $GSM11815
    ## [1] "GPL97"
    ## 
    ## $GSM11823
    ## [1] "GPL96"
    ## 
    ## $GSM11827
    ## [1] "GPL97"

Indeed, there are two GPLs, GPL96 and GPL97, as their platforms (which
we could have determined by looking at the GPLList for `gse`). We can
filter the original GSMList to include only those GSMs with the GPL96
platform and use this list for further processing

::: {#cb36 .sourceCode}
``` {.sourceCode .r}
gsmlist = Filter(function(gsm) {Meta(gsm)$platform_id=='GPL96'},GSMList(gse))
length(gsmlist)
```
:::

    ## [1] 17

So, now we would like to know what column represents the data that we
would like to extract. Looking at the first few rows of the Table of a
single GSM will likely give us an idea (and by the way, GEO uses a
convention that the column that contains the single measurement for each
array is called the `VALUE` column, which we could use if we don't know
what other column is most relevant).

::: {#cb38 .sourceCode}
``` {.sourceCode .r}
Table(gsmlist[[1]])[1:5,]
```
:::

    ##           ID_REF  VALUE ABS_CALL
    ## 1 AFFX-BioB-5_at  953.9        P
    ## 2 AFFX-BioB-M_at 2982.8        P
    ## 3 AFFX-BioB-3_at 1657.9        P
    ## 4 AFFX-BioC-5_at 2652.7        P
    ## 5 AFFX-BioC-3_at 2019.5        P

::: {#cb40 .sourceCode}
``` {.sourceCode .r}
# and get the column descriptions
Columns(gsmlist[[1]])[1:5,]
```
:::

    ##        Column
    ## 1            
    ## 2       VALUE
    ## 3    ABS_CALL
    ## NA       <NA>
    ## NA.1     <NA>
    ##                                                                     Description
    ## 1                                                                      ID_REF =
    ## 2                            MAS 5.0 Statistical Algorithm (mean scaled to 500)
    ## 3    MAS 5.0 Absent, Marginal, Present call  with Alpha1 = 0.05, Alpha2 = 0.065
    ## NA                                                                         <NA>
    ## NA.1                                                                       <NA>

We will indeed use the `VALUE` column. We then want to make a matrix of
these values like so:

::: {#cb42 .sourceCode}
``` {.sourceCode .r}
# get the probeset ordering
probesets <- Table(GPLList(gse)[[1]])$ID
# make the data matrix from the VALUE columns from each GSM
# being careful to match the order of the probesets in the platform
# with those in the GSMs
data.matrix <- do.call('cbind',lapply(gsmlist,function(x) 
                                      {tab <- Table(x)
                                       mymatch <- match(probesets,tab$ID_REF)
                                       return(tab$VALUE[mymatch])
                                     }))
data.matrix <- apply(data.matrix,2,function(x) {as.numeric(as.character(x))})
data.matrix <- log2(data.matrix)
data.matrix[1:5,]
```
:::

    ##       GSM11805  GSM11814  GSM11823  GSM11830  GSM12067  GSM12075  GSM12079
    ## [1,] 10.926963 11.105254 11.275019 11.438636 11.424376 11.222795 11.469845
    ## [2,]  5.749534  7.908092  7.093814  7.514122  7.901470  6.407693  5.165912
    ## [3,]  7.066089  7.750205  7.244126  7.962896  7.337176  6.569856  7.477354
    ## [4,] 12.660353 12.479755 12.215897 11.458355 11.397568 12.529870 12.240046
    ## [5,]  6.195741  6.061776  6.565293  6.583459  6.877744  6.652486  3.981853
    ##       GSM12098  GSM12100  GSM12105  GSM12268  GSM12270  GSM12283  GSM12298
    ## [1,] 10.823367 10.835971 10.810893 11.062653 10.323055 11.181028 11.566387
    ## [2,]  6.556123  8.207014  6.816344  6.563768  7.353147  5.770829  6.912889
    ## [3,]  7.708739  7.428779  7.754888  7.126188  8.742815  7.339850  7.602142
    ## [4,] 12.336534 11.762839 11.237509 12.412490 11.213408 12.678380 12.232901
    ## [5,]  5.501439  6.247928  6.017922  6.525129  6.683696  5.918863  5.837943
    ##       GSM12300  GSM12399  GSM12444
    ## [1,] 11.078151 11.535178 11.105450
    ## [2,]  4.812498  7.471675  7.488644
    ## [3,]  7.383704  7.432959  7.381110
    ## [4,] 12.090939 11.421802 12.172834
    ## [5,]  6.281698  5.419539  5.469235

Note that we do a `match` to make sure that the values and the platform
information are in the same order. Finally, to make the `ExpressionSet`
object:

::: {#cb44 .sourceCode}
``` {.sourceCode .r}
require(Biobase)
# go through the necessary steps to make a compliant ExpressionSet
rownames(data.matrix) <- probesets
colnames(data.matrix) <- names(gsmlist)
pdata <- data.frame(samples=names(gsmlist))
rownames(pdata) <- names(gsmlist)
pheno <- as(pdata,"AnnotatedDataFrame")
eset2 <- new('ExpressionSet',exprs=data.matrix,phenoData=pheno)
eset2
```
:::

    ## ExpressionSet (storageMode: lockedEnvironment)
    ## assayData: 22283 features, 17 samples 
    ##   element names: exprs 
    ## protocolData: none
    ## phenoData
    ##   sampleNames: GSM11805 GSM11814 ... GSM12444 (17 total)
    ##   varLabels: samples
    ##   varMetadata: labelDescription
    ## featureData: none
    ## experimentData: use 'experimentData(object)'
    ## Annotation:

So, using a combination of `lapply` on the GSMList, one can extract as
many columns of interest as necessary to build the data structure of
choice. Because the GSM data from the GEO website are fully downloaded
and included in the `GSE` object, one can extract foreground and
background as well as quality for two-channel arrays, for example.
Getting array annotation is also a bit more complicated, but by
replacing \`\`platform'' in the lapply call to get platform information
for each array, one can get other information associated with each
array.
:::
:::

::: {#accessing-raw-data-from-geo .section .level1}
# [5]{.header-section-number} Accessing Raw Data from GEO

NCBI GEO accepts (but has not always required) raw data such as .CEL
files, .CDF files, images, etc. Sometimes, it is useful to get quick
access to such data. A single function, `getGEOSuppFiles`, can take as
an argument a GEO accession and will download all the raw data associate
with that accession. By default, the function will create a directory in
the current working directory to store the raw data for the chosen GEO
accession. Combining a simple `sapply` statement or other loop structure
with `getGEOSuppFiles` makes for a very simple way to get gobs of raw
data quickly and easily without needing to know the specifics of GEO raw
data URLs.
:::

::: {#use-cases .section .level1}
# [6]{.header-section-number} Use Cases

GEOquery can be quite powerful for gathering a lot of data quickly. A
few examples can be useful to show how this might be done for data
mining purposes.

::: {#getting-all-series-records-for-a-given-platform .section .level2}
## [6.1]{.header-section-number} Getting all Series Records for a Given Platform

For data mining purposes, it is sometimes useful to be able to pull all
the GSE records for a given platform. GEOquery makes this very easy, but
a little bit of knowledge of the GPL record is necessary to get started.
The GPL record contains both the GSE and GSM accessions that reference
it. Some code is useful to illustrate the point:

::: {#cb46 .sourceCode}
``` {.sourceCode .r}
gpl97 <- getGEO('GPL97')
Meta(gpl97)$title
```
:::

    ## [1] "[HG-U133B] Affymetrix Human Genome U133B Array"

::: {#cb48 .sourceCode}
``` {.sourceCode .r}
head(Meta(gpl97)$series_id)
```
:::

    ## [1] "GSE362" "GSE473" "GSE620" "GSE674" "GSE781" "GSE907"

::: {#cb50 .sourceCode}
``` {.sourceCode .r}
length(Meta(gpl97)$series_id)
```
:::

    ## [1] 165

::: {#cb52 .sourceCode}
``` {.sourceCode .r}
head(Meta(gpl97)$sample_id)
```
:::

    ## [1] "GSM3922" "GSM3924" "GSM3926" "GSM3928" "GSM3930" "GSM3932"

::: {#cb54 .sourceCode}
``` {.sourceCode .r}
length(Meta(gpl97)$sample_id)
```
:::

    ## [1] 7917

The code above loads the GPL97 record into R. The Meta method extracts a
list of header information from the GPL record. The `title` gives the
human name of the platform. The `series_id` gives a vector of series
ids. Note that there are 165 series associated with this platform and
7917 samples. Code like the following could be used to download all the
samples or series. I show only the first 5 samples as an example:

::: {#cb56 .sourceCode}
``` {.sourceCode .r}
gsmids <- Meta(gpl97)$sample_id
gsmlist <- sapply(gsmids[1:5],getGEO)
names(gsmlist)
```
:::

    ## [1] "GSM3922" "GSM3924" "GSM3926" "GSM3928" "GSM3930"
:::
:::

::: {#conclusion .section .level1}
# [7]{.header-section-number} Conclusion

The GEOquery package provides a bridge to the vast array resources
contained in the NCBI GEO repositories. By maintaining the full richness
of the GEO data rather than focusing on getting only the \`\`numbers'',
it is possible to integrate GEO data into current Bioconductor data
structures and to perform analyses on that data quite quickly and
easily. These tools will hopefully open GEO data more fully to the array
community at large.

::: {#citing-geoquery .section .level2}
## [7.1]{.header-section-number} Citing GEOquery

Please consider citing GEOquery if used in support of your own research:

::: {#cb58 .sourceCode}
``` {.sourceCode .r}
citation("GEOquery")
```
:::

    ## Please cite the following if utilizing the GEOquery software:
    ## 
    ##   Davis S, Meltzer P (2007). "GEOquery: a bridge between the Gene
    ##   Expression Omnibus (GEO) and BioConductor." _Bioinformatics_, *14*,
    ##   1846-1847. doi:10.1093/bioinformatics/btm254
    ##   <https://doi.org/10.1093/bioinformatics/btm254>.
    ## 
    ## A BibTeX entry for LaTeX users is
    ## 
    ##   @Article{,
    ##     author = {Sean Davis and Paul Meltzer},
    ##     title = {GEOquery: a bridge between the Gene Expression Omnibus (GEO) and BioConductor},
    ##     journal = {Bioinformatics},
    ##     year = {2007},
    ##     volume = {14},
    ##     pages = {1846--1847},
    ##     doi = {10.1093/bioinformatics/btm254},
    ##   }
:::

::: {#reporting-problems-or-bugs .section .level2}
## [7.2]{.header-section-number} Reporting problems or bugs

If you run into problems using GEOquery, the [Bioconductor Support
site](https://support.bioconductor.org/) is a good first place to ask
for help. If you are convinced that there is a bug in GEOquery (this is
pretty unusual, but not unheard of), feel free to submit an issue on the
[GEOquery github site](https://github.com/seandavi/GEOquery) or file a
bug report directly from R (will open a new github issue):

::: {#cb60 .sourceCode}
``` {.sourceCode .r}
bug.report(package='GEOquery')
```
:::
:::
:::

::: {#session-info .section .level1}
# [8]{.header-section-number} Session info

The following package and versions were used in the production of this
vignette.

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
    ## [1] stats     graphics  grDevices utils     datasets  methods   base     
    ## 
    ## other attached packages:
    ## [1] GEOquery_2.76.0     Biobase_2.68.0      BiocGenerics_0.54.0
    ## [4] generics_0.1.3      knitr_1.50         
    ## 
    ## loaded via a namespace (and not attached):
    ##  [1] rappdirs_0.3.3              tidyr_1.3.1                
    ##  [3] sass_0.4.10                 xml2_1.3.8                 
    ##  [5] SparseArray_1.8.0           lattice_0.22-7             
    ##  [7] hms_1.1.3                   digest_0.6.37              
    ##  [9] magrittr_2.0.3              evaluate_1.0.3             
    ## [11] grid_4.5.0                  fastmap_1.2.0              
    ## [13] R.oo_1.27.0                 jsonlite_2.0.0             
    ## [15] Matrix_1.7-3                R.utils_2.13.0             
    ## [17] GenomeInfoDb_1.44.0         limma_3.64.0               
    ## [19] httr_1.4.7                  purrr_1.0.4                
    ## [21] UCSC.utils_1.4.0            XML_3.99-0.18              
    ## [23] httr2_1.1.2                 jquerylib_0.1.4            
    ## [25] abind_1.4-8                 cli_3.6.4                  
    ## [27] rlang_1.1.6                 crayon_1.5.3               
    ## [29] XVector_0.48.0              R.methodsS3_1.8.2          
    ## [31] cachem_1.1.0                DelayedArray_0.34.0        
    ## [33] yaml_2.3.10                 S4Arrays_1.8.0             
    ## [35] tools_4.5.0                 tzdb_0.5.0                 
    ## [37] dplyr_1.1.4                 GenomeInfoDbData_1.2.14    
    ## [39] SummarizedExperiment_1.38.0 curl_6.2.2                 
    ## [41] vctrs_0.6.5                 R6_2.6.1                   
    ## [43] matrixStats_1.5.0           stats4_4.5.0               
    ## [45] lifecycle_1.0.4             S4Vectors_0.46.0           
    ## [47] IRanges_2.42.0              pkgconfig_2.0.3            
    ## [49] bslib_0.9.0                 pillar_1.10.2              
    ## [51] rentrez_1.2.3               data.table_1.17.0          
    ## [53] glue_1.8.0                  statmod_1.5.0              
    ## [55] xfun_0.52                   tibble_3.2.1               
    ## [57] GenomicRanges_1.60.0        tidyselect_1.2.1           
    ## [59] MatrixGenerics_1.20.0       htmltools_0.5.8.1          
    ## [61] rmarkdown_2.29              readr_2.1.5                
    ## [63] compiler_4.5.0
:::
:::
