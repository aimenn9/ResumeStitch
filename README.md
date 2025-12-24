# ResumeStitch

**ResumeStitch** is a local Python tool that acts as a matchmaker between your portfolio and a job description. It analyzes your projects and experiences, selects the most relevant ones using AI embeddings, and stitches them into a tailored LaTeX resume draft.

It solves the problem of having too many projects to fit on one page. Instead of guessing, ResumeStitch calculates which projects fit the job description best.

## Features

* **AI-Powered Selection:** Uses the `bge-m3` embedding model (via Ollama) to mathematically rank your projects against a job post.
* **"Flavor" Optimization:** Matches not just the project, but the *version* of the project description (e.g., emphasizing Frontend vs. Backend) that fits the role best.
* **LaTeX Generation:** Outputs a `.tex` file using Jinja2 templates, ready for professional compiling.
* **Highly Customizable:** Fully control your Technical Skills, Experience, and Template layout.

## Setup

1. Install **Ollama**
2. **Pull the Embedding Model:**
```bash
ollama pull bge-m3:latest
```

3. **Install Python Dependencies:**
```bash
pip install -r requirements.txt
```


## Data Configuration

ResumeStitch looks for your data in the `data/` folder. Examples for all files are provided in the `examples/` directory.

| File Name | Description |
| --- | --- |
| `projects.json` | Contains your projects and their different description "flavors." |
| `pro_experience.json` | Your work history and roles. |
| `skills.json` | A list of your technical skills (languages, tools, etc.). |

## Usage

1. **Prepare Data:** Ensure your JSON files are populated in the `data/` folder.
2. **Set Job Description:** Open ``main.py`` and paste the job description text into the `job_description` variable.
3. **Run the Script:**
```bash
python stitch.py
```

4. **Get Output:**
* The script generates a `.tex` file in the `resumes/` folder.
* **Drafting:** This is a *draft*. You will likely need to tweak personal details or education.
* **Compiling:** Upload the `.tex` file to [Overleaf](https://www.overleaf.com/) or compile it locally to get your final PDF.


## Customization

* **Project Count:** You can change the number of selected projects (default: Top 3) in the main script.
* **Templates:** You can edit `templates/template.tex` or add new Jinja2 templates to change the visual layout.
* **Paths:** All default file paths can be configured at the top of the main script.
---