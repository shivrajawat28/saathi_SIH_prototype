import { apiClient } from './client';
import {
  WellnessCheckInRequest,
  CompanionChatRequest,
  CompanionChatResponse,
  CompanionSubmitRequest,
  CompanionConversationSummary,
  CompanionReviewRequest,
  VoiceTranscribeResponse
} from '../types';

export const wellnessApi = {
  submitCheckIn: async (checkInData: WellnessCheckInRequest): Promise<{ status: string; message: string }> => {
    const res = await apiClient.post<{ status: string; message: string }>('/wellness/check-in', checkInData);
    return res.data;
  },

  chatWithCompanion: async (chatReq: CompanionChatRequest): Promise<CompanionChatResponse> => {
    const res = await apiClient.post<CompanionChatResponse>('/wellness/companion/chat', chatReq);
    return res.data;
  },

  submitCompanionSession: async (submitReq: CompanionSubmitRequest): Promise<CompanionConversationSummary> => {
    const res = await apiClient.post<CompanionConversationSummary>('/wellness/companion/submit', submitReq);
    return res.data;
  },

  getMyCompanionHistory: async (): Promise<CompanionConversationSummary[]> => {
    const res = await apiClient.get<CompanionConversationSummary[]>('/wellness/companion/history');
    return res.data;
  },

  getPersonnelCompanionSignals: async (personnelId: string): Promise<CompanionConversationSummary[]> => {
    const res = await apiClient.get<CompanionConversationSummary[]>(`/wellness/companion/personnel/${personnelId}`);
    return res.data;
  },

  reviewCompanionConversation: async (
    conversationId: string,
    reviewReq: CompanionReviewRequest
  ): Promise<CompanionConversationSummary> => {
    const res = await apiClient.post<CompanionConversationSummary>(
      `/wellness/companion/${conversationId}/review`,
      reviewReq
    );
    return res.data;
  },

  transcribeVoice: async (textHint?: string, audioBase64?: string): Promise<VoiceTranscribeResponse> => {
    const res = await apiClient.post<VoiceTranscribeResponse>('/wellness/companion/voice-transcribe', {
      text_hint: textHint,
      audio_base64: audioBase64,
      language: 'hi-IN'
    });
    return res.data;
  },

  getCheckInStatus: async (): Promise<import('../types').PersonnelCheckInStatusResponse> => {
    const res = await apiClient.get<import('../types').PersonnelCheckInStatusResponse>('/wellness/check-in-status');
    return res.data;
  }
};
