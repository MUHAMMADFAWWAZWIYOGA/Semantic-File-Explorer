Local File Retrieval with Verbatim Evidence Checks in a Five Query Pilot Study

**Muhammad Fawwaz Wiyoga**
Andalas University, Padang, Indonesia
Student ID 2311532019
2311532019_fawwaz@student.unand.ac.id

**Abstract—**Locating a file from a natural-language description is difficult when folders contain multiple versions and formats. This paper presents a local retrieval prototype that parses TXT, Markdown, DOCX, and CSV files, builds a timestamp-cached term frequency–inverse document frequency (TF–IDF) index, ranks candidates by cosine similarity, and returns a path with a snippet checked against the source file. We audit the implemented code and examine a supplied benchmark of five Indonesian queries over a small synthetic directory. Exact-path top-one accuracy was 5/5 for the prototype and 4/5 for a keyword baseline; mean measured query time was 10.49 ms versus 5.44 ms. An independent rerun reproduced all five labeled paths and literal evidence spans. The baseline's only error selected a text duplicate with the same content as the labeled Word document. A reported 5/5 versus 0/5 evidence score cannot support a comparative faithfulness claim because the baseline always returns medium confidence while the scoring script requires high confidence. The system uses lexical retrieval, not an LLM agent. Larger, independently annotated tests are needed to assess semantic retrieval and evidence quality.

**Keywords—**local file retrieval, TF–IDF, cosine similarity, evidence verification, pilot evaluation.

Implemented indexing, ranking, and literal evidence check. A query with no ranked candidate returns a root listing without a second search.

# INTRODUCTION

Local directories often contain several versions of a document, inconsistent filenames, and files in different formats. A user may remember a description such as “the revised third quarter report” without remembering the exact path. Retrieving a path is therefore a ranking problem: the system must map a short query to the most appropriate file and provide enough evidence for the user to inspect the result.

Classical term weighting and cosine similarity offer an inexpensive and transparent basis for ranking text [1], [2]. Provenance is a separate concern: a retrieved path can be accompanied by a passage that can be checked in the source, but the existence of that passage does not alone prove that it answers the query. This distinction matters in evidence oriented retrieval evaluations [3].

The supplied project implements a local prototype named Semantic File Explorer. Despite its name and earlier proposal language, the implemented ranking method is lexical TF–IDF. The program does not call a large language model, use dense embeddings, or execute a multi step reasoning agent. Its fallback lists the root directory when vector search finds no candidate. This paper describes the implemented behavior, reports the available benchmark, and identifies what the five query pilot can and cannot show. The research questions are: (1) how does exact path retrieval compare with the supplied keyword baseline on the pilot queries, and (2) what does the current evidence check actually verify?

# RELATED WORK

Salton and Buckley described the role of term weights in automatic retrieval [1]. The vector space treatment in Introduction to Information Retrieval explains TF–IDF, cosine ranking, and retrieval evaluation [2]. The current prototype follows that family of lexical methods; it should not be described as a contextual embedding model merely because it represents documents as weighted vectors.

KILT distinguishes answer quality from provenance quality in knowledge intensive tasks [3]. That separation motivates reporting path correctness and support of an attached passage independently. ReAct interleaves language model reasoning with tool actions [4]. The present implementation has no such reasoning trace or iterative tool plan, so ReAct is context for future work rather than a description of the tested system.

# METHODS

## System and corpus

The retriever walks a configured root directory and accepts .txt, .md, .py, .csv, and .docx files. Word paragraphs are extracted with python-docx; CSV rows are flattened to text; the remaining accepted files are read as UTF-8. Empty files and files that cannot be read successfully are not indexed. The index stores extracted content, token counts, file modification times, and document vectors. A JSON cache reuses content and counts when a file's modification time is unchanged. The directory tree is still walked at initialization, and vectors are recomputed; this is timestamp based incremental extraction rather than a filesystem watchdog.

Table I inventories the 11 task files in the supplied snapshot. The generator specifies 10 files; the additional Q3_report_FINAL.txt has the same extracted text as the Word document. Of the 11 files, one is empty and 10 enter the proposed index. The proposed system excludes its JSON cache, but the baseline's directory walk does not. Five Indonesian queries and one exact target path per query are recorded in ground_truth.json. No separate development partition or relevance assessment of alternative valid files is available.

SUPPLIED CORPUS SNAPSHOT

## Retrieval and evidence procedure

Text is lowercased and tokenized by replacing characters outside ASCII letters, digits, and whitespace. One character tokens are removed. Term frequency is the count of a term divided by the document token count; inverse document frequency is the natural logarithm of the indexed document count divided by the number of documents containing that term. A query and each file are converted to TF–IDF vectors and ranked by cosine similarity [1], [2]. Only scores above 0.05 enter the candidate list, and the highest score is returned. If no candidate survives, the function lists the root directory and returns no file; it does not perform a second search (Fig. 1).

The retriever creates an evidence snippet around a prominent query token in the stored file content. A post check reads the file again and tests whether the snippet appears as a literal substring after whitespace normalization. A passing check sets confidence to high; failure sets it to low. This check confirms textual presence, not that the snippet entails the user's requested meaning. The confidence field is a rule based label, not a calibrated probability.

The baseline scans filenames and tries to open every file as UTF-8 text for each query. It adds two points per query token found as a substring in the filename and one point per token found in readable content, then returns the highest scoring path. It does not parse Word content. Its output confidence is hard coded to medium. These differences make the baseline an illustrative comparator rather than a controlled ablation of TF–IDF alone.

## Evaluation

The supplied benchmark.py calculates top one exact path accuracy as the number of predictions identical to the single labeled path divided by five. The field named faithfulness is counted only when the predicted path matches the label and the agent returns confidence == "high". It is therefore a joint path and confidence indicator, not an independent human judgment that the snippet supports the answer. Query time is measured with time.time() around each query() call. The proposed index is constructed before timing starts; the report has one timing run and does not record hardware or variation across runs.

## Reproducibility of the supplied run

The numerical results in this paper are transcribed from benchmark_report.json and checked against the evaluation code and corpus snapshot. The report logs predicted paths and per-query times, but not evidence snippets, software versions, or machine specifications. Running generate_dataset.py alone does not reproduce the supplied snapshot because the duplicate Q3 text file is absent from the generator. A replicable follow-up experiment would archive the exact corpus and hashes, exclude the cache from both candidate sets, record the software and hardware environment, and repeat timing measurements. Standard retrieval evaluations also require a stable document collection, queries, and relevance judgments [5].

## Independent diagnostic rerun

For an additional implementation check, we copied the supplied task files to a temporary directory, excluded the pre-existing index cache, and ran the unchanged retriever on the five recorded queries. We compared each returned path with the label and tested each returned span against the file using the program's own literal post-check. We then initialized the retriever again against the same copied directory to observe cache reuse and submitted an out-of-vocabulary query to inspect the no-match branch. These checks test behavior, not semantic validity; they are reported separately from the supplied timing benchmark. The script and machine-readable output accompany this manuscript.

# RESULTS

Table II reproduces the values in benchmark_report.json. The proposed retriever matches all five exact target paths, while the keyword baseline matches four. The reported joint path and high confidence counts are five and zero. The proposed method takes about 5.05 ms longer per query in the single recorded run.

SUPPLIED FIVE QUERY BENCHMARK

QUERY LEVEL EXACT PATH RESULTS

The only path disagreement is the query “laporan keuangan Q3 yang sudah direvisi.” The label is finance/Q3_report_FINAL.docx; the baseline returns finance/Q3_report_FINAL.txt, whereas the TF–IDF retriever returns the labeled Word file. Inspection of the supplied corpus shows that these two files contain the same sentence. Thus, the 20 percentage point difference is an exact path difference under a single answer label, rather than evidence that one method retrieved semantically irrelevant content. The remaining four queries receive the labeled path from both methods.

As a sensitivity check, we re-scored the recorded predictions with either the strict path label or the two verified same-content Q3 files accepted as equivalent (Table IV). Both methods retrieve relevant content on all five queries under the latter rule. This is a re-analysis of the existing predictions, not a new system run. It shows that a single-label evaluation can turn a duplicate version into an apparent retrieval error. The equivalence rule does not establish that all duplicate files in a larger corpus should always be interchangeable; it applies only to this verified pair.

EFFECT OF THE RELEVANCE RULE

The single-run mean in Table II also hides a large first-query difference. Table V reports the ordered timing summary calculated from the five per-query values in the supplied JSON. The Word-file query took 48.84 ms for the retriever, while each of its four other queries took less than 1 ms. Consequently, its median was lower than the baseline median even though its mean was higher. No causal explanation or stable speed ranking follows from five sequential measurements without repeated runs.

RECORDED QUERY LATENCY DISTRIBUTION (MS)

In the independent rerun on the copied corpus, the retriever indexed 10 nonempty files and returned the labeled path and a literally present span on each query (Table VI). The second initialization reused 10 cached documents. The unmatched token query returned no path and low confidence after the root listing branch. These results confirm the observed implementation path without adding independent relevance judgments.

