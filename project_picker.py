import json
import numpy as np
import ollama

MODEL_NAME = "bge-m3" 
# MODEL_NAME = "qwen3-embedding:8b" 
JD_VECTOR=None
W_TECH = 3.5
W_TYPE = 2.0
W_DESC = 1.0
JOB_DESCRIPTION = """
"""

def get_embedding(text):
    response = ollama.embeddings(model=MODEL_NAME, prompt=text)
    return response["embedding"]

def query_embedding(text):
    text = f"Given a job description, retrieve relevant resume projects: {text}"
    response = ollama.embeddings(model=MODEL_NAME, prompt=text)
    return response["embedding"]


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


def find_best_experience_presentation(experience_path):
    with open(experience_path, 'r') as f:
        experience_data = json.load(f)

    candidates = []
    for experience in experience_data:
        full_exp = experience.get("experience",{})
        options_list = full_exp.get("Options",[])

        for option in options_list:
            # Type String
            types_list = option.get("types",[])
            if types_list:
                types= "- " + "\n- ".join(types_list)
            else:
                types=""
            type_text =f"Best For roles: {types}"
            v_type = np.array(get_embedding(type_text))
            
            bullets_list = option.get("bullets",[])
            if bullets_list:
                bullets="- "+"\n- ".join(bullets_list)
            else:
                bullets=""
            # Description String (Title + Bullets)
            desc_text = f"""
            Details: {bullets}
            """
            v_desc = np.array(get_embedding(desc_text))

            # calculate and multiply by weight
            weighted_sum =  (v_type * W_TYPE) + (v_desc * W_DESC)
            final_vector = weighted_sum / np.linalg.norm(weighted_sum)
            
            # add project name and other properties
            option["position"]=full_exp.get("position")
            option["date"]=full_exp.get("date")
            option["city"]=full_exp.get("city")
            option["comments"]=full_exp.get("comments")
            # store important info
            candidates.append({
                "option_data": option,
                "vector": final_vector,
                "text_preview": option.get('position', 'Unknown Position')
            })

    scored_candidates = []
    for cand in candidates:
        score = cosine_similarity(JD_VECTOR, cand["vector"])
        scored_candidates.append((score, cand["option_data"]))

    #sort by score
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    # print("scored candidates==========presentation")
    # print(scored_candidates)
    return get_presentation(scored_candidates)

        
def set_jd_vector(job_desc):
    global JD_VECTOR
    print("vectorizing job description")
    JD_VECTOR = get_embedding(job_desc)
    # JD_VECTOR = query_embedding(job_desc)

def find_best_match(job_desc,projects_path,project_number):
    print(f"loading JSON from {projects_path}")
    with open(projects_path, 'r') as f:
        projects_data = json.load(f)

    candidates = []

    print("vectorizing project Options")
    
    for entry in projects_data:
        response_data = entry.get("element", {})
        options_list = response_data.get("Options", [])

        for option in options_list:
            tech_list = option.get("technologies",[])
            if tech_list:
                tech="- "+"\n- ".join(tech_list)
            else:
                tech=""
            tech_text = f"Technologies: {tech}"
            v_tech = np.array(get_embedding(tech_text))
            
            types_list= option.get("types",[])
            if types_list:
                types="- "+"\n- ".join(types_list)
            else:
                types=""
            type_text = f"Best For roles: {types}"
            v_type = np.array(get_embedding(type_text))
            
            bullets_list=option.get("bullets",[])
            if bullets_list:
                bullets="- "+"\n- ".join(bullets_list)
            else:
                bullets=""
            desc_text = f"""
            Project: {option.get("project",'')}
            Title: {option.get('title', '')}
            Details: {bullets}
            """
            v_desc = np.array(get_embedding(desc_text))

            weighted_sum = (v_tech * W_TECH) + (v_type * W_TYPE) + (v_desc * W_DESC)
            final_vector = weighted_sum / np.linalg.norm(weighted_sum)

            #store important info
            candidates.append({
                "option_data": option,
                "vector": final_vector,
                "text_preview": option.get('title', 'Unknown Title')
            })


    print("ranking projects")
    scored_candidates = []
    for cand in candidates:
        score = cosine_similarity(JD_VECTOR, cand["vector"])
        scored_candidates.append((score, cand["option_data"]))

    # sort by score
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    return get_podium(scored_candidates,project_number)


def get_podium(scored_candidates,project_number):
    selected_projects = set()
    top_projects = []
    for (score,option) in scored_candidates:
        project_name = option.get("project")
        if project_name not in selected_projects:
            top_projects.append(option)
            selected_projects.add(project_name)
            # print_project(score,option)

        if len(selected_projects)>=project_number:
            break

    # print(top_projects)
    return top_projects

def get_presentation(scored_candidates):
    selected_presentations = set()
    top_presentations = []
    for (score,option) in scored_candidates:
        position_name = option.get("position")
        if position_name not in selected_presentations:
            top_presentations.append(option)
            selected_presentations.add(position_name)
            # print_project(score,option)

        if len(selected_presentations)>=1:
            break
    # print("winner presentation=======")
    # print(top_presentations)
    return top_presentations

def print_project(score,option):
    print("="*40)
    print(f"Title:    {option.get('title')}")
    print(f"Subtitle: {option.get('subtitle')}")
    print("Details:")
    for bullet in option.get('bullets', []):
        print(f"  - {bullet}")
    print(f"Types:    {option.get('types')}")
    print(f"Score: {score:.4f})")
    print("-" * 20)


