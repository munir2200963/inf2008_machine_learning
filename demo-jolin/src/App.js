

import React, { useState, useEffect, useRef } from "react";

const App = () => {
  // State management
  const [userId, setUserId] = useState("");
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [view, setView] = useState("enroll"); // "enroll" or "validate"
  const mediaRecorderRef = useRef(null);
  const [timer, setTimer] = useState(0);

  // Enrollment states
  const [sentences, setSentences] = useState([]);
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const [audioRecordings, setAudioRecordings] = useState([]);

  // Validation states
  const [validationSentence, setValidationSentence] = useState("");
  const [validationAudio, setValidationAudio] = useState(null);
  const [validationResult, setValidationResult] = useState(null);

  // Fetch sentences on component mount
  useEffect(() => {
    const fetchSentences = async () => {
      try {
        const response = await fetch("http://localhost:5000/get-sentences");
        const data = await response.json();
        setSentences(data.sentences || []);
      } catch (error) {
        setMessage("❌ Failed to fetch sentences.");
      }
    };

    fetchSentences();
  }, []);

  const startRecording = async () => {
    if (currentSentenceIndex >= sentences.length) {
      setMessage("✅ All sentences recorded!");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      // Set initial timer value
      setTimer(5);

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        setAudioRecordings((prev) => [
          ...prev,
          { sentence: sentences[currentSentenceIndex], audioBlob },
        ]);

        setMessage(`✅ Sentence ${currentSentenceIndex + 1} recorded!`);
        setCurrentSentenceIndex((prev) => prev + 1);
        setTimer(0); // Reset timer when done
      };

      mediaRecorder.start();
      setRecording(true);
      setMessage(`🎙️ Recording sentence ${currentSentenceIndex + 1}...`);

      // Timer countdown
      const timerInterval = setInterval(() => {
        setTimer(prevTimer => {
          if (prevTimer <= 1) {
            clearInterval(timerInterval);
            return 0;
          }
          return prevTimer - 1;
        });
      }, 1000);

      setTimeout(() => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
          setRecording(false);
          clearInterval(timerInterval); // Make sure to clear the interval
        }
      }, 5000);
    } catch (error) {
      setMessage("❌ Error accessing microphone.");
    }
  };

  // Start recording for validation
  const startValidationRecording = async () => {
    if (!userId.trim()) {
      setMessage("❌ Please enter your User ID.");
      return;
    }

    if (!validationSentence) {
      // Pick a random sentence if none is selected
      const randomIndex = Math.floor(Math.random() * sentences.length);
      setValidationSentence(sentences[randomIndex]);
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      // Set initial timer value
      setTimer(5);

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        setValidationAudio(audioBlob);
        setMessage("✅ Validation audio recorded!");
        setTimer(0); // Reset timer when done
      };

      mediaRecorder.start();
      setRecording(true);
      setMessage("🎙️ Recording for validation...");

      // Timer countdown
      const timerInterval = setInterval(() => {
        setTimer(prevTimer => {
          if (prevTimer <= 1) {
            clearInterval(timerInterval);
            return 0;
          }
          return prevTimer - 1;
        });
      }, 1000);

      setTimeout(() => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
          setRecording(false);
          clearInterval(timerInterval); // Make sure to clear the interval
        }
      }, 5000);
    } catch (error) {
      setMessage("❌ Error accessing microphone.");
    }
  };

  // Submit enrollment data
  const handleEnrollmentSubmit = async () => {
    if (!userId.trim()) {
      setMessage("❌ Please enter a user ID.");
      return;
    }

    if (audioRecordings.length !== 20) {
      setMessage(`❌ Please record all 20 sentences before submitting.`);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("user_id", userId);

    audioRecordings.forEach((recording, index) => {
      formData.append(`audio_${index}`, recording.audioBlob, `audio_${index}.wav`);
      formData.append(`sentence_${index}`, recording.sentence);
    });

    try {
      const response = await fetch("http://localhost:5000/enroll", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage("✅ All voice recordings successfully enrolled!");
      } else {
        setMessage(`❌ ${result.error || "An error occurred during enrollment."}`);
      }
    } catch {
      setMessage("❌ Error connecting to the server.");
    } finally {
      setLoading(false);
    }
  };

  // Submit validation data
  const handleValidationSubmit = async () => {
    if (!userId.trim()) {
      setMessage("❌ Please enter your User ID.");
      return;
    }

    if (!validationAudio) {
      setMessage("❌ Please record your voice first.");
      return;
    }

    setLoading(true);
    setValidationResult(null);

    const formData = new FormData();
    formData.append("speaker_name", userId);
    formData.append("text", validationSentence);
    formData.append("trialAudio", validationAudio, "validation.wav");

    try {
      const response = await fetch("http://localhost:5000/validate_trial", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        const isVerified = Number(result.result) === 1;  // ✅ Ensure correct type comparison
        setValidationResult(isVerified);
        setMessage(isVerified ? "✅ Voice authentication successful!" : "❌ Voice authentication failed!");
      } else {
        setMessage(`❌ ${result.error || "An error occurred during validation."}`);
      }
    } catch {
      setMessage("❌ Error connecting to the server.");
    } finally {
      setLoading(false);
    }
  };


  // Pick a random sentence for validation
  const pickRandomSentence = () => {
    const randomIndex = Math.floor(Math.random() * sentences.length);
    setValidationSentence(sentences[randomIndex]);
    setMessage(`Sentence selected. Please record your voice.`);
  };

  // Reset validation form
  const resetValidation = () => {
    setValidationSentence("");
    setValidationAudio(null);
    setValidationResult(null);
    setMessage("");
  };

  // Toggle between enrollment and validation views
  const toggleView = (newView) => {
    setView(newView);
    setMessage("");

    if (newView === "validate") {
      resetValidation();
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.tabs}>
        <button
          onClick={() => toggleView("enroll")}
          style={{
            ...styles.tabButton,
            backgroundColor: view === "enroll" ? "#5e35b1" : "rgba(255, 255, 255, 0.2)",
          }}
        >
          🎤 Enroll Voice
        </button>
        <button
          onClick={() => toggleView("validate")}
          style={{
            ...styles.tabButton,
            backgroundColor: view === "validate" ? "#5e35b1" : "rgba(255, 255, 255, 0.2)",
          }}
        >
          🔍 Validate Voice
        </button>
      </div>

      {view === "enroll" ? (
        <div style={styles.card}>
          <h1 style={styles.header}>🎤 Voice Enrollment</h1>

          <div style={styles.formGroup}>
            <label style={styles.label}>User ID:</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              style={styles.input}
              placeholder="Enter your unique ID"
            />
          </div>

          <div style={styles.sentenceBox}>
            <p style={styles.labelText}><strong>Please read aloud:</strong></p>
            <p style={styles.sentence}>
              {currentSentenceIndex < sentences.length
                ? `"${sentences[currentSentenceIndex]}"`
                : "✅ All sentences recorded!"}
            </p>
          </div>

    

          <button
            onClick={startRecording}
            disabled={recording || currentSentenceIndex >= sentences.length}
            style={{
              ...styles.button,
              backgroundColor: recording ? "#ff9800" : "#0E4D92",
              opacity: (recording || currentSentenceIndex >= sentences.length) ? 0.7 : 1
            }}
          >
            {recording ? `⏺️ Recording... (${timer}s)` : "🎙️ Record Next Sentence"}
          </button>

          <div style={styles.progressSection}>
            <div style={styles.progressBarContainer}>
              <div style={{ ...styles.progressBar, width: `${(currentSentenceIndex / 20) * 100}%` }}></div>
            </div>
            <p style={styles.progressText}>{currentSentenceIndex}/20 sentences recorded</p>
          </div>

          <button
            onClick={handleEnrollmentSubmit}
            disabled={loading || audioRecordings.length < 20}
            style={{
              ...styles.button,
              backgroundColor: "#5DBB63",
              opacity: (loading || audioRecordings.length < 20) ? 0.7 : 1
            }}
          >
            {loading ? "⏳ Processing..." : "Submit Enrollment"}
          </button>

          {message && <p style={styles.message}>{message}</p>}

          {audioRecordings.length > 0 && (
            <div style={styles.recordingsSection}>
              <h3 style={styles.subheader}>Your Recordings</h3>
              <div style={styles.recordingsList}>
                {audioRecordings.slice(Math.max(0, audioRecordings.length - 3)).map((recording, index) => (
                  <div key={index} style={styles.recordingItem}>
                    <div style={styles.recordingInfo}>
                      <span style={styles.recordingNumber}>#{audioRecordings.length - index}</span>
                      <p style={styles.recordingText}>{recording.sentence}</p>
                    </div>
                    <audio controls src={URL.createObjectURL(recording.audioBlob)} style={styles.audioPlayer} />
                  </div>
                ))}
                {audioRecordings.length > 3 && (
                  <p style={styles.moreRecordings}>
                    +{audioRecordings.length - 3} more recordings
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={styles.card}>
          <h1 style={styles.header}>🔍 Voice Validation</h1>

          <div style={styles.formGroup}>
            <label style={styles.label}>User ID:</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              style={styles.input}
              placeholder="Enter your User ID"
            />
          </div>

          <div style={styles.sentenceBox}>
            <p style={styles.labelText}><strong>Validation sentence:</strong></p>
            {validationSentence ? (
              <p style={styles.sentence}>"{validationSentence}"</p>
            ) : (
              <button
                onClick={pickRandomSentence}
                style={{ ...styles.button, backgroundColor: "#009688", marginTop: "10px" }}
              >
                🔄 Get Random Sentence
              </button>
            )}
          </div>

          {validationSentence && (
            <>
              <button
                onClick={startValidationRecording}
                disabled={recording}
                style={{
                  ...styles.button,
                  backgroundColor: recording ? "#ff9800" : "#ff5722",
                  opacity: recording ? 0.7 : 1
                }}
              >
                {recording ? "⏺️ Recording..." : "🎙️ Record Your Voice"}
              </button>

              {validationAudio && (
                <div style={styles.audioPreviewContainer}>
                  <p style={styles.labelText}>Your recording:</p>
                  <audio
                    controls
                    src={URL.createObjectURL(validationAudio)}
                    style={styles.audioPlayer}
                  />

                  <button
                    onClick={handleValidationSubmit}
                    disabled={loading}
                    style={{
                      ...styles.button,
                      backgroundColor: "#03a9f4",
                      opacity: loading ? 0.7 : 1,
                      marginTop: "15px"
                    }}
                  >
                    {loading ? "⏳ Processing..." : "🚀 Validate Voice"}
                  </button>
                </div>
              )}
            </>
          )}

          {validationResult !== null && (
            <div
              style={{
                ...styles.resultBox,
                backgroundColor: validationResult ? "rgba(76, 175, 80, 0.2)" : "rgba(244, 67, 54, 0.2)",
                borderColor: validationResult ? "#4caf50" : "#f44336"
              }}
            >
              <h3 style={{
                ...styles.resultText,
                color: validationResult ? "#4caf50" : "#f44336"
              }}>
                {validationResult ? "✅ Authentication Successful" : "❌ Authentication Failed"}
              </h3>
              <p style={styles.resultDetails}>
                {validationResult
                  ? "Voice pattern matches the enrolled profile."
                  : "Voice pattern does not match the enrolled profile."}
              </p>
              <button
                onClick={resetValidation}
                style={{ ...styles.button, backgroundColor: "#673ab7", marginTop: "15px" }}
              >
                🔄 Try Again
              </button>
            </div>
          )}

          {message && <p style={styles.message}>{message}</p>}
        </div>
      )}
    </div>
  );
};

export default App;

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    minHeight: "100vh",
    background: "linear-gradient(135deg, #6366f1, #a855f7)",
    padding: "20px",
    fontFamily: "'Segoe UI', Roboto, 'Helvetica Neue', sans-serif",
  },
  tabs: {
    display: "flex",
    width: "450px",
    marginBottom: "20px",
    borderRadius: "12px",
    overflow: "hidden",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
  },
  tabButton: {
    flex: 1,
    padding: "14px",
    border: "none",
    fontSize: "16px",
    fontWeight: "600",
    color: "white",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
  },
  card: {
    background: "rgba(255, 255, 255, 0.9)",
    padding: "30px",
    borderRadius: "16px",
    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
    width: "450px",
    textAlign: "center",
    backdropFilter: "blur(10px)",
  },
  header: {
    fontSize: "26px",
    marginBottom: "20px",
    color: "#333",
    fontWeight: "700",
  },
  subheader: {
    fontSize: "20px",
    marginBottom: "15px",
    color: "#444",
    fontWeight: "600",
  },
  formGroup: {
    marginBottom: "20px",
    textAlign: "left",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontSize: "16px",
    fontWeight: "500",
    color: "#444",
  },
  labelText: {
    fontSize: "16px",
    fontWeight: "500",
    color: "#444",
    margin: "5px 0",
  },
  input: {
    width: "100%",
    padding: "12px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    backgroundColor: "#f9f9f9",
    transition: "border-color 0.2s",
    outline: "none",
    boxSizing: "border-box",
  },
  sentenceBox: {
    background: "#fff",
    padding: "16px",
    borderRadius: "12px",
    marginBottom: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
    border: "1px solid #eee",
  },
  sentence: {
    fontSize: "18px",
    fontWeight: "500",
    color: "#333",
    margin: "10px 0",
    lineHeight: "1.5",
  },
  button: {
    width: "100%",
    padding: "14px",
    color: "#fff",
    borderRadius: "8px",
    margin: "10px 0",
    cursor: "pointer",
    border: "none",
    fontSize: "16px",
    fontWeight: "600",
    transition: "all 0.2s ease",
    boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
  },
  progressSection: {
    margin: "20px 0",
    width: "100%",
  },
  progressBarContainer: {
    height: "10px",
    width: "100%",
    background: "#e0e0e0",
    borderRadius: "5px",
    overflow: "hidden",
  },
  progressBar: {
    height: "10px",
    background: "linear-gradient(90deg, #4caf50, #8bc34a)",
    borderRadius: "5px",
    transition: "width 0.3s ease",
  },
  progressText: {
    fontSize: "14px",
    color: "#555",
    margin: "8px 0",
  },
  message: {
    marginTop: "15px",
    padding: "10px",
    borderRadius: "8px",
    backgroundColor: "rgba(0,0,0,0.05)",
    color: "#333",
    fontWeight: "600",
  },
  recordingsSection: {
    marginTop: "25px",
    width: "100%",
    textAlign: "left",
  },
  recordingsList: {
    maxHeight: "300px",
    overflowY: "auto",
    paddingRight: "5px",
  },
  recordingItem: {
    display: "flex",
    flexDirection: "column",
    background: "#f5f5f5",
    padding: "12px",
    borderRadius: "8px",
    marginBottom: "10px",
    border: "1px solid #eee",
  },
  recordingInfo: {
    display: "flex",
    marginBottom: "8px",
  },
  recordingNumber: {
    background: "#673ab7",
    color: "white",
    borderRadius: "50%",
    width: "24px",
    height: "24px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "14px",
    fontWeight: "bold",
    marginRight: "10px",
    flexShrink: 0,
  },
  recordingText: {
    margin: "0",
    fontSize: "14px",
    color: "#555",
    lineHeight: "1.5",
    flex: "1",
  },
  audioPlayer: {
    width: "100%",
    height: "40px",
    outline: "none",
  },
  moreRecordings: {
    textAlign: "center",
    color: "#777",
    fontSize: "14px",
    fontStyle: "italic",
  },
  audioPreviewContainer: {
    marginTop: "20px",
    backgroundColor: "#f5f5f5",
    padding: "15px",
    borderRadius: "12px",
    border: "1px solid #eee",
  },
  resultBox: {
    marginTop: "20px",
    padding: "20px",
    borderRadius: "12px",
    border: "1px solid",
    textAlign: "center",
  },
  resultText: {
    fontSize: "20px",
    margin: "0 0 10px 0",
    fontWeight: "600",
  },
  resultDetails: {
    fontSize: "16px",
    margin: "0 0 10px 0",
    color: "#555",
  }
};