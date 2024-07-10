## Agents on DSpy
Building an agent using DSPy that can interact with the webarena environment. We are looking to achieve SOTA performance on webarena benchmarking,
by implementing various ideas like:
* [SteP: Stacked LLM Policies for Web Actions](https://arxiv.org/pdf/2310.03720)
* [Tree Search For Language Model Agents](https://jykoh.com/search-agents/paper.pdf)

### Installation
1. Install webarena depedencies
```bash
cd webarena
uv venv -p 3.11 --seed
source .venv/bin/activate
pip install -r requirements.txt
playwright install
pip install -e .
```

2. Configure the environment
```bash
# export MAP="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:3000"
export MAP="https://www.openstreetmap.org"
export SHOPPING="<your_shopping_site_domain>:7770"
export SHOPPING_ADMIN="<your_e_commerce_cms_domain>:7780/admin"
export REDDIT="<your_reddit_domain>:9999"
export GITLAB="<your_gitlab_domain>:8023"
```

3. Obtain the auto-login cookies for all websites
```bash
mkdir -p ./.auth
python browser_env/auto_login.py
```

4. Copy the map configs to config_data folder
```bash
python scripts/generate_test_data.py
grep -ol "\"map\"" config_files/*.json | xargs cp -t ../config_data/
rm ../config_data/test*.json
```

### Running
1. Setup the environment from the root directory
```bash
source webarena/.venv/bin/activate
python -m scripts.evaluate.debug_webarena
```