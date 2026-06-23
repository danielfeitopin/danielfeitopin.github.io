import logging
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


ENABLED_BLUEPRINTS = { 
    # Blueprint name: website path
    'home': '/'
}

SRC_DIR = Path('src') # Source directory
DST_DIR = Path('site') # Destination directory
BP_DIR = SRC_DIR / 'blueprints' # Blueprints directory
TPL_DIR = SRC_DIR / 'templates' # Templates directory


# Config logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def render_templates(bp_tpl_dir: Path, context: dict) -> str:

    # Check if index.jinja exists in the templates directory
    index_file: Path = bp_tpl_dir / 'index.jinja'

    if index_file.is_file():

        # Create a Jinja2 environment
        env = Environment(loader=FileSystemLoader([bp_tpl_dir, TPL_DIR]))

        # Load and render the index.jinja template
        return env.get_template('index.jinja').render(context)
    else:
        logging.warning(f'index.jinja template not found in {bp_tpl_dir}')
        return ''


def process_templates(bp_src_dir: Path, bp_dst_dir: Path) -> None:

    # Get the templates directory for this blueprint
    bp_tpl_dir: Path = bp_src_dir / 'templates'

    # Create a context dictionary for the template
    context: dict = {
        'bp_name': bp_src_dir.name,
        'bp_path': ENABLED_BLUEPRINTS.get(bp_src_dir.name, '/')
    }

    # Render the templates
    content: str = render_templates(bp_tpl_dir, context)

    # Write rendered content to index.html in the destination directory
    index_file: Path = bp_dst_dir / 'index.html'
    with index_file.open('w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':


    # Create website directory
    DST_DIR.mkdir(exist_ok=True)

    # Copy static files
    static_src_dir: Path = SRC_DIR / 'static'
    static_dst_dir: Path = DST_DIR / 'static'
    if static_src_dir.is_dir():
        static_dst_dir.mkdir(exist_ok=True)
        shutil.copytree(static_src_dir, static_dst_dir, dirs_exist_ok=True)
        logging.info(f'Copied static files from {static_src_dir} to {static_dst_dir}')

    # Get blueprints from src directory
    blueprints: list[Path] = [f for f in BP_DIR.iterdir() if f.is_dir()]
    logging.info(f'Found {len(blueprints)} blueprints: {[f.name for f in blueprints]}')

    # Process enabled blueprints
    blueprints: list[Path] = [bp for bp in blueprints if bp.name in ENABLED_BLUEPRINTS]
    logging.info(f'Enabled blueprints: {[f.name for f in blueprints]}')

    for bp in blueprints:

        # Get blueprint information
        bp_name: str = bp.name
        bp_path: str = ENABLED_BLUEPRINTS[bp.name]
        bp_src_dir: Path = BP_DIR / bp.name

        # Ensure blueprint directory exists
        if bp_src_dir.is_dir():
            logging.info(f"Processing blueprint: '{bp_name}' at path: '{bp_path}'")
        else:
            logging.warning(f"Blueprint directory not found: '{bp_src_dir}'")
            continue

        # Create destination directory for blueprint
        bp_dst_dir: Path = DST_DIR / bp_path.strip('/')
        bp_dst_dir.mkdir(parents=True, exist_ok=True)
        
        # Process blueprint files
        try:

            # Process templates
            process_templates(bp_src_dir, bp_dst_dir)
            logging.debug(f"Rendered index.html for blueprint '{bp_name}'")

        except Exception as e:
            logging.error(f"Error processing blueprint '{bp_name}': {e}")
