"""
SAATHI Voluntary AI Welfare Conversation Assistant Schemas
Pydantic data models for non-clinical conversational interactions, voluntary wellness signal extraction,
and human-in-the-loop review.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CompanionChatMessage(BaseModel):
    sender: str = Field(..., description="'USER' or 'ASSISTANT'")
    text: str = Field(..., description="Message text content")
    timestamp: Optional[datetime] = None
    is_voice: Optional[bool] = False

class CompanionChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Voluntary text input from personnel")
    input_mode: Optional[str] = Field("TEXT", description="'TEXT', 'VOICE', or 'VOICE_FALLBACK_TEXT'")
    consent_given: bool = Field(True, description="Explicit consent for welfare signal analysis")
    conversation_history: Optional[List[CompanionChatMessage]] = Field(default_factory=list)

class StructuredWellnessSignals(BaseModel):
    sleep_difficulty: str = Field("None", description="None, Low, Moderate, Elevated, Severe")
    fatigue: str = Field("None", description="None, Low, Moderate, Elevated, Severe")
    workload_pressure: str = Field("None", description="None, Low, Moderate, Elevated, Severe")
    emotional_exhaustion: str = Field("None", description="None, Low, Moderate, Elevated, Severe")
    recovery_difficulty: str = Field("None", description="None, Low, Moderate, Elevated, Severe")
    personal_concern: str = Field("None", description="None, Reported (Homesickness/Family), Elevated")
    morale_concern: str = Field("None", description="None, Moderate, Elevated")
    social_withdrawal: bool = Field(False, description="Whether voluntary withdrawal is indicated")
    positive_resilience_indicators: List[str] = Field(default_factory=list, description="Self-reported strengths/positive signs")
    sentiment_valence: str = Field("Neutral", description="Positive, Neutral, Strained, Negative")
    urgency_level: str = Field("NORMAL", description="NORMAL, MODERATE, ELEVATED, CRISIS")
    extraction_confidence: float = Field(0.85, ge=0.0, le=1.0)
    primary_strain_driver: Optional[str] = None

class CompanionChatResponse(BaseModel):
    reply: str = Field(..., description="Empathetic, non-diagnostic response")
    ai_summary: str = Field(..., description="Concise non-clinical summary of voluntary disclosure")
    extracted_signals: StructuredWellnessSignals
    is_crisis: bool = Field(False, description="True if severe distress/self-harm language is detected")
    urgency_level: str = Field("NORMAL")
    confidence: float = Field(0.85)
    change_vs_previous: Optional[str] = Field(None, description="Longitudinal change vs previous voluntary check-in")
    welfare_signal_impact: Optional[str] = Field(None, description="Non-diagnostic support signal contribution")
    saved_conversation_id: Optional[str] = None

class CompanionSubmitRequest(BaseModel):
    consent_given: bool = Field(True, description="Explicit personnel consent")
    input_mode: str = Field("TEXT", description="TEXT, VOICE, VOICE_FALLBACK_TEXT")
    messages: List[CompanionChatMessage] = Field(..., min_length=1)

class CompanionConversationSummaryResponse(BaseModel):
    id: int
    conversation_id: str
    personnel_id: str
    created_at: datetime
    consent_given: bool
    input_mode: str
    ai_summary: str
    structured_signals: Dict[str, Any]
    confidence: float
    urgency_level: str
    is_crisis: bool
    welfare_signal_impact: Optional[str] = None
    change_vs_previous: Optional[str] = None
    status: str
    welfare_officer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    messages: Optional[List[CompanionChatMessage]] = None

    model_config = ConfigDict(from_attributes=True)

class CompanionReviewRequest(BaseModel):
    status: str = Field(..., description="'ACKNOWLEDGED', 'INTERVENTION_CREATED', 'RESOLVED'")
    notes: Optional[str] = Field(None, max_length=1000, description="Welfare officer notes or follow-up plan")

class VoiceTranscribeRequest(BaseModel):
    audio_base64: Optional[str] = Field(None, description="Optional raw/compressed audio payload")
    text_hint: Optional[str] = Field(None, description="Optional partial transcript or hint")
    language: Optional[str] = Field("hi-IN", description="Language code e.g. hi-IN or en-IN")

class VoiceTranscribeResponse(BaseModel):
    transcript: str
    input_mode: str = "VOICE"
    fallback_used: bool = False
    confidence: float = 0.90
    message: str = "Voice transcribed successfully."
