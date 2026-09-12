import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Send,
  Sparkles,
  Volume2,
  VolumeX,
  ShieldCheck,
  Lock,
  HeartHandshake,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  PhoneCall,
  User,
  Bot
} from 'lucide-react';
import { wellnessApi } from '../api/wellness';
import {
  CompanionChatMessage,
  StructuredWellnessSignals,
  CompanionConversationSummary
} from '../types';

interface WellnessCompanionProps {
  personnelId: string;
  onSessionSubmitted?: (session: CompanionConversationSummary) => void;
}

export const WellnessCompanion: React.FC<WellnessCompanionProps> = ({
  personnelId,
  onSessionSubmitted
}) => {
  const [messages, setMessages] = useState<CompanionChatMessage[]>([
    {
      sender: 'ASSISTANT',
      text: 'Namaste! Main SAATHI Wellness Companion hoon. Yeh aapka ek private, voluntary space hai jahan aap duty, rest ya general wellbeing ke baare mein baat kar sakte hain. Aap aaj kaisa mehsus kar rahe hain?',
      timestamp: new Date().toISOString(),
      is_voice: false
    }
  ]);

  const [inputMessage, setInputMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Consent State
  const [consentGiven, setConsentGiven] = useState<boolean>(true);
  const [showConsentModal, setShowConsentModal] = useState<boolean>(false);

  // Voice Recognition & Synthesis State
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [voiceSupported, setVoiceSupported] = useState<boolean>(true);
  const [ttsEnabled, setTtsEnabled] = useState<boolean>(false);
  const [voiceNotice, setVoiceNotice] = useState<string | null>(null);

  // Extracted Signals Live State
  const [liveSignals, setLiveSignals] = useState<StructuredWellnessSignals | null>(null);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [isCrisis, setIsCrisis] = useState<boolean>(false);
  const [longitudinalChange, setLongitudinalChange] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Quick Starters
  const quickPrompts = [
    'Mujhe pichhle kuch dino se continuous night shifts ki wajah se bahut thakaan ho rahi hai.',
    'Meri neend proper nahi ho rahi aur thoda recovery rest chahiye.',
    'Duty ka pressure zyada lag raha hai, breaks nahi mil rahe.',
    'Ghar ki yaad aa rahi hai aur family ki thodi chinta hai.',
    'Sab theek chal raha hai, feeling good and motivated for duty.'
  ];

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'hi-IN';

      recognition.onstart = () => {
        setIsRecording(true);
        setVoiceNotice('Listening... Speak naturally in Hindi or English.');
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsRecording(false);
        setVoiceNotice(null);
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error);
        setIsRecording(false);
        setVoiceNotice('Voice input unavailable — you can continue using text input.');
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    } else {
      setVoiceSupported(false);
    }
  }, []);

  // Scroll to bottom on new message
  useEffect(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  const handleToggleVoiceRecording = () => {
    if (!voiceSupported || !recognitionRef.current) {
      setVoiceNotice('Voice input unavailable — you can continue using text input.');
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.error('Failed to start speech recognition:', err);
        setVoiceNotice('Voice input unavailable — you can continue using text input.');
      }
    }
  };

  const handleSpeakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputMessage;
    if (!textToSend.trim()) return;

    const userMsg: CompanionChatMessage = {
      sender: 'USER',
      text: textToSend.trim(),
      timestamp: new Date().toISOString(),
      is_voice: isRecording || Boolean(voiceNotice?.includes('Listening'))
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await wellnessApi.chatWithCompanion({
        message: textToSend.trim(),
        input_mode: userMsg.is_voice ? 'VOICE' : 'TEXT',
        consent_given: consentGiven,
        conversation_history: updatedMessages.slice(-6)
      });

      const assistantMsg: CompanionChatMessage = {
        sender: 'ASSISTANT',
        text: response.reply,
        timestamp: new Date().toISOString(),
        is_voice: false
      };

      setMessages([...updatedMessages, assistantMsg]);
      setLiveSignals(response.extracted_signals);
      setAiSummary(response.ai_summary);
      setIsCrisis(response.is_crisis);
      setLongitudinalChange(response.change_vs_previous || null);

      if (ttsEnabled) {
        handleSpeakText(response.reply);
      }
    } catch (err: any) {
      console.error('Failed to communicate with companion:', err);
      setError(err.response?.data?.detail || 'Companion service is temporarily unreachable.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (messages.filter((m) => m.sender === 'USER').length === 0) {
      setError('Please share your thoughts before submitting a check-in.');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSubmitSuccess(null);

    try {
      const res = await wellnessApi.submitCompanionSession({
        consent_given: consentGiven,
        input_mode: 'TEXT',
        messages: messages
      });

      setSubmitSuccess('Voluntary wellness conversation recorded for Welfare Officer review. Thank you!');
      if (onSessionSubmitted) {
        onSessionSubmitted(res);
      }
    } catch (err: any) {
      console.error('Failed to submit companion session:', err);
      setError(err.response?.data?.detail || 'Failed to submit check-in session.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Top Banner & Consent Information */}
      <div className="bg-white border border-saathi-border p-4 sm:p-5 rounded-lg shadow-gov flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1 rounded bg-saathi-primarySubtle text-saathi-primary border border-saathi-secondaryLight">
              <Sparkles className="w-4 h-4 text-saathi-primary" />
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-saathi-primary">
              Voluntary AI Welfare Companion
            </span>
          </div>
          <h2 className="text-xl font-black text-saathi-textDark">SAATHI Wellness Companion</h2>
          <p className="text-xs text-saathi-textMuted mt-0.5 max-w-xl">
            A private, voluntary space to share how you're doing. Non-diagnostic decision support designed to help authorized Welfare Officers assist you.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Audio TTS Toggle */}
          <button
            type="button"
            onClick={() => setTtsEnabled(!ttsEnabled)}
            className={`px-3 py-1.5 rounded text-xs font-bold border flex items-center gap-1.5 transition-colors cursor-pointer ${
              ttsEnabled
                ? 'bg-saathi-primarySubtle border-saathi-primary text-saathi-primary'
                : 'bg-saathi-bg border-saathi-border text-saathi-textMuted hover:text-saathi-textDark'
            }`}
            title="Read AI responses aloud"
          >
            {ttsEnabled ? <Volume2 className="w-4 h-4 text-saathi-primary" /> : <VolumeX className="w-4 h-4" />}
            <span>{ttsEnabled ? 'Voice Output ON' : 'Voice Output OFF'}</span>
          </button>

          {/* Privacy & Consent Badge */}
          <button
            type="button"
            onClick={() => setShowConsentModal(true)}
            className="px-3 py-1.5 rounded text-xs font-bold bg-emerald-50 border border-emerald-300 text-emerald-800 hover:bg-emerald-100 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-700" />
            <span>Voluntary & Protected</span>
          </button>
        </div>
      </div>

      {/* High-Risk / Crisis Safety Banner */}
      {isCrisis && (
        <div className="p-4 rounded-lg bg-red-50 border-2 border-red-400 shadow-sm flex items-start gap-3">
          <PhoneCall className="w-6 h-6 text-red-700 shrink-0 mt-0.5 animate-pulse" />
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-red-900">
              Immediate Human Care & Support Assistance
            </h4>
            <p className="text-xs text-red-800 leading-relaxed font-medium">
              Aap akele nahi hain. Agar aap acute strain ya crisis mehsus kar rahe hain, kripya turant apne Base Medical/Welfare Officer se sampark karein ya 24/7 dedicated support helpline par baat karein:
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <span className="text-xs font-mono font-bold text-white bg-red-700 px-3 py-1 rounded shadow-xs">
                KIRAN Helpline: 1800-599-0019
              </span>
              <span className="text-xs text-red-800 font-semibold">
                (Toll-Free, 24/7 Confidential Psychological Support)
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Conversation Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Chat Stream (7 cols) */}
        <div className="lg:col-span-7 flex flex-col h-[520px] bg-white border border-saathi-border rounded-lg shadow-gov overflow-hidden">
          
          {/* Chat Messages */}
          <div className="flex-1 p-4 space-y-3.5 overflow-y-auto bg-saathi-bg">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'ASSISTANT' && (
                  <div className="w-7 h-7 rounded-full bg-saathi-primarySubtle border border-saathi-secondaryLight flex items-center justify-center text-saathi-primary shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[82%] p-3 rounded-lg text-xs leading-relaxed space-y-1 shadow-xs ${
                    msg.sender === 'USER'
                      ? 'bg-saathi-primary text-white rounded-tr-none'
                      : 'bg-white text-saathi-textDark border border-saathi-border rounded-tl-none font-medium'
                  }`}
                >
                  <p>{msg.text}</p>
                  <div className={`flex items-center justify-between text-[10px] pt-1 ${
                    msg.sender === 'USER' ? 'text-emerald-200' : 'text-saathi-textSubtle'
                  }`}>
                    <span>{msg.sender === 'USER' ? 'You' : 'SAATHI Companion'}</span>
                    <span>{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span>
                  </div>
                </div>

                {msg.sender === 'USER' && (
                  <div className="w-7 h-7 rounded-full bg-saathi-primary text-white flex items-center justify-center text-xs font-bold shrink-0 mt-1">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-xs text-saathi-textMuted p-2 bg-white rounded border border-saathi-border w-fit">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-saathi-primary" />
                <span>SAATHI Companion is typing...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div className="p-2 bg-white border-t border-saathi-border flex gap-1.5 overflow-x-auto">
            {quickPrompts.map((prompt, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSendMessage(prompt)}
                disabled={loading}
                className="whitespace-nowrap px-2.5 py-1 rounded bg-saathi-bg hover:bg-saathi-primarySubtle border border-saathi-border text-[11px] text-saathi-textDark font-medium transition-colors shrink-0 cursor-pointer"
              >
                {prompt.length > 35 ? `${prompt.slice(0, 35)}...` : prompt}
              </button>
            ))}
          </div>

          {/* Voice status notice */}
          {voiceNotice && (
            <div className="px-3 py-1 bg-amber-50 border-t border-amber-200 text-[11px] text-amber-900 font-medium flex items-center justify-between">
              <span>{voiceNotice}</span>
              <button
                onClick={() => setVoiceNotice(null)}
                className="text-xs hover:text-black font-bold"
              >
                ×
              </button>
            </div>
          )}

          {/* Input Box */}
          <div className="p-3 bg-white border-t border-saathi-border flex items-center gap-2">
            <button
              type="button"
              onClick={handleToggleVoiceRecording}
              disabled={loading}
              className={`p-2 rounded border transition-all cursor-pointer ${
                isRecording
                  ? 'bg-red-600 text-white border-red-700 animate-pulse'
                  : 'bg-saathi-bg border-saathi-border text-saathi-primary hover:bg-saathi-primarySubtle'
              }`}
              title={isRecording ? 'Stop Voice Recording' : 'Start Voice Input (Speech to Text)'}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Share how you are feeling... (Hindi / English)"
              disabled={loading}
              className="flex-1 bg-saathi-bg border border-saathi-border rounded px-3 py-2 text-xs text-saathi-textDark placeholder-saathi-textSubtle focus:bg-white focus:outline-none focus:border-saathi-primary font-medium"
            />

            <button
              type="button"
              onClick={() => handleSendMessage()}
              disabled={loading || !inputMessage.trim()}
              className="p-2 rounded bg-saathi-primary hover:bg-saathi-primaryLight disabled:bg-saathi-bg disabled:text-saathi-textSubtle text-white transition-colors cursor-pointer shadow-xs"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Signals & Submission Panel (5 cols) */}
        <div className="lg:col-span-5 flex flex-col justify-between space-y-4">
          
          {/* Extracted Structured Signals Card */}
          <div className="bg-white border border-saathi-border p-4 sm:p-5 rounded-lg shadow-gov space-y-3.5">
            <div className="flex items-center justify-between border-b border-saathi-border pb-2.5">
              <div className="flex items-center gap-2">
                <HeartHandshake className="w-4 h-4 text-saathi-primary" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-saathi-textDark">
                  Extracted Voluntary Signals
                </h3>
              </div>
              <span className="text-[10px] font-mono font-bold text-saathi-primary bg-saathi-primarySubtle border border-saathi-secondaryLight px-2 py-0.5 rounded">
                Confidence: {liveSignals ? `${(liveSignals.extraction_confidence * 100).toFixed(0)}%` : '85%'}
              </span>
            </div>

            {liveSignals ? (
              <div className="space-y-2.5">
                {/* Signals Grid */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border">
                    <span className="text-[10px] uppercase font-bold text-saathi-textMuted block">Fatigue</span>
                    <span className={`font-bold mt-0.5 block ${liveSignals.fatigue === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'}`}>
                      {liveSignals.fatigue}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border">
                    <span className="text-[10px] uppercase font-bold text-saathi-textMuted block">Sleep Difficulty</span>
                    <span className={`font-bold mt-0.5 block ${liveSignals.sleep_difficulty === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'}`}>
                      {liveSignals.sleep_difficulty}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border">
                    <span className="text-[10px] uppercase font-bold text-saathi-textMuted block">Workload Pressure</span>
                    <span className={`font-bold mt-0.5 block ${liveSignals.workload_pressure === 'Elevated' ? 'text-orange-700' : 'text-saathi-textDark'}`}>
                      {liveSignals.workload_pressure}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border">
                    <span className="text-[10px] uppercase font-bold text-saathi-textMuted block">Emotional State</span>
                    <span className="font-bold text-saathi-textDark mt-0.5 block">
                      {liveSignals.emotional_exhaustion !== 'None' ? liveSignals.emotional_exhaustion : 'Stable'}
                    </span>
                  </div>
                </div>

                {/* Positive Resilience Indicators */}
                {liveSignals.positive_resilience_indicators.length > 0 && (
                  <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 space-y-1">
                    <span className="text-[11px] font-bold text-emerald-800 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                      <span>Positive Coping Indicators</span>
                    </span>
                    <div className="space-y-0.5">
                      {liveSignals.positive_resilience_indicators.map((res, i) => (
                        <div key={i} className="text-[11px] text-emerald-900 font-medium">
                          • {res}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Longitudinal Delta */}
                {longitudinalChange && (
                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border text-[11px] text-saathi-textMuted">
                    <strong className="text-saathi-textDark block mb-0.5">Change vs Previous Check-In:</strong>
                    {longitudinalChange}
                  </div>
                )}

                {/* AI Summary */}
                {aiSummary && (
                  <div className="p-2.5 rounded bg-saathi-bg border border-saathi-border text-[11px] text-saathi-textDark font-medium">
                    <strong className="text-saathi-primary block mb-0.5 font-bold">AI Non-Clinical Synthesis:</strong>
                    {aiSummary}
                  </div>
                )}
              </div>
            ) : (
              <div className="py-8 text-center text-saathi-textMuted text-xs space-y-1">
                <Sparkles className="w-5 h-5 mx-auto text-saathi-textSubtle" />
                <p>
                  As you share your thoughts, non-clinical welfare indicators will appear here in real time.
                </p>
              </div>
            )}

            {/* Submission Section */}
            <div className="pt-2 border-t border-saathi-border space-y-2">
              <button
                type="button"
                onClick={handleSubmitForReview}
                disabled={submitting || loading}
                className="w-full py-2.5 rounded bg-saathi-saffron hover:bg-saathi-saffronHover disabled:bg-slate-300 text-white font-bold text-xs shadow-xs flex items-center justify-center gap-2 transition-colors cursor-pointer uppercase tracking-wider"
              >
                {submitting ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Recording Voluntary Signals...</span>
                  </>
                ) : (
                  <>
                    <HeartHandshake className="w-4 h-4" />
                    <span>Submit Check-In for Welfare Officer Review</span>
                  </>
                )}
              </button>

              {submitSuccess && (
                <div className="text-xs text-emerald-800 bg-emerald-50 border border-emerald-300 p-2 rounded flex items-center gap-1.5 font-medium">
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-700" />
                  <span>{submitSuccess}</span>
                </div>
              )}

              {error && (
                <div className="text-xs text-red-800 bg-red-50 border border-red-300 p-2 rounded flex items-center gap-1.5 font-medium">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-700" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </div>

          {/* Operational Ethical Guardrail Card */}
          <div className="p-3.5 rounded bg-white border border-saathi-border text-[11px] text-saathi-textMuted space-y-1 shadow-xs">
            <div className="flex items-center gap-1.5 font-bold text-saathi-textDark">
              <Lock className="w-3.5 h-3.5 text-saathi-primary" />
              <span>Ethical AI & Privacy Guardrails</span>
            </div>
            <p className="text-[10px] text-saathi-textMuted leading-relaxed">
              SAATHI is not a diagnostic system. Conversations are voluntary. Raw audio is never permanently retained or used for employee surveillance.
            </p>
          </div>

        </div>
      </div>

      {/* Explicit Consent Modal */}
      {showConsentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white border-2 border-saathi-primary rounded-lg max-w-lg w-full p-5 shadow-gov-lg space-y-3.5">
            <div className="flex items-center gap-2 text-saathi-primary">
              <ShieldCheck className="w-5 h-5 text-saathi-saffron" />
              <h3 className="text-base font-bold text-saathi-textDark uppercase tracking-wider">Voluntary Participation & Privacy Notice</h3>
            </div>

            <div className="text-xs text-saathi-textDark space-y-2 leading-relaxed bg-saathi-bg p-3.5 rounded border border-saathi-border">
              <p>
                <strong>1. Entirely Voluntary:</strong> Participation in the SAATHI Wellness Companion is completely optional. You choose what to share.
              </p>
              <p>
                <strong>2. Non-Diagnostic Decision Support:</strong> SAATHI identifies occupational strain indicators (such as fatigue, duty pressure, or recovery needs). It does not produce psychiatric or medical diagnoses.
              </p>
              <p>
                <strong>3. Confidential Welfare Review:</strong> Signals you voluntarily submit are accessible solely to authorized Welfare Officers for supportive planning. They are never shared with unit commanders as disciplinary records.
              </p>
              <p>
                <strong>4. No Audio Surveillance:</strong> Voice conversation is transcribed locally in browser and processed temporarily. No background recording or voice emotion profiling is conducted.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-1">
              <button
                type="button"
                onClick={() => setShowConsentModal(false)}
                className="px-4 py-1.5 rounded bg-saathi-primary hover:bg-saathi-primaryLight text-white font-bold text-xs shadow-xs transition-colors"
              >
                I Understand & Proceed
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
