import json
import os
import jinja2
from project_picker import find_best_experience_presentation, find_best_match, set_jd_vector

PROJECTS_FILE = "data/projects.json"
EXPERIENCE_FILE="data/pro_experience.json"
SKILLS_PATH="data/skills.json"
TEMPLATE_FILE="templates/template.tex"
OUTPUT_PATH="resumes/resume_output.tex"
PROJECT_NUMBER= 3
# job description text
job_description = """
Job description HEEERE
"""
# LaTeX special characters that need to be escaped
LATEX_SUBS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
}

def escape_tex(value):
    if not isinstance(value, str):
        return value
    newval = value
    for k, v in LATEX_SUBS.items():
        newval = newval.replace(k, v)
    return newval

def build_resume():

    #setup Jinja2 to use LaTeX-safe delimiters
    env = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string=r'}',
        variable_start_string=r'\VAR{',
        variable_end_string=r'}',
        comment_start_string=r'\#{',
        comment_end_string=r'}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    
    # Add the escape filter to env
    env.filters['escape_tex'] = escape_tex

    # setup LLM & vectorize job description
    set_jd_vector(job_description)
    # get all the data
    full_data = read_data()

    #escape all strings in the data
    #avoid writing \VAR{ x | escape_tex } everywhere in the template
    def escape_data(d):
        if isinstance(d, str):
            return escape_tex(d)
        elif isinstance(d, list):
            return [escape_data(i) for i in d]
        elif isinstance(d, dict):
            return {k: escape_data(v) for k, v in d.items()}
        return d
    
    safe_data = escape_data(full_data)

    #render template
    # template = env.get_template('template.tex')
    template = env.get_template(TEMPLATE_FILE)
    rendered_tex = template.render(**safe_data)

    #write result
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(rendered_tex)

    print(f"success {OUTPUT_PATH} created.")
    

def read_data():
    full_data = {}
    full_data["technical_skills"]=read_skills()
    full_data["experiences"]=read_experience()
    full_data["projects"]=read_projects()

    # print("full data=====")
    # print(full_data)
    return full_data

def read_skills():
    with open(SKILLS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
        # return json.load(f).get("technical_skills")

def read_experience():
    return find_best_experience_presentation(EXPERIENCE_FILE)

def read_projects():
    return find_best_match(job_description,PROJECTS_FILE,PROJECT_NUMBER)

if __name__ == "__main__":
    build_resume()
