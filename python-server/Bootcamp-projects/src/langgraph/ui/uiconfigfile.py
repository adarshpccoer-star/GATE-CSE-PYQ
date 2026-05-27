from configparser import ConfigParser


class Config:

    def __init__(self, config_file="./src/langgraph/ui/uiconfigfile.ini"):
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        # List comprehension strips accidental spaces around elements
        return [opt.strip() for opt in self.config["DEFAULT"].get("LLM_OPTIONS").split(",")]

    def get_usecase_options(self):
        # List comprehension strips accidental spaces around elements
        return [opt.strip() for opt in self.config["DEFAULT"].get("USECASE_OPTIONS").split(",")]

    def get_groq_model_options(self):
        # List comprehension strips accidental spaces around elements
        return [opt.strip() for opt in self.config["DEFAULT"].get("GROQ_MODEL_OPTIONS").split(",")]

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")