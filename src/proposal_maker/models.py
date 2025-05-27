from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RequirementType(str, Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    BUSINESS = "business"
    TECHNICAL = "technical"

class ExtractedContent(BaseModel):
    """Model for extracted RFP content"""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(..., description="Title of the RFP document")
    summary: str = Field(..., description="Brief summary of the RFP")
    requirements: List[str] = Field(..., description="List of requirements extracted from the RFP")
    specifications: List[str] = Field(..., description="Technical specifications from the RFP")
    timeline: Dict[str, Any] = Field(..., description="Project timeline information")
    constraints: List[str] = Field(default=[], description="Any constraints mentioned in the RFP")
    dependencies: List[str] = Field(default=[], description="Dependencies between requirements")

class Requirement(BaseModel):
    """Model for a single requirement."""
    id: str = Field(..., description="Unique identifier for the requirement")
    description: str = Field(..., description="Description of the requirement")
    type: RequirementType = Field(..., description="Type of requirement")
    priority: PriorityLevel = Field(..., description="Priority level of the requirement")
    category: str = Field(..., description="Category of the requirement")
    dependencies: List[str] = Field(default=[], description="IDs of dependent requirements")

    @field_validator('id')
    def validate_id(cls, v):
        if not v.startswith('REQ-'):
            raise ValueError('Requirement ID must start with REQ-')
        return v

class RequirementsList(BaseModel):
    """Wrapper model for list of requirements."""
    requirements: List[Requirement] = Field(..., description="List of requirements")

class UserPersona(BaseModel):
    """Model for a user persona."""
    id: str = Field(..., description="Unique identifier for the persona")
    name: str = Field(..., description="Name of the persona")
    role: str = Field(..., description="Role of the persona")
    goals: List[str] = Field(..., description="List of goals for this persona")
    pain_points: List[str] = Field(..., description="List of pain points for this persona")
    technical_proficiency: str = Field(..., description="Technical proficiency level")

    @field_validator('id')
    def validate_id(cls, v):
        if not v.startswith('PERSONA-'):
            raise ValueError('Persona ID must start with PERSONA-')
        return v

class PersonasList(BaseModel):
    """Wrapper model for list of personas."""
    personas: List[UserPersona] = Field(..., description="List of user personas")

class UserGoal(BaseModel):
    """Model for a user goal."""
    id: str = Field(..., description="Unique identifier for the goal")
    persona_id: str = Field(..., description="ID of the persona this goal belongs to")
    description: str = Field(..., description="Description of the goal")
    priority: PriorityLevel = Field(..., description="Priority level of the goal")
    requirements: List[str] = Field(..., description="List of requirement IDs that support this goal")

    @field_validator('id')
    def validate_id(cls, v):
        if not v.startswith('GOAL-'):
            raise ValueError('Goal ID must start with GOAL-')
        return v

class UserGoalsList(BaseModel):
    """Wrapper model for list of user goals."""
    goals: List[UserGoal] = Field(..., description="List of user goals")

class UserStory(BaseModel):
    """Model for a user story."""
    id: str = Field(..., description="Unique identifier for the user story")
    title: str = Field(..., description="Title of the user story")
    description: str = Field(..., description="Description of the user story")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    business_value: str = Field(..., description="Business value of the user story")
    priority: PriorityLevel = Field(..., description="Priority level of the user story")
    requirements: List[str] = Field(..., description="List of requirement IDs covered by this story")

    @field_validator('id')
    def validate_id(cls, v):
        if not v.startswith('STORY-'):
            raise ValueError('Story ID must start with STORY-')
        return v

class UserStoriesList(BaseModel):
    """Wrapper model for list of user stories."""
    stories: List[UserStory] = Field(..., description="List of user stories")

# class RequirementMapping(BaseModel):
#     """Model for mapping requirements to goals."""
#     requirement_id: str = Field(..., description="ID of the requirement")
#     goal_id: str = Field(..., description="ID of the goal")
#     coverage_status: str = Field(..., description="Status of coverage (full/partial/none)")
#     notes: Optional[str] = Field(None, description="Additional notes about the mapping")

# class RequirementMappingsList(BaseModel):
#     """Wrapper model for list of requirement mappings."""
#     mappings: List[RequirementMapping] = Field(..., description="List of requirement mappings")
class RequirementMappingsList(BaseModel):
    """Model for mapping requirements to goals without nested structure."""
    requirement_ids: List[str] = Field(..., description="List of requirement IDs")
    goal_ids: List[str] = Field(..., description="List of corresponding goal IDs (same index as requirement_ids)")
    coverage_statuses: List[str] = Field(..., description="List of coverage statuses (full/partial/none) for each mapping")
    notes: List[Optional[str]] = Field(default_factory=list, description="List of additional notes for each mapping (optional)")
    

class EvaluationReport(BaseModel):
    """Model for evaluation report."""
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the evaluation")
    completeness_score: float = Field(..., description="Score for completeness of artifacts")
    consistency_score: float = Field(..., description="Score for consistency between artifacts")
    gaps_identified: List[str] = Field(..., description="List of identified gaps")
    recommendations: List[str] = Field(..., description="List of recommendations")
    overall_status: str = Field(..., description="Overall status of the evaluation")

class CritiqueReport(BaseModel):
    strictly_follows_structure: bool = Field(..., description="Whether the proposal strictly follows the required document structure")
    missing_or_misplaced_sections: List[str] = Field(..., description="List of missing or misplaced sections")
    section_names: List[str] = Field(..., description="List of all required section names in order")
    section_present: List[bool] = Field(..., description="Whether each section is present in the proposal, in order of section_names")
    section_quality: List[str] = Field(..., description="Assessment of quality and completeness for each section, in order of section_names")
    section_recommendations: List[Optional[str]] = Field(..., description="Actionable recommendations for improvement for each section, if any, in order of section_names")
    section_strengths: List[Optional[str]] = Field(..., description="Strengths or best practices observed in each section, in order of section_names")
    formatting_section_headers: str = Field(..., description="Assessment of section headers formatting and clarity")
    formatting_cross_references: str = Field(..., description="Assessment of cross-references and links")
    formatting_tone: str = Field(..., description="Assessment of tone and professionalism")
    formatting_clarity: str = Field(..., description="Assessment of clarity and jargon-free writing")
    formatting_visual_consistency: str = Field(..., description="Assessment of branding, formatting, and visual consistency")
    gaps: List[str] = Field(..., description="List of gaps, inconsistencies, or misalignments with the RFP")
    improvement_recommendations: List[str] = Field(..., description="Actionable recommendations for improvement, referencing relevant sections")
    overall_strengths: List[str] = Field(..., description="Strengths and best practices observed in the proposal")
    summary_for_refinement: str = Field(..., description="Summary of changes to be made, structured for the refinement agent")
    professional_tone: str = Field(..., description="Confirmation that the critique is written in a professional, constructive tone")

class RefinedProposalInput(BaseModel):
    original_proposal_path: str = Field(..., description="Path to the original proposal document")
    critique_report: CritiqueReport = Field(..., description="The critique report to be used for refinement")
    # Optionally, you can add a field for the output path or metadata

class RefinedProposalOutput(BaseModel):
    refined_proposal_path: str = Field(..., description="Path to the refined proposal document")
    changes_made: List[str] = Field(..., description="List of sections/changes made as per the critique report")
    unchanged_sections: List[str] = Field(..., description="List of sections that were left unchanged from the original proposal")
    summary: str = Field(..., description="Summary of the refinement process and final quality")