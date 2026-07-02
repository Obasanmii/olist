# Olist Delivery Analysis — Are late deliveries costing us reviews & revenue?

**The Hook —** _[FILL IN once you have numbers, e.g. "Late deliveries average ~1.3 stars
lower; the worst 3 categories drive 41% of late orders and ~R$X in at-risk revenue."]_

### 🔗 Live demo
_[Streamlit Community Cloud link goes here after Week 3, Day 15]_

![demo](docs/demo.gif)
<!-- record a GIF of the dashboard and save it as docs/demo.gif -->

### The question
Late deliveries are suspected of dragging down review scores. **Which categories,
sellers, and regions are the worst offenders, and how much revenue is at risk?**

### Architecture / data flow
```
Olist CSVs  →  DuckDB (SQL)  →  pandas (analysis)  →  Streamlit (dashboard)
```

### Key findings
- _[Finding 1 — with a number]_
- _[Finding 2 — with a number]_
- _[Finding 3 — with a number]_

### Recommendations
1. _[Action]_ → _[estimated impact]_
2. _[Action]_ → _[estimated impact]_
3. _[Action]_ → _[estimated impact]_

### Tech
Python · SQL (DuckDB) · pandas · Plotly · Streamlit

### How to run
```bash
git clone <your-repo-url>
cd olist
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# download the Olist dataset from Kaggle and put the 9 CSVs in data/
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

streamlit run app/app.py
```

### Repo structure
```
data/        # raw CSVs (gitignored) — see data/PUT_CSVS_HERE.md
notebooks/   # 01_exploration.ipynb — EDA scratchpad
sql/         # queries.sql — reference SQL
src/         # data_loader.py — loads CSVs into DuckDB, holds all queries
app/         # app.py — the Streamlit dashboard
docs/        # demo.gif and any screenshots
```
