from crewai import Crew, Agent, LLM, Task
from dotenv import load_dotenv
from crewai_tools import DirectoryReadTool, FileReadTool
load_dotenv()
import os

def editing(instructions:str):
    senior_editor=Agent(
        role="Senior Editor in Chief",
        goal=f"""Your task is to edit a proposal to according to the {instructions} provided by the user.
        You will be given a proposal and set of instructions """,
        backstory="""You are a senior editor in chief with years of experience in editing proposals. You are an expert in refining and polishing written documents to ensure they are clear, concise, and compelling.
        You have a deep understanding of proposal writing and are skilled at identifying areas for improvement. You are able to provide constructive feedback and suggestions to enhance the overall quality of the proposal.
        You are known for your attention to detail and your ability to make proposals shine.
        You have a keen eye for grammar, style, and structure, and you are able to provide constructive feedback to improve the proposal.""",
        llm=LLM(
            model="gemini/gemini-2.0-flash",
            temperature=0,
            api_key=os.getenv("GEMINI_API_KEY")
        ),
        tools=[DirectoryReadTool(
            directory="../../output"
        ), FileReadTool(
            file_path="../../output/final_md/refined_proposal.md"
        )],
        verbose=True,
    )

    editing_task=Task(
        name="Edit Proposal",
        description=f"""Edit the proposal that you read from the FileReadTool tool and edit it according to the {instructions} provided by the user.""",
        expected_output=f"""You edit the proposal that you read from the FileReadTool tool and edit it according to the {instructions} provided by the user.
        You are an expert and only edit the portions that the user has requested.You keep the rest of the proposal intact and write it as it is""",
        agent=senior_editor,
        markdown=True,
        output_file="output/edited_proposal.md"
    )


    crew = Crew(
        tasks=[editing_task],
        agents=[senior_editor],
        name="Proposal Editing Crew",
        max_rpm=30,
        verbose=True,
    )

    print(crew.kickoff())


while True:
    user_instructions = input("Enter your instructions for editing the proposal (or type 'exit' or 'q' to quit): ")
    if user_instructions.lower() == 'exit' or user_instructions.lower() == 'q':
        print("Exiting the editing process.")
        break
    editing(user_instructions)