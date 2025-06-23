import React, { useState, useRef, useEffect } from 'react';

const VoiceRecorder = ({ onRecordingComplete, maxDuration = 120 }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [uploading, setUploading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const intervalRef = useRef(null);
  const analyzerRef = useRef(null);
  const audioContextRef = useRef(null);

  useEffect(() => {
    return () => {
      // Cleanup
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        } 
      });

      // Set up audio analysis for visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyzerRef.current = audioContextRef.current.createAnalyser();
      analyzerRef.current.fftSize = 256;
      source.connect(analyzerRef.current);

      // Start audio level monitoring
      const updateAudioLevel = () => {
        if (analyzerRef.current) {
          const dataArray = new Uint8Array(analyzerRef.current.frequencyBinCount);
          analyzerRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average);
        }
      };
      const audioLevelInterval = setInterval(updateAudioLevel, 100);

      // Set up MediaRecorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        clearInterval(audioLevelInterval);
        setAudioLevel(0);
        
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm;codecs=opus' 
        });
        
        const audioUrl = URL.createObjectURL(audioBlob);
        setRecordedAudio({ blob: audioBlob, url: audioUrl });

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Upload the audio
        await uploadAudio(audioBlob);
      };

      mediaRecorderRef.current.start(1000); // Collect data every second
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          if (newTime >= maxDuration) {
            stopRecording();
          }
          return newTime;
        });
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
      }
    }
  };

  const uploadAudio = async (audioBlob) => {
    setUploading(true);

    try {
      const formData = new FormData();
      const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, {
        type: 'audio/webm'
      });
      formData.append('file', audioFile);

      const response = await fetch('http://localhost:8000/api/v1/upload/audio', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      
      console.log('🎤 Audio processing result:', result);
      
      const audioInfo = {
        id: result.file_id || `audio_${Date.now()}`,
        name: result.filename || `recording_${Date.now()}.webm`,
        type: 'audio/webm',
        size: audioFile.size,
        duration: recordingTime,
        url: URL.createObjectURL(audioBlob),
        uploadedAt: new Date().toISOString(),
        transcription: result.processing_details?.transcription,
        aiResponse: result.response
      };

      if (onRecordingComplete) {
        onRecordingComplete(audioInfo);
      }
      
      // Show transcription result if available
      if (result.response) {
        console.log('✅ Audio transcribed and analyzed:', result.response.substring(0, 100));
      }

    } catch (error) {
      console.error('Audio upload failed:', error);
      alert('Failed to upload audio. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const discardRecording = () => {
    setRecordedAudio(null);
    setRecordingTime(0);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAudioLevelColor = () => {
    if (audioLevel < 30) return 'bg-green-400';
    if (audioLevel < 60) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  return (
    <div className="w-full max-w-md mx-auto p-4">
      {/* Recording Controls */}
      <div className="flex flex-col items-center space-y-4">
        
        {/* Audio Level Visualization */}
        {isRecording && (
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full transition-all duration-100 ${getAudioLevelColor()}`}
              style={{ width: `${Math.min(100, (audioLevel / 128) * 100)}%` }}
            />
          </div>
        )}

        {/* Recording Time */}
        <div className="text-2xl font-mono font-bold text-gray-700">
          {formatTime(recordingTime)}
        </div>

        {/* Control Buttons */}
        <div className="flex items-center space-x-4">
          {!isRecording && !recordedAudio && (
            <button
              onClick={startRecording}
              className="w-16 h-16 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors shadow-lg"
              title="Start Recording"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            </button>
          )}

          {isRecording && (
            <>
              <button
                onClick={pauseRecording}
                className={`w-12 h-12 ${isPaused ? 'bg-green-500 hover:bg-green-600' : 'bg-yellow-500 hover:bg-yellow-600'} text-white rounded-full flex items-center justify-center transition-colors`}
                title={isPaused ? "Resume" : "Pause"}
              >
                {isPaused ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
              </button>

              <button
                onClick={stopRecording}
                className="w-16 h-16 bg-gray-600 hover:bg-gray-700 text-white rounded-full flex items-center justify-center transition-colors shadow-lg"
                title="Stop Recording"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
              </button>
            </>
          )}
        </div>

        {/* Recording Status */}
        {isRecording && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span>{isPaused ? 'Recording Paused' : 'Recording...'}</span>
          </div>
        )}

        {/* Upload Status */}
        {uploading && (
          <div className="flex items-center space-x-2 text-sm text-blue-600">
            <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span>Uploading audio...</span>
          </div>
        )}

        {/* Recorded Audio Playback */}
        {recordedAudio && !uploading && (
          <div className="w-full space-y-3">
            <audio
              controls
              src={recordedAudio.url}
              className="w-full"
            />
            <div className="flex space-x-2">
              <button
                onClick={discardRecording}
                className="flex-1 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Record Again
              </button>
            </div>
          </div>
        )}

        {/* Max Duration Warning */}
        {recordingTime > maxDuration * 0.8 && isRecording && (
          <div className="text-sm text-orange-600 text-center">
            Recording will stop automatically at {formatTime(maxDuration)}
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceRecorder; 