from langchain.prompts import PromptTemplate

extract_insights_prompt = PromptTemplate(
    input_variables=["method_graph", "classes_data"],
    template="""
        You are an expert in business analysis and python software engineering.
        You must extract and summarize all insights about business logic and functional requirements using data below.
        
        Classes and methods, extracted after parsing codebase:
        {classes_data}

        Methods  directed graph, which is built using AST trees:
        {method_graph}

        YOU MUST IDENTIFY:
        - Key functionalities provided by the codebase
        - Main business processes implemented in the functions
        - Dependencies and relationships between functions
        - Any inferred high-level business requirements
        
        YOU MUST CREATE AND APPEND TABLE USING INPUT INFORMATION SUCH AS:
        - classes and methods names
        - class and methods relations
        - method arguments
        - any availavle docstrings and comments 

        FORMAT OF THE TABLE:
        | **File Path** | **Class** | **Methods** | **Arguments** | **Returns** | **Dependencies** | **Functionality** | **Business Process** |
    """
)

format_markdown_prompt = PromptTemplate(
    input_variables=["collected_insights"],
    template="""
        You are an expert technical writer. 
        You must generate a structured Markdown report, using Collected Insights about business requirements, key functionalities and dependencies.
        
        Collected Insights:
        {collected_insights}
        
        The report MUST have following structure:
        - ## High-Level Summary of Business Logic
            - Which product the given codebase represents;
            - What the product supports;
            - Key business requirements in form of bullet list;

        - ## Breakdown of Functionalities and Corresponding Methods
            - List of functionality with classes and methods specification implemented given functionality
            - Each method must contain description (if docstring is available)

        - ## Method Invocation Paths
        - ## Links to Corresponding Code Files
            Add following text to the section if actual urls are not available (Note: Replace `#` with actual file paths or URLs if available.)

        - ## Summary
            Any observations in free form about codebase, design and functional purposes

        EXAMPLE:
        
        # CRM System Codebase Analysis Report

        ## High-Level Summary of Business Logic
        The provided codebase represents...

        ---

        ## Breakdown of Functionalities and Corresponding Methods

        ### 1. ****
        - **Methods**:
            - 
            - 
            - 
        - **Classes**:

        ### 2. ****
        - **Methods**:
            -
            -
            -
        - **Classes**:

        ---

        ## Method Invocation Paths

        ### 1. ****
        - 
        -

        ### 2. ****
        - 
        - 

        ---

        ## Path to Corresponding Code File
        - ****: [/dir/filename.py](#)
        - ****: [/dir/filename.py](#)

        ---

        ## Conclusion
        The product is...
    """
)