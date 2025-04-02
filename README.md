# 📌 Legacy Python Codebase Analyzer

## 📖 About The Project
### ❗ Problem Statement
Legacy codebases often present significant challenges due to their complexity and lack of documentation. Understanding their functionality and business requirements is difficult, as traditional heuristic methods of code analysis fail to provide a comprehensive view of the code’s intent and behavior.

### 💡 Solution Approach
To address these challenges, we employ a hybrid approach that integrates traditional heuristic techniques with advanced Generative AI (GenAI) capabilities. This combination allows for a deeper and more thorough understanding of the codebase, ensuring alignment with business requirements.

## 🚀 Getting Started
This section provides instructions on how to set up the project locally.

### 📋 Prerequisites
Ensure you have the following installed before proceeding:
- Python >= 3.13
- Poetry-core >= 2.0.0
- VS Code

### ⚙ Installation
Follow these steps to set up the project:

1. Clone the repository:  
   `git clone git@github.com:andreykukalev/codebase-analyzer.git`

2. Open the cloned folder in VS Code.

3. Install dependencies:  
   `poetry install`

4. Activate the virtual environment:  
   - **Windows:**  
     `.venv\Scripts\activate`  
   - **macOS/Linux:**  
     `source .venv/bin/activate`

5. Initialize the `.env` file with local settings:
    ```ini
    MODEL_NAME=<MODEL_NAME>
    API_KEY=<API_KEY>
    BASE_URL=<BASE_URL>
    TEMPERATURE=0.3
    CLONE_DIR_PATH=<CLONE_DIR_PATH>
    REPORT_DIR_PATH=<REPORT_DIR_PATH>
    TRACES_DIR_PATH=<TRACES_DIR_PATH>

6. Run **run.py** in VS Code to check everything works correctly:
   `python run.py`

## 🛠 Usage
To analyze a legacy Python codebase:

1. Run **run.py** in VS Code:  
    `python run.py`

2. When prompted, provide the following details in the terminal:
    - SSH link to the repository containing the Python codebase to analyze;
    - Report name, which will be used as output file name;

3. Wait for the analysis to complete. The processing time depends on the complexity of the codebase.

4. Once finished, locate the generated report in the directory specified by the *REPORT_DIR_PATH* setting in your **.env** file.

5. If you're interested in reviewing trace content to assess how well the agent processed the codebase, you can find intermediate outputs in the directory set in *TRACES_DIR_PATH* within the **.env** file.

## 🤝 Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:  
`git checkout -b feature/YourFeature`
3. Commit your changes:  
`git commit -m 'Add YourFeature'`
4. Push to the branch:  
`git push origin feature/YourFeature`
5. Open a Pull Request.

## 🎖 Acknowledgments
- [Poetry](https://python-poetry.org/) for dependency management.
- [NetworkX](https://networkx.org/) for graph-based analysis.
- [Abstract Syntax Trees](https://docs.python.org/3/library/ast.html) for parsing python code.
- The open-source community for tools and inspiration.

## 📬 Contact
For questions or feedback, feel free to open an issue on GitHub or contact the maintainers at [andrey_kukalev@live.com](mailto:andrey_kukalev@live.com).

## 📜 License
This project is licensed under the MIT License. More details: [MIT License](https://rem.mit-license.org)