INDEPENDENT RERUN OF PATH AND SPAN CHECKS

# DISCUSSION

The prototype demonstrates that several local formats can be indexed and searched without a cloud service. The timestamp cache reduces repeated text extraction for unchanged files, and the returned snippet can be checked for literal presence in the file. These are implementation properties visible in the code. The five examples show that the pipeline runs on the supplied small corpus.

Table VII summarizes design labels in the accompanying draft against implemented behavior. A weighted term vector does not imply a dense semantic embedding, and directory listing is a fallback message rather than an iterative exploration policy.

IMPLEMENTATION AUDIT

The benchmark does not isolate the value of TF–IDF. The baseline cannot read .docx as structured text, the candidate directory includes a duplicate text file, and the baseline may scan semantic_index.json as if it were a document. A stronger comparison would give both systems the same candidate set and extracted text, then vary only the ranking method. BM25 would be a relevant additional lexical baseline [6]. Duplicate paths with identical content should either both be labeled relevant or grouped as one document family. Queries should be written by assessors who did not build the corpus and should include paraphrases without shared tokens if semantic generalization is the research question.

The reported evidence metric also requires redesign. Because the baseline always sets confidence to medium, it cannot score a positive value regardless of whether it returns a correct path and valid snippet. The proposed system receives high when the snippet is literally present, even if the quoted phrase is irrelevant to the query. A fair protocol should evaluate, for both systems, path correctness, literal quote validity, and semantic support as separate outcomes; the last outcome needs human annotation or a validated independent judge. The current 100% figure should not be interpreted as a zero hallucination guarantee.

The 10.49 ms mean is a single observed value for search after index construction. It does not measure initial indexing, cold start, directory growth, repeated runs, or an end to end user experience. Claims about real time behavior at tens of thousands of files therefore await a scale experiment. The five hand written queries also cannot support a statistical claim that the proposed method is generally more accurate.

# LIMITATIONS AND FUTURE WORK

The pilot uses a tiny synthetic corpus, one ground truth path per query, and one benchmark run. The supplied snapshot differs from the generator output and should be frozen and versioned before a new experiment. No train/test partition, independent annotations, adversarial queries, or statistical uncertainty estimates are available. The ASCII tokenizer may discard non ASCII characters; the system is lexical and cannot be assumed to understand synonyms or paraphrases. The quoted span check verifies occurrence but not relevance. The path guard uses a string prefix check, which is not a complete containment check for arbitrary paths or symbolic links, and no security test is reported.

Future work should create a larger, versioned corpus; annotate all acceptable target paths and supporting spans; normalize extraction across baselines; exclude cache files; assess retrieval and evidence separately; and test repeated warm and cold start latency. A meaningful semantic claim would require comparison with a dense or hybrid retriever on queries specifically designed to separate lexical overlap from meaning. A security claim would require explicit traversal and link tests.

# CONCLUSION

This five query pilot documents a working local TF–IDF file retriever with multi format extraction and a literal evidence check. In the supplied report it returns the labeled path on five queries, compared with four for a keyword baseline, at a higher measured query time. The one path difference concerns a duplicate file with identical content, and the reported evidence scores are not comparable under the current metric. The contribution at this stage is a reproducible prototype and an explicit account of its evaluation limits. Broader claims require a corrected benchmark and independently assessed evidence quality.

##### REFERENCES

G. Salton and C. Buckley, “Term-weighting approaches in automatic text retrieval,” Information Processing & Management, vol. 24, no. 5, pp. 513–523, 1988, doi: 10.1016/0306-4573(88)90021-090021-0).

C. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information Retrieval. Cambridge, U.K.: Cambridge University Press, 2008. [Online]. Available: https://nlp.stanford.edu/IR-book/.

F. Petroni et al., “KILT: a benchmark for knowledge intensive language tasks,” in Proc. NAACL-HLT, 2021, pp. 2523–2544, doi: 10.18653/v1/2021.naacl-main.200.

S. Yao et al., “ReAct: synergizing reasoning and acting in language models,” in Proc. ICLR, 2023. [Online]. Available: arXiv:2210.03629.

National Institute of Standards and Technology, “Text REtrieval Conference relevance judgments,” [Online]. Available: https://trec.nist.gov/data/reljudge_eng.html. Accessed: Sep. 27, 2026.

S. Robertson and H. Zaragoza, “The probabilistic relevance framework: BM25 and beyond,” Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009, doi: 10.1561/1500000019.
