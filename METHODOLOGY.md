# METHODOLOGY: SkillPulse

## 1. Spark RDD Analytical Pipeline

The analytical foundation of SkillPulse is implemented strictly using **Apache Spark RDD (Resilient Distributed Dataset)** transformations and actions, avoiding black-box MLlib or DataFrame APIs for core machine learning.

### 1.1 Ingestion & Preprocessing
Unstructured job descriptions are processed using custom mapping functions:
```python
def parse(r):
    toks = {t.strip(".") for t in re.findall(r"[a-z][a-z+#.]*", (r["description"] or "").lower())}
    sk = sorted(toks & SK.value)
    if not sk: return None
    return {
        "band": band_of(float(r["salary_lpa"])),
        "lpa": float(r["salary_lpa"]),
        "skills": sk,
        "feats": [f"sk_{s}" for s in sk] + [f"lvl_{r['experience']}"]
    }

raw_rdd = sc.parallelize(rows, numSlices=4)
jobs_rdd = raw_rdd.map(parse).filter(lambda j: j is not None).cache()
```

---

## 2. Naive Bayes Classification from Scratch with RDDs

### 2.1 Mathematical Formulation
For a document represented as feature set $F = \{f_1, f_2, \dots, f_k\}$ and salary band $C \in \{\text{Low}, \text{Mid}, \text{High}\}$:

$$P(C \mid F) \propto P(C) \prod_{i=1}^{k} P(f_i \mid C)$$

Applying Laplace smoothing to handle unseen features and log-space transformations to prevent floating-point underflow:

$$\ln P(C \mid F) \propto \ln \left(\frac{N_C + 1}{N + |C|}\right) + \sum_{i=1}^{k} \ln \left(\frac{\text{count}(f_i, C) + 1}{N_C + 2}\right)$$

### 2.2 RDD Distributed Implementation
1. **Partitioning:** `train_rdd, test_rdd = jobs_rdd.randomSplit([0.80, 0.20], seed=42)`
2. **Prior Estimation:**
   ```python
   class_cnt = train_rdd.map(lambda j: (j["band"], 1)).reduceByKey(add).collectAsMap()
   ```
3. **Likelihood Estimation:**
   ```python
   feat_cnt = train_rdd.flatMap(lambda j: [((j["band"], f), 1) for f in j["feats"]]).reduceByKey(add).collectAsMap()
   ```
4. **Broadcast Lookup:** `M = sc.broadcast((class_cnt, feat_cnt, total_train))`
5. **Inference & Confusion Matrix:**
   ```python
   conf = test_rdd.map(lambda j: ((j["band"], nb(j["feats"])), 1)).reduceByKey(add).collectAsMap()
   ```

---

## 3. Skill Stock Market Metrics

### 3.1 Demand Index (0–100)
Normalized share of job postings demanding a particular skill:

$$\text{Demand Index}(s) = \frac{\text{Postings}(s)}{\max_{k} \text{Postings}(k)} \times 100$$

### 3.2 24-Month Momentum Slope (OLS Regression)
For a 24-month share vector $Y = [y_1, y_2, \dots, y_{24}]$:

$$\text{Slope} = \frac{\sum_{i=1}^{n} (i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^{n} (i - \bar{x})^2}$$

$$\text{Momentum (\% / mo)} = \frac{\text{Slope}}{\bar{y}} \times 100$$

- **`RISING`:** Momentum $> +1.2\% / \text{month}$
- **`FALLING`:** Momentum $< -1.2\% / \text{month}$
- **`STABLE`:** $-1.2\% \le \text{Momentum} \le +1.2\% / \text{month}$

### 3.3 Salary Premium
$$\text{Premium}(s) = \bar{S}_s - \bar{S}_{\text{market}}$$
Where $\bar{S}_s$ is the average salary of postings requiring skill $s$, and $\bar{S}_{\text{market}}$ is the overall market average LPA.

---

## 4. Evaluation Metrics
- **Accuracy:** $\frac{\sum \text{TP}_i}{N_{\text{test}}}$
- **Precision:** $\frac{\text{TP}_c}{\text{TP}_c + \text{FP}_c}$
- **Recall:** $\frac{\text{TP}_c}{\text{TP}_c + \text{FN}_c}$
- **Macro F1:** $\frac{1}{3} \sum_{c \in \{\text{Low}, \text{Mid}, \text{High}\}} 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$
