from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool, FileReadTool
import os
from dotenv import load_dotenv
load_dotenv()
import agentops
agentops.init()
from .models import (
    ExtractedContent, EvaluationReport,
    RequirementsList, PersonasList, UserGoalsList, UserStoriesList,
    RequirementMappingsList, CritiqueReport
)

llm1 = LLM(
        model="gemini/gemini-2.5-flash-preview-04-17",
        temperature=0.0,
        # stream=True,
        api_key=os.getenv("GEMINI_API_KEY"),  # Set your Google API key here
        reasoning_effort="high",  # Optional, can be set to "low", "medium", or "high"
    )



def generate_proposal(uploaded_rfp):

    #Agents to create the proposal
    document_reader = Agent(
        role = "Document Reader and Initial Analyzer",
        goal = """Extract structured and meaningful content from RFP documents,
    ensuring no essential information is missed while maintaining
    the original document's integrity and context.""",
        backstory="""You are an exceptional AI document reader with expertise in RFP analysis.
    Your primary strength lies in understanding complex business requirements and technical specifications while maintaining document structure.
    You excel at identifying key sections, requirements, and constraints within RFP documents.
    You note down any ambiguities or potential gaps in the RFP for further clarification.
""",
        verbose=True,
        tools=[FileReadTool(file_path="knowledge/Request for Proposal.txt")],

    )

    requirements_classifier = Agent(
        role="Requirements Classification Specialist",
        goal="""Accurately categorize requirements into Functional, Non-Functional, Business,
    Technical, Legal/Compliance, Operational, and User Requirements categories while maintaining traceability and context.""",
        backstory="""You are a seasoned requirements analyst with deep expertise in software requirements engineering.
    Your strength lies in understanding the nuances between different types of requirements and their implications.
    You excel at identifying dependencies, complexities, and risks associated with each requirement.
    You maintain a keen eye for detail, ensuring that each requirement is categorized correctly and traceable to its source in the RFP. The source should be mentioned as a summary note.""",
        verbose=True,
        tools=[SerperDevTool(
                n_results=40,
                search_type="search",
            )],
    )

    persona_generator = Agent(
        role="Business Persona Specialist",
        goal="""Create detailed, realistic personas that accurately represent the stakeholders
and users who will interact with the system, ensuring comprehensive coverage
of all relevant user types.
You should also ensure that the personas are aligned with the business context and requirements extracted from the RFP.""",
        backstory="""You are an experienced user researcher with a deep understanding of user behavior and business contexts. 
Your expertise lies in creating personas that bridge business requirements with user needs.
You excel at synthesizing complex information into clear, actionable user profiles that guide design and development decisions.""",
        tools=[SerperDevTool(
                n_results=30,
                search_type="search",
        )],
        verbose=True
    )

    goal_identifier = Agent(
        role="User Goals Analyst",
        goal="""Identify and analyze specific user goals within the business context,
ensuring alignment between user needs and business objectives while
maintaining traceability to requirements.""",
        backstory="""You are a user experience strategist with expertise in goal-oriented design.
Your strength lies in understanding user motivations and translating them
into actionable goals."""
    )

    requirement_mapper = Agent(
        role="Requirements-Goals Alignment Specialist",
        goal="""Create clear and traceable mappings between classified requirements and
identified user goals, ensuring comprehensive coverage and alignment
with business objectives.""",
        backstory="""You are a requirements traceability expert with experience in complex
software projects. Your expertise lies in creating clear connections
between business needs and user goals."""
    )

    story_generator = Agent(
        role="User Story Creation Specialist",
        goal="""Generate comprehensive, well-structured user stories that accurately
capture user needs, acceptance criteria, and business value while
maintaining alignment with requirements and goals.""",
        backstory="""You are an agile requirements specialist with expertise in translating
complex requirements into clear, actionable user stories. Your strength
lies in maintaining the balance between user needs and technical feasibility.
You can easily breakdown large requirements into manageable user stories
that can be prioritized and implemented effectively.""",
tools=[SerperDevTool(
                n_results=30,
                search_type="search",
            )],
            verbose=True
    )

    markdown_creator = Agent(
        role="Documentation Specialist",
        goal="""Transform structured content into well-formatted Markdown documentation,
ensuring clarity, readability, and proper organization of all project artifacts.""",
        backstory="""You are a documentation expert with a keen eye for structure and detail.
Your expertise lies in creating clear, navigable documentation that serves
as a single source of truth.
You excel at organizing complex information into user-friendly formats,
ensuring that all project stakeholders can easily access and understand the content.
You maintain consistency in formatting and style across all documents,
ensuring that the documentation is professional and polished.""",
llm=llm1,  # Use the LLM instance defined above
        verbose=True,
    )

    evaluator = Agent(
        role="Quality Assurance Specialist",
        goal="""Review and validate all generated artifacts for completeness, consistency,
and alignment with project objectives while ensuring traceability across
all components.""",
        backstory="""You are a meticulous reviewer with expertise in requirements validation
and quality assurance. Your strength lies in ensuring consistency and
completeness across all project deliverables.
You can easily identify what is missing, what is redundant, and what needs to be clarified.
You excel at ensuring that all artifacts are aligned with the original RFP and business goals,
maintaining a high standard of quality throughout the project lifecycle."""
    )

    tech_stack_recommender = Agent(
        role="Technical Stack Architect",
        goal="""Generate a comprehensive technical report outlining the tech stack required 
to implement the solution, with detailed recommendations for all layers of 
the architecture justified by the RFP requirements and business goals.""",
        backstory="""You are a seasoned technical architect with extensive experience across 
diverse technology ecosystems. Your expertise lies in designing scalable, 
maintainable, and secure technical solutions that precisely align with 
business requirements and project constraints.
You thoroughly analyze the RFP to identify the most suitable technologies,
frameworks, and tools, ensuring that your recommendations are justified for the specific project context.
You do not give generic recommendations; instead, you provide tailored solutions that address the unique challenges and goals outlined in the RFP.
You use the latest industry standards and best practices to ensure that the proposed tech stack is robust, future-proof, and capable of meeting the project's demands."""
    )

    internet_researcher = Agent(
        role="Internet Research and Differentiation Specialist",
        goal="""Search the internet to identify differentiating factors and unique strengths for this proposal, providing clear reasons why this project should be chosen over competitors.""",
        backstory="""You are a skilled online researcher with expertise in competitive analysis. Your strength lies in quickly gathering relevant information from the web, identifying unique selling points, and articulating compelling arguments that highlight the proposal's advantages.
You can easily sift through vast amounts of data to find the most pertinent information that sets this proposal apart from others.
Your strength is understanding the task and then doing relevant internet research by asking the most relevant and specific questions to find the most relevant information. 
The information you find is then rechecked for relevance and accuracy before being included in the proposal.
You know what the right questions are to ask to find the most relevant information, and you can easily identify the most relevant sources of information.""",
tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            verbose=True,
            llm=llm1,
    )

    cost_calculator = Agent(
        role="Project Cost Calculation Specialist",
        goal="""Calculate the total project cost by determining each team member's hourly pay. Aggregate all team members' costs to provide a comprehensive project budget.
If a member works for a week, then for that week the member has worked for 5 days out of week, and then per day the member has worked for 8 hours.
This is how you calculate how many hours a member has worked in a week. 
To calculate the total hours worked during the project, you multiply the hours worked per week by the number of weeks worked. 
Then total cost is calculated by multiplying the total hours worked by the hourly pay of the member.""",
        backstory="""You are a detail-oriented financial analyst specializing in project cost estimation. Your expertise ensures accurate, transparent, and justifiable cost calculations based on team composition and project duration.
You follow a structured approach to cost estimation, ensuring that all financial aspects of the project are covered.""",
verbose=True,
            llm=llm1
    )

    conclusion_writer = Agent(
        role="Formal Conclusion and Contact Specialist",
        goal="""Draft a formal conclusion for the proposal, including clear contact details sourced from the official company webpage to facilitate further communication.
Ensure that the conclusion reinforces the proposal's key points and encourages the client to take the next steps.
you always add a CTA (Call to Action) at the end of the conclusion, encouraging the client to reach out for further discussions or clarifications.
You always make the conclusion very engaging and professional, leaving a positive impression on the client.""",
        backstory="""You are an experienced business communicator with a knack for crafting professional conclusions. 
Your role is to ensure the proposal ends with a strong, actionable closing statement and accurate contact information.
You maintain a formal tone and ensure that all contact details are up-to-date and sourced from the official company webpage, providing a reliable point of contact for the client.""",
tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            verbose=True
    )

    critique = Agent(
        role="Proposal Critique Specialist",
        goal="""Critically evaluate the final proposal by comparing it to the original RFP, identifying gaps, inconsistencies, and areas for improvement in alignment, completeness, and clarity.""",
        backstory="""You are an expert reviewer with a strong background in requirements engineering and proposal evaluation. 
Your expertise lies in objectively assessing deliverables, ensuring they fully address the RFP, and providing actionable, constructive feedback for refinement.
You pinpoint specific areas that need improvement, ensuring that the proposal meets the highest standards of quality and relevance.""",
llm=llm1,  # Use the LLM instance defined above
    )

    refinement = Agent(
        role="Proposal Refinement Specialist",
        goal="""Refine and edit the final proposal based on critique feedback, making only the necessary changes while preserving the structure and content of unaffected sections.""",
        backstory="""You are a meticulous editor and solution architect. Your strength is in implementing targeted improvements, ensuring the proposal is enhanced according to critique remarks without altering sections that do not require changes. You maintain consistency, traceability, and alignment with the original proposal structure.
You only edits the sections that have been critiqued, ensuring that the overall structure and content of the proposal remain intact.
You do not change the structure of the proposal, only the content of the sections that have been critiqued.
You edit the sections after doing a thorough analysis of the critique feedback and proper research, ensuring that all points are addressed and the proposal is improved accordingly.""",
llm=llm1,  # Use the LLM instance defined above
allow_delegation=True,  # Allow delegation to other agents if needed
        verbose=True,
    )

    template_extractor = Agent(
        role="Template Structure Extractor Specialist",
        goal="""Analyze provided proposal template documents and extract their structural outline, including all major sections, subsections, and headings, to create a clear, hierarchical template structure for proposal generation.""",
        backstory="""You are an expert in document analysis and structural extraction. Your primary responsibility is to read template documents, identify and organize their sections and subsections, and produce a structured representation (such as a list or tree) that defines the ideal format for future proposals. You ensure that the extracted structure is comprehensive, accurate, and easy to use as a blueprint for proposal creation and validation.""",
        tools=[FileReadTool(file_path="templates/template2.txt")],
            llm=llm1,
    )

    # Tasks to be performed by the agents
    
    extract_content = Task(
        description="""Extract and analyze the content from the RFP document. 
    This includes identifying key sections, requirements, specifications like in-scope and out-of-scope for the proposal, and timeline information.
    The analysis should capture both explicit and implicit requirements, noting any dependencies or constraints mentioned in the document.
    The extraction should also identify stakeholders, project scope, budget limitations, evaluation criteria, and any compliance or regulatory requirements. 
    Special attention should be paid to technical specifications, service level agreements, and any mentioned success metrics or KPIs.
    Any ambiguities or potential gaps in the RFP should be flagged for further clarification.
    """,
        expected_output= """A comprehensive, structured summary of the RFP content including detailed requirements(both explicit and implicit requirements),any dependencies or constraints, specifications like in-scope and out-of-scope for the proposal, timeline, stakeholders,budget limitations, evaluation criteria, and any compliance or regulatory requirements and constraints.
    The output should be organized into clear hierarchical sections with proper categorization of information.
    It should include metadata tags for each extracted element to facilitate traceability and cross-referencing.
    Any identified ambiguities or potential gaps should be clearly highlighted with explanatory notes.
    """,
    agent= document_reader,
    name="Extracting Content from RFP",
            tools=[FileReadTool(
                    file_path="knowledge\\Request for Proposal.txt"
                ),  # Optional, you can add tools to your task
            ],
            output_pydantic=ExtractedContent,  # Specify the output type
            output_file='output/json/extracted_content.json', 
        # Assign the agent to the task
    )

    classify_requirements = Task(
        description="""This task classifies the extracted requirements into functional, non-functional, business, and technical categories. 
    Each requirement should be analyzed for its type, priority, dependencies, complexity, implementation risk, and business value. 
    The classification should help in understanding the scope and complexity of the project. 
    Additionally, requirements should be tagged with attributes such as 'mandatory' vs 'optional', 'immediate' vs 'future phase', 'core functionality' vs 'enhancement', and 'externally visible' vs 'internal'. 
    For each requirement, identify potential implementation challenges, verification methods, and downstream impacts on other system components.
    """,
    expected_output="""A detailed list of categorized requirements with comprehensive metadata including types, priorities, dependencies, complexity scores, risk assessments, and business value ratings. 
    Each requirement should be uniquely identified, clearly labeled with its primary and secondary categories, and include a traceability matrix to source sections in the RFP. 
    The output should also include a summary of potential implementation challenges, verification methods, and downstream impacts for each requirement.
    """,
    agent=requirements_classifier,
    context=[extract_content],
    name="Classifying Requirements",
            output_pydantic=RequirementsList,
            output_file='output/json/requirements.json'

    )

    generate_personas = Task(
        description="""This task helps in creating detailed user personas based on the RFP requirements and business context.
    Each persona should represent a key stakeholder or user type, including their role, responsibilities, goals, pain points, technical proficiency, daily workflows, decision-making authority, and system usage patterns.
    The personas should help in understanding the end-users' needs, expectations, and behavioral patterns. 
    Including demographic information, professional background, motivations, frustrations with current systems, technology adoption tendencies, and contextual usage scenarios. 
    Each persona should be developed with sufficient depth to guide design decisions and feature prioritization throughout the development lifecycle.
    """,
    expected_output=""" A comprehensive set of user personas with detailed profiles including roles, goals, pain points, technical proficiency levels, usage scenarios, and behavior patterns. 
    Each persona should be presented with a narrative description, visual representation, key characteristics, and contextual scenarios illustrating typical interactions with the system. 
    The personas should be cross-referenced with specific RFP requirements and include assessment of impact on design decisions. The collection should represent the full spectrum of user types from novice to expert, occasional to power users, and operational to strategic stakeholders.
    """,
    agent=persona_generator,
    context=[classify_requirements, extract_content],
      name="Generating User Personas",
            output_pydantic=PersonasList,
            output_file='output/json/personas.json'  # Use the output of classify_requirements as context
    )

    identify_user_goals = Task(
        description="""Identify and define user goals for each persona. 
    These goals should align with the RFP requirements and represent what each user type wants to achieve. 
    The goals should be specific, measurable, achievable, relevant, and time-bound (SMART). 
    For each goal, analyze the underlying motivations, success criteria, potential obstacles, and relationship to business outcomes. 
    Differentiate between primary goals (must-have) and secondary goals (nice-to-have). 
    Map how these goals change throughout the user journey and how they relate to different system functionalities. Consider both explicit goals stated in the RFP and implicit goals derived from understanding of the business context and user needs.
    """,
    expected_output="""A comprehensive list of user goals aligned with each persona's needs, categorized by priority and type. 
    Each goal should be clearly defined with SMART criteria, success metrics, relationship to business outcomes, and connection to specific requirements. 
    The output should include a hierarchical goal structure showing relationships between high-level goals and supporting sub-goals. 
    For each goal, provide contextual scenarios illustrating how users would achieve them through the system, along with acceptance criteria that would indicate successful goal attainment.
    """,
    agent=goal_identifier,
    context=[classify_requirements,generate_personas],
    name="Identifying User Goals",
            output_pydantic=UserGoalsList,
            output_file='output/json/user_goals.json'
    )

    map_requirements = Task(
        description="""Map requirements to user goals and identify coverage, gaps, and overlaps. 
    This mapping should show how each requirement supports specific user goals and help identify any missing requirements or redundancies. 
    The mapping should consider priority, dependencies, implementation complexity, and business impact. 
    Analyze the strength of each requirement-goal relationship (direct support, indirect support, or enabling). 
    Identify potential conflicts between requirements or goals. 
    Evaluate whether the collective requirements fully satisfy each user goal and the overall project objectives. Assess whether requirements properly address non-functional aspects such as performance, security, usability, and scalability for each goal.""",
    expected_output="""A detailed mapping matrix of requirements to user goals with comprehensive coverage analysis. The output should include visual representations showing requirement-goal relationships with strength indicators, gap analysis highlighting under-served goals or over-engineered areas, conflict identification between competing requirements, and traceability to RFP sections. The mapping should include both tabular data and graphical visualizations such as heat maps or network diagrams to illustrate relationship patterns. Recommendations should be provided for addressing identified gaps, resolving conflicts, and optimizing the requirement set to better align with user goals.""",
    agent=requirement_mapper,
    context=[classify_requirements, identify_user_goals, generate_personas],  # Use the outputs of classify_requirements and identify_user_goals as context
    name="Mapping Requirements to User Goals",
            output_pydantic=RequirementMappingsList,
            output_file='output/json/requirements_mapping.json'
    )

    generate_user_stories = Task(
        description="""Generate comprehensive user stories based on the mapped requirements and goals. Each story should follow the format 'As a [persona], I want to [goal] so that [benefit]'. Stories should include detailed acceptance criteria, business value assessments, implementation complexity estimates, and priorities. 
    Consider edge cases and alternative flows for each story. Group related stories into epics where appropriate. Include technical considerations and dependencies between stories. For complex functionalities, break down into multiple granular stories while maintaining traceability to the original requirements and goals. 
    Consider the full user journey and ensure stories collectively provide complete coverage of requirements. For each story, identify potential challenges in implementation and testing.""",
    expected_output="""A comprehensive set of user stories with detailed acceptance criteria, business value metrics, complexity estimates, and priority rankings. 
    Each story should be well-formed with clear persona reference, goal statement, and benefit explanation. 
    Stories should be organized into epics and feature groups with clear relationship indicators. For each story, provide implementation notes, technical considerations, testing approaches, and dependency mappings. 
    The collection should include both happy path and exception path scenarios, with edge cases explicitly addressed. Each story should maintain clear traceability to source requirements, personas, and business objectives.""",
    agent=story_generator,
    context=[classify_requirements, identify_user_goals, map_requirements],  # Use the outputs of classify_requirements and identify_user_goals as context
    name="Generating User Stories",
            tools=[SerperDevTool(
                n_results=30,
                search_type="search",
            )],
            output_pydantic=UserStoriesList,
            output_file='output/json/user_stories.json'
    )

    generate_technical_report = Task(
        description="""Generate a comprehensive technical report outlining the tech stack required to implement the solution mentioned in the proposal. The report should include detailed recommendations for frontend technologies, backend frameworks, database systems, API architectures, cloud infrastructure, DevOps tools, security measures, and third-party integrations. Each recommendation should be justified based on the functional and non-functional requirements identified in the RFP, considering factors such as scalability, performance, security, maintainability, cost-effectiveness, and alignment with business goals. The report should also address potential technical risks and mitigation strategies, along with implementation timeline considerations. Include architectural patterns, data flow diagrams, deployment models, capacity planning guidelines, disaster recovery approaches, and technology governance frameworks. Conduct comparative analysis of alternative technologies with decision matrices showing evaluation criteria. Address technology compatibility issues, integration challenges, and migration strategies if replacing existing systems. Consider future-proofing aspects, extensibility requirements, and emerging technology trends relevant to the domain.""",
        expected_output="""A comprehensive technical report with the following sections: 
    1) Executive Summary of technology recommendations with strategic alignment rationale, 
    2) Detailed System Architecture diagrams with component descriptions and interaction patterns, 
    3) Technology Stack Analysis with in-depth evaluation of each component including version specifications and licensing considerations, 
    4) Comparative Analysis of alternative technologies using multi-dimensional decision matrices, 
    5) Detailed Implementation Roadmap with dependency graphs, critical path analysis and resource requirements, 
    6) Scalability and Performance Engineering guidelines with capacity models and optimization strategies, 
    7) Comprehensive Security Architecture covering authentication, authorization, data protection, network security and compliance controls, 
    8) Development Workflow and DevOps practices including CI/CD pipeline specifications, environment management and quality gates, 
    9) Testing Strategy covering unit, integration, performance, and security testing approaches, 
    10) Deployment Architecture with infrastructure-as-code templates, scaling strategies and monitoring solutions, 
    11) Operational Support Model with incident management processes and SLA frameworks, and 
    12) Technology Risk Register with detailed mitigation strategies. Each section should explicitly trace recommendations back to specific functional and non-functional requirements from the RFP. 
    The report should be well-structured, visually engaging, and suitable for both technical and non-technical stakeholders. It should include diagrams, tables, and charts to enhance clarity and understanding. The report should be written in a professional tone, avoiding jargon where possible, and ensuring accessibility for a diverse audience.""",
    agent=tech_stack_recommender,
    context=[classify_requirements, identify_user_goals, generate_user_stories],  # Use the outputs of classify_requirements and identify_user_goals as context
    name="Generating Technical Report",
            tools=[
                SerperDevTool(
            n_results=50,
            search_type="search",
            # search_engine="serperdev"  # Optional, specify if you want to use a specific search engine
        )
            ],
            output_file='output/intermediate_md/technical_report.md',
            markdown=True,  # Specify that this task outputs markdown

    )

    generate_differentiation_analysis = Task(
        description="""Conduct internet research to identify differentiating factors and unique strengths for this proposal. Analyze competitors and articulate clear, compelling reasons why this project should be chosen over alternatives. Highlight unique value propositions, innovative approaches, and advantages based on market research and industry trends.""",
        expected_output="""A detailed differentiation analysis report summarizing unique selling points, competitive advantages, and clear justifications for selecting this proposal over others. 
    It should mainly focus on why this proposal is different from its competitors and specify its strengths. 
    The report should include evidence from internet research, competitor comparisons, and a list of key strengths.
    The report should not contain sections like executive summary or conclusion, you can add case studies or examples to support the analysis. 
    The report should be structured with clear headings and subheadings, and include visual elements such as charts or tables to enhance understanding. 
    The analysis should be objective, evidence-based, and actionable, with clear distinction between critical differentiators and enhancement opportunities for future consideration.""",
    agent=internet_researcher,
    context=[generate_technical_report],
     name="Generating Differentiation Analysis",
            tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            output_file='output/intermediate_md/differentiation_analysis.md',
            markdown=True,
    )

    calculate_project_cost = Task(
        description="""Calculate the total project cost by determining each team member's hourly pay, multiplying by 8 hours per day, 5 days per week, and the total number of weeks in the project. Aggregate all team members' costs to provide a comprehensive project budget. Ensure transparency and justification for all calculations.""",
        expected_output="""A comprehensive project cost breakdown including per-member calculations, total cost, and summary tables. The output should include assumptions, calculation formulas, and any relevant notes for transparency.
    The cost breakdown should be structured in a clear and organized manner, with sections for each team member's role, hourly rate, total hours, and overall cost. 
    It should also include a buffer of 20% added to the total cost for contingencies. 
    Include a summary table that aggregates all costs and provides a total project budget. 
    The report should be easy to read and understand, with clear labeling and formatting. 
    The cost breakdown should be presented in a way that is suitable for inclusion in the final proposal document.""",
    agent=cost_calculator,
    context=[map_requirements,generate_personas,generate_user_stories],
    name="Calculating Project Cost",
            output_file='output/intermediate_md/project_cost.md',
            markdown=True,
    )

    write_conclusion= Task(
    description=""" Draft a formal conclusion for the proposal, including a strong closing statement and clear contact details sourced from the official company webpage. The conclusion should reinforce the proposal's value and provide actionable next steps for the client.""",
    expected_output="""A well-written conclusion section with a professional closing statement and accurate contact information. 
    The section should be suitable for direct inclusion in the final proposal document. 
    At the bottom of the conclusion, include a call to action encouraging the client to reach out for further discussion or clarification. 
    The contact information should be clearly presented, including name {user_name}, title, email address, and phone number. 
    The conclusion should be concise, persuasive, and aligned with the overall tone of the proposal.
    The conclusion should summarize the key points of the proposal, reiterate the unique value propositions, and express enthusiasm for the opportunity to work with the client. 
    It should also address any potential concerns or questions the client may have, providing reassurance of the team's commitment to delivering a successful project.
    The conclusion should be engaging and leave a positive impression on the client, encouraging them to take the next steps in the decision-making process.""",
    agent=conclusion_writer,
    context=[generate_differentiation_analysis,calculate_project_cost,generate_technical_report],  # Use the outputs of generate_differentiation_analysis and calculate_project_cost as context
    name="Writing Conclusion",
            tools=[SerperDevTool(
                n_results=10,
                search_type="search",
            )],
            output_file='output/intermediate_md/conclusion.md',
            markdown=True,
)
    extract_template_structure = Task(
        description=""" Extract the content of the file and understand the structure of the proposal template from the provided file. 
    This includes identifying all sections, subsections, and their hierarchical relationships. 
    The extraction should focus on the document's organization, including headings, subheadings, and any specific formatting or structural elements that are required for the final proposal.""",
        expected_output="""Read and Extract the content of the file and understand the structure of the proposal template from the provided file. All sections present in the file should be extracted and overview must be provided for each section.
    A structured representation of the proposal template's sections and subsections, including their hierarchical relationships.
    Focus on the document's organization, including headings, subheadings, and any specific formatting or structural elements that are required for the final proposal.
    The output should clearly delineate each section and subsection, providing a comprehensive overview of the proposal's structure.
    The output should be in a format that can be easily referenced and used to guide the creation of the final proposal document. 
    It should include clear labels for each section and subsection, along with any specific formatting requirements or guidelines that need to be followed.
    Make a new section for every heading in the file and their respective subheadings should be included as subsections.""",
        agent=template_extractor,
        name="Extracting Template Structure",
            tools=[FileReadTool(file_path="templates\\template2.txt")],
            output_file='output/intermediate_md/template_structure.md',
            markdown=True,
    )
    create_final_proposal = Task(
        description="""
Create a comprehensive, professional final proposal documentation that synthesizes all analysis and artifacts into a cohesive business and technical solution. This document should articulate the understanding of client needs, proposed approach, implementation strategy, project management methodology, timeline, resource requirements, cost estimates, and expected outcomes. The proposal should be tailored to multiple stakeholder perspectives including business decision-makers, technical evaluators, and end-users. It should demonstrate clear understanding of the RFP requirements, competitive advantages of the proposed solution, risk management approach, quality assurance practices, and post-implementation support plan. The document should be persuasive, addressing potential concerns preemptively and highlighting unique value propositions.""",
        expected_output="""Create a polished, professional proposal document in markdown format for {company_name} for the date: {date}. 
    The document must be well-structured, visually engaging, and suitable for both digital and print distribution. 
    Follow these guidelines:
    ** Include a Cover Page with branding and title. 
    it should contain document name, company name, date, and contact information. 
    It should contain the company logo, prepared by (company_name) and prepared for (client_name), and be visually engaging with proper layout mentioned.**

    ** Make the proposal according to the Extracted Template Structure from the extract_template_structure task, 
    and ensure it meets the highest standards for business and technical documentation. 
    It should strictly follow the template for creation of sections and subsections, 
    ensuring that all required content is included and properly formatted.
    The context data for these sections and subsections can be taken from the tasks in the provided context**


    **Formatting and Style Instructions:**
      - Do not use numbers in section headings.
      - Ensure the document is easy to navigate with a table of contents (in a table format, with links to each section), clear section headers, and cross-references.
      - Write in a professional, business-appropriate tone.
      - Make the content clear, detailed, and free of jargon, so it is accessible to both technical and non-technical readers.
      - Avoid duplicate information or unnecessary repetition.
      - When referencing user stories, goals, or personas, use their names only (not IDs).
      - Use tables for the project plan and cost breakdown.
      - Ensure consistent branding, formatting, and strategic use of visual elements throughout.

    **IMPORTANT NOTE:**
      - The proposal should be comprehensive and persuasive, addressing all required sections.
      - All instructions above must be strictly followed.
      - Take the structure from the extract_template_structure task and use it to create the proposal. The content for sections in the template should be filled in based on the context from calculate_project_cost, generate_user_stories, generate_technical_report, generate_differentiation_analysis, write_conclusion, and any other relevant tasks for the relevant sections in the proposal.""",
      agent=markdown_creator,
      context=[extract_template_structure, calculate_project_cost, generate_user_stories, generate_technical_report, generate_differentiation_analysis, write_conclusion],  # Use the outputs of extract_template_structure and other tasks as context
      name="Creating Final Proposal",
            markdown=True,  # Specify that this task outputs markdown
            output_file='output/final_md/proposal.md',
    )
    evaluate_output =Task(
        description="""Conduct a comprehensive evaluation of all generated artifacts for completeness, consistency, accuracy, traceability, and alignment with the original RFP requirements. 
    This evaluation should include both automated checks and expert review perspectives. Verify that all requirements are properly classified and prioritized; all personas have comprehensive profiles and associated goals; all goals are measurable and mapped to requirements; all user stories are complete with acceptance criteria and follow best practices; and all documentation maintains consistent terminology and cross-references. Identify potential gaps, inconsistencies, ambiguities, or areas needing enhancement. Analyze whether the solution addresses both explicit and implicit needs identified in the RFP. Check for technical feasibility of proposed approaches and alignment with industry best practices. Assess whether non-functional requirements such as performance, security, scalability, and usability are adequately addressed throughout all artifacts.""",
    expected_output=""" A detailed evaluation report with both executive summary and in-depth analysis sections. The report should include: 
    1) Comprehensive quality metrics for each artifact type, 
    2) Traceability analysis showing coverage of RFP requirements, 
    3) Consistency check results across all documentation, 
    4) Gap analysis with specific recommendations for improvement, 
    5) Risk assessment of identified issues with severity ratings, 
    6) Prioritized action items for addressing findings, 
    7) Comparative analysis against industry standards and best practices,
    8) Visual dashboards showing quality metrics and coverage statistics. The evaluation should be objective, evidence-based, and actionable, with clear distinction between critical issues requiring immediate attention and enhancement opportunities for future consideration.
    9)Update the proposal document with any necessary changes based on the evaluation findings.
    10)Check the formatting and structure of the proposal document to ensure it meets the requirements specified in the create_final_proposal task.
    11)Ensure that all sections are properly linked in the table of contents and that the document is easy to navigate.
""",
agent=evaluator,
context=[create_final_proposal],
name="Evaluating Generated Artifacts",
            output_pydantic=EvaluationReport,
            output_file='output/json/evaluation_report.json'
    )

    critique_proposal = Task(
        description="""Critically evaluate the final proposal by comparing it to the original RFP and Proposal Template. 
    Identify any gaps, inconsistencies, or misalignments with the RFP requirements or the Proposal Template structure, and provide clear, actionable feedback for improvement. 
    The critique should be objective, comprehensive, and reference specific sections of both documents. 
    Highlight strengths, weaknesses, and areas needing refinement.
    You dont edit the final proposal, you just provide a detailed critique report that can be used by the refinement agent to make targeted improvements. 
    The critique should be structured to facilitate easy understanding and actionable feedback.
    The critique evaluates each section of the proposal against the required structure and content, ensuring it meets the highest standards for business and technical documentation. 
    The critique should also assess the overall quality of the proposal, including formatting, style, and clarity.
""",
    expected_output="""The output must be a detailed, actionable critique report that references the exact structure and content required for a top-tier professional proposal. 
    The critique should:
    
    1. Clearly state whether the final proposal strictly follows the required document structure as outlined above, identifying any missing or misplaced sections.
    2. Assess the quality and completeness of each section, referencing the specific content that should be present in each section according to the Proposal Template. Go through each section and subsection of the proposal and evaluate its content against the requirements specified in the RFP and the structure from Proposal template.
    3. Evaluate formatting and style: section headers, cross-references, tone, clarity, and visual consistency.
    4. Identify any gaps, inconsistencies, or misalignments with the RFP and Proposal template, and provide specific, actionable recommendations for improvement, referencing the relevant section(s).
    5. Highlight strengths and best practices observed in the proposal.
    6. Structure the critique so it can be directly used by the refinement agent to make targeted improvements.
    7. Verify that proposal document is structured according to the template extracted in the extract_template_structure task.
    
    The critique must be comprehensive, objective, and written in a professional, constructive tone. 
    It should enable the refinement agent to produce a proposal that meets the highest standards for business and technical documentation.""",
    agent=critique,
    context= [create_final_proposal, extract_template_structure,extract_content],  # Use the outputs of create_final_proposal and extract_template_structure as context
     name="Critiquing Proposal",
            output_pydantic=CritiqueReport,
            output_file='output/json/critique_report.json',
    )

    refine_proposal = Task(
        description="""Refine and edit the final proposal based on the critique report. 
    Only make changes to the sections and content specifically mentioned in the critique, preserving the structure and content of all other sections as in the original proposal.
    Ensure the revised proposal fully addresses the critique feedback while maintaining consistency and traceability.
    Maintain the Document Structure , the same as the create_final_proposal task and extract_template_structure task,check if both of them follow the same structure and follow the critique_proposal task to make the necessary edits and ensure the proposal is ready for direct delivery to the client.
   
    **Formatting and Style Instructions:**
      - Do not use numbers in section headings.
      - Do not include any code formatting or markdown/code fences such as ```markdown ``` or ```json```.
      - Ensure the document is easy to navigate with a table of contents (in a table format, with links to each section), clear section headers, and cross-references.
      - Write in a professional, business-appropriate tone.
      - Make the content clear, detailed, and free of jargon, so it is accessible to both technical and non-technical readers.
      - Avoid duplicate information or unnecessary repetition.
      - When referencing user stories, goals, or personas, use their names only (not IDs).
      - Use tables for the project plan and cost breakdown.
      - Ensure consistent branding, formatting, and strategic use of visual elements throughout.

    **Notes:**
      - The proposal should be comprehensive and persuasive, addressing all required sections.
      - All instructions above must be strictly followed.""",
      expected_output="""The output must be a fully revised, professional proposal document that strictly follows the required structure and content standards as specified by the critique report and has all the contents intact.

    The refinement is done only to the sections and content explicitly identified in the critique report, ensuring that all other sections remain unchanged from the original proposal. The refined proposal must not change anything that was not mentioned in the critique report and rewrite such sections as they were in the original proposal.

    Specifically:
    1. Only update the sections and content explicitly identified in the critique report, leaving all other sections unchanged from the original proposal.
    2. Ensure the revised sections fully address the critique's recommendations, including:
        - Adding or correcting any missing, incomplete, or misplaced sections.
        - Enhancing clarity, detail, and alignment with the RFP where required.
        - Improving formatting, cross-references, and visual consistency as needed.
        - Ensuring all tables, links, and visual elements are present and correctly formatted.
        - Updating the sections of the proposal with the content from the critique_proposal task and keeping other content intact from create_final_proposal task.
    3. Maintain the overall structure, branding, and style of the original proposal for all unchanged sections.
    4. The final output must be ready for direct delivery to the client, meeting the highest standards for business and technical proposals.
    
    The refined proposal must be comprehensive, visually engaging, and strictly adhere to all structure, content, and style requirements. Only the necessary changes should be made, ensuring consistency and traceability throughout the document.""",
    agent=refinement,
    context=[create_final_proposal, critique_proposal],  # Use the outputs of create_final_proposal and critique_proposal as context
    name="Refining Proposal Based on Critique",
            output_file='output/final_md/refined_proposal.md',
            markdown=True,  # Specify that this task outputs markdown,
            human_input=True
    )

    crew = Crew(
        name = "Proposal Maker Crew",
        agents=[], #fill in with the agents you want to use
        tasks=[], #fill in with the tasks you want to use
        process=Process.sequential,
        verbose=True,
        max_rpm=30
    )

    crew.kickoff()
