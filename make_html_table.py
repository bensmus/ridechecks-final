import jinja2
from typing import Dict, List

def make_html_table(
        multiple_day_assignments: Dict[str, Dict[str, str]], 
        rides: List[str], template_path, output_path: str) -> None:
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_path)
    output_text = template.render({
        'multiple_day_assignments': multiple_day_assignments,
        'rides': rides
    })
    with open(output_path, 'w') as f:
        f.write(output_text)
