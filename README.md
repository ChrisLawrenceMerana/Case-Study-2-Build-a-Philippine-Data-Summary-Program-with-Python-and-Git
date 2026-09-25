# Philippine Customs 2015 Data Summary Program

A modular Python data processing pipeline developed for Case Study 2 to summarize and analyze Philippine customs transactions.

---

## 1. Data Source & Setup
* **Dataset**: Philippine Customs 2015 (`2015.csv`)
* **Size**: ~493.5 MB (~2.2M records)
* **Storage Rule**: Download the raw dataset and place it inside the `data/` directory as `data/2015.csv`. The raw dataset is excluded from Git tracking via `.gitignore`.

---

## 2. Installation & Environment Setup
Clone the repository and install the dependencies in a virtual environment:

```bash
# Clone the repository
git clone https://github.com/ChrisLawrenceMerana/Case-Study-2-Build-a-Philippine-Data-Summary-Program-with-Python-and-Git.git
cd Case-Study-2-Build-a-Philippine-Data-Summary-Program-with-Python-and-Git

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
