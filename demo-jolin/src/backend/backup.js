// import React, { useState, useEffect, useCallback } from "react";

// const styleConstants = {
//   colors: {
//     primary: "#4f46e5", // indigo
//     primaryHover: "#4338ca",
//     secondary: "#6b7280", // gray
//     secondaryHover: "#4b5563",
//     success: "#10b981", // green
//     successHover: "#059669",
//     danger: "#ef4444", // red
//     dangerHover: "#dc2626",
//     verify: "#3b82f6", // blue
//     verifyHover: "#2563eb",
//     lightBg: "#f9fafb",
//     darkText: "#111827",
//     lightText: "#ffffff",
//     border: "#e5e7eb",
//     cardBg: "#ffffff",
//     lightBorder: "#f3f4f6",
//     lightGray: "#f3f4f6",
//     midGray: "#9ca3af"
//   },
//   shadows: {
//     small: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
//     medium: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
//     large: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
//   },
//   radius: {
//     small: "4px",
//     medium: "8px",
//     large: "12px",
//     xl: "16px",
//   }
// };

// const App = () => {
//   const [userId, setUserId] = useState("");
//   const [audioBlob, setAudioBlob] = useState(null);
//   const [recording, setRecording] = useState(false);
//   const [message, setMessage] = useState("");
//   const [mediaRecorder, setMediaRecorder] = useState(null);
//   const [audioURL, setAudioURL] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [recordingTime, setRecordingTime] = useState(0);
//   const [visualizerData, setVisualizerData] = useState([]);
//   const [recordingFeedback, setRecordingFeedback] = useState("");
//   const [isEnrolled, setIsEnrolled] = useState(false);

  
//   // Define stopRecording as a useCallback to avoid dependency issues
//   const stopRecording = useCallback(() => {
//     if (mediaRecorder && mediaRecorder.state === "recording") {
//       mediaRecorder.stop();
//       setRecording(false);
//     }
//   }, [mediaRecorder]);
  
//   // Timer effect for recording countdown
//   useEffect(() => {
//     let interval;
//     if (recording) {
//       interval = setInterval(() => {
//         setRecordingTime(prev => {
//           const newTime = prev + 1;
//           if (newTime >= 30) {
//             stopRecording();
//           }
//           return newTime;
//         });
//       }, 1000);
//     } else {
//       setRecordingTime(0);
//     }
    
//     return () => clearInterval(interval);
//   }, [recording, stopRecording]); // Added stopRecording as dependency


//   // Add this new state variable in your useState declarations
// const [promptSentence, setPromptSentence] = useState("");

// // Add this function to fetch a sentence
// const fetchSentence = async () => {
//   try {
//     const response = await fetch("http://localhost:5000/get-sentence");
//     const data = await response.json();
//     setPromptSentence(data.sentence);
//   } catch (error) {
//     console.error("Error fetching sentence:", error);
//     setPromptSentence("The quick brown fox jumps over the lazy dog.");
//   }
// };

// // Call fetchSentence in useEffect to get a sentence when the component mounts
// useEffect(() => {
//   fetchSentence();
// }, []);

// // Add this function to refresh the sentence
// const refreshSentence = () => {
//   fetchSentence();
// };
  
  // Audio visualizer effect
  useEffect(() => {
    if (recording) {
      const interval = setInterval(() => {
        setVisualizerData(Array.from({ length: 20 }, () => Math.random() * 100));
      }, 100);
      return () => clearInterval(interval);
    }
  }, [recording]);
  

  const startRecording = async (verification = false) => {
    try {
      // Prompt message changes based on whether it's enrollment or verification
      const promptMessage = verification
        ? "Verification in progress! Please speak again to verify your identity."
        : "Recording in progress for enrollment. Please speak into the microphone.";
  
      setRecordingFeedback(promptMessage); // Update feedback based on the action
  
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const audioChunks = [];
      
      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        setAudioBlob(audioBlob);
        setAudioURL(URL.createObjectURL(audioBlob));
        setRecordingFeedback(verification 
          ? "Verification recording completed! You can now submit." 
          : "Enrollment recording completed! You can now submit.");
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);  // Start the recording
      setMessage("");
      
      // Automatically stop recording after 30 seconds (you can adjust this as needed)
      setTimeout(() => {
        if (recorder.state === "recording") {
          recorder.stop(); // Stop recording after time
          setRecording(false);
        }
      }, 30000); // Timeout after 30 seconds
    } catch (error) {
      setMessage("Error accessing microphone. Please ensure you've given permission.");
    }
  };
  
  
  
//   const handleSubmit = async (endpoint) => {
//     if (!userId.trim()) {
//       setMessage("Please enter a user ID.");
//       return;
//     }
  
//     if (!audioBlob) {
//       setMessage("Please record an audio clip first.");
//       return;
//     }
  
//     setLoading(true);
//     const formData = new FormData();
//     formData.append("user_id", userId);
//     formData.append("audio", audioBlob, "audio.wav");
//     formData.append("sentence", promptSentence);  // Use sentence for verification
    
//     try {
//       const response = await fetch(`http://localhost:5000/${endpoint}`, {
//         method: "POST",
//         body: formData,
//       });
  
//       const result = await response.json();
      
//       if (response.ok) {
//         setMessage(
//           endpoint === "enroll" 
//             ? "✅ Voice profile successfully enrolled!" 
//             : `✅ ${result.message || "Voice successfully verified!"}`
//         );
//         fetchSentence(); // Get a new sentence after successful submission
//       } else {
//         setMessage(`❌ ${result.error || "An error occurred during processing."}`);
//       }
//     } catch (error) {
//       setMessage("❌ Error connecting to the server. Please try again.");
//     } finally {
//       setLoading(false);
//     }
//   };
  
//   const saveEnrollmentAudio = async (audioBlob) => {
//     // You need to handle saving the audio to the backend or storage
//     // For example, send it to the server to store the user's enrollment audio
//     const formData = new FormData();
//     formData.append("audio", audioBlob, "enrollmentAudio.wav");
//     try {
//       const response = await fetch("http://localhost:5000/save-enrollment", {
//         method: "POST",
//         body: formData,
//       });
//       const data = await response.json();
//       if (response.ok) {
//         console.log("Enrollment audio saved successfully");
//       } else {
//         console.error("Error saving enrollment audio:", data);
//       }
//     } catch (error) {
//       console.error("Error saving enrollment audio:", error);
//     }
//   };
  
  
//   const handleVerification = async () => {
//     if (audioBlob && !isEnrolled) {
//       // Save this audio as the enrolled voice
//       saveEnrollmentAudio(audioBlob);
//       setIsEnrolled(true);  // Set the enrollment state
//       setMessage("Voice successfully enrolled!");
//       return;
//     }
  
//     if (audioBlob && isEnrolled) {
//       // Proceed with verification logic if user is already enrolled
//       const isVerified = await verifyIdentity(audioBlob);
//       if (isVerified) {
//         setMessage("Verification successful.");
//       } else {
//         setMessage("Verification failed. Please try again.");
//       }
//     }
  
//    // If no audio exists yet, prompt user to record their voice
//   if (!audioBlob) {
//     setRecording(true);
//     setMessage("Recording in progress...");
//   }
// };

// const verifyIdentity = async (audioBlob) => {
//   const formData = new FormData();
//   formData.append("user_id", userId);
//   formData.append("audio", audioBlob, "audio.wav");
  
//   try {
//     const response = await fetch("http://localhost:5000/verify", {
//       method: "POST",
//       body: formData,
//     });

//     const result = await response.json();
//     if (response.ok) {
//       return true;
//     } else {
//       setMessage(result.error);
//       return false;
//     }
//   } catch (error) {
//     console.error("Error verifying identity:", error);
//     setMessage("❌ Error connecting to the server.");
//     return false;
//   }
// };
  
  
//   const resetRecording = () => {
//     setAudioBlob(null);
//     setAudioURL("");
//     setRecordingFeedback("");
//   };
  
//   const styles = {
//     container: {
//       minHeight: "100vh",
//       background: "linear-gradient(135deg, #312e81 0%, #5b21b6 100%)",
//       display: "flex",
//       alignItems: "center",
//       justifyContent: "center",
//       padding: "16px",
//       fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
//     },
//     card: {
//       backgroundColor: styleConstants.colors.cardBg,
//       borderRadius: styleConstants.radius.xl,
//       boxShadow: styleConstants.shadows.large,
//       width: "100%",
//       maxWidth: "500px",
//       overflow: "hidden"
//     },
//     header: {
//       background: `linear-gradient(90deg, ${styleConstants.colors.primary} 0%, #818cf8 100%)`,
//       padding: "24px",
//       color: styleConstants.colors.lightText
//     },
//     headerTitle: {
//       fontSize: "28px",
//       fontWeight: "bold",
//       textAlign: "center",
//       margin: "0 0 8px 0"
//     },
//     headerSubtitle: {
//       textAlign: "center",
//       fontSize: "16px",
//       fontWeight: "normal",
//       margin: 0,
//       opacity: 0.9
//     },
//     body: {
//       padding: "24px"
//     },
//     formGroup: {
//       marginBottom: "24px"
//     },
//     label: {
//       display: "block",
//       fontSize: "14px",
//       fontWeight: "500",
//       color: styleConstants.colors.darkText,
//       marginBottom: "4px"
//     },
//     input: {
//       width: "100%",
//       padding: "12px",
//       border: `1px solid ${styleConstants.colors.border}`,
//       borderRadius: styleConstants.radius.medium,
//       fontSize: "16px",
//       transition: "all 0.2s ease",
//       outline: "none",
//       boxSizing: "border-box"
//     },
//     flexRow: {
//       display: "flex",
//       justifyContent: "space-between",
//       alignItems: "center",
//       marginBottom: "8px"
//     },
//     countdownText: {
//       fontSize: "14px",
//       fontWeight: "500",
//       color: styleConstants.colors.danger
//     },
//     visualizer: {
//       height: "64px",
//       backgroundColor: styleConstants.colors.lightGray,
//       borderRadius: styleConstants.radius.medium,
//       marginBottom: "16px",
//       display: "flex",
//       alignItems: "flex-end",
//       justifyContent: "center",
//       padding: "0 8px"
//     },
//     visualizerBar: {
//       width: "4px",
//       backgroundColor: styleConstants.colors.primary,
//       borderTopLeftRadius: "2px",
//       borderTopRightRadius: "2px",
//       marginLeft: "2px",
//       marginRight: "2px",
//       minHeight: "4px"
//     },
//     audioPlayer: {
//       marginBottom: "16px",
//       padding: "12px",
//       backgroundColor: styleConstants.colors.lightGray,
//       borderRadius: styleConstants.radius.medium,
//       border: `1px solid ${styleConstants.colors.border}`
//     },
//     feedbackText: {
//       fontSize: "14px",
//       marginBottom: "12px",
//       fontWeight: "500",
//       textAlign: "center",
//       color: styleConstants.colors.primary
//     },
//     buttonRow: {
//       display: "flex",
//       gap: "12px"
//     },
//     button: {
//       flex: 1,
//       padding: "12px",
//       borderRadius: styleConstants.radius.medium,
//       border: "none",
//       fontSize: "16px",
//       fontWeight: "500",
//       cursor: "pointer",
//       transition: "all 0.2s ease",
//       display: "flex",
//       alignItems: "center",
//       justifyContent: "center"
//     },
//     primaryButton: {
//       backgroundColor: styleConstants.colors.primary,
//       color: styleConstants.colors.lightText
//     },
//     dangerButton: {
//       backgroundColor: styleConstants.colors.danger,
//       color: styleConstants.colors.lightText
//     },
//     resetButton: {
//       padding: "12px",
//       backgroundColor: styleConstants.colors.lightGray,
//       color: styleConstants.colors.secondary,
//       borderRadius: styleConstants.radius.medium,
//       border: "none",
//       fontSize: "14px",
//       fontWeight: "500",
//       cursor: "pointer",
//       transition: "all 0.2s ease"
//     },
//     enrollButton: {
//       backgroundColor: styleConstants.colors.success,
//       color: styleConstants.colors.lightText
//     },
//     verifyButton: {
//       backgroundColor: styleConstants.colors.verify,
//       color: styleConstants.colors.lightText
//     },
//     disabledButton: {
//       opacity: 0.5,
//       cursor: "not-allowed"
//     },
//     loadingContainer: {
//       display: "flex",
//       alignItems: "center",
//       justifyContent: "center",
//       gap: "8px",
//       color: styleConstants.colors.primary,
//       padding: "8px"
//     },
//     spinner: {
//       width: "16px",
//       height: "16px",
//       borderRadius: "50%",
//       border: `2px solid ${styleConstants.colors.primary}`,
//       borderTopColor: "transparent",
//       animation: "spin 1s linear infinite"
//     },
//     messageContainer: {
//       padding: "12px",
//       borderRadius: styleConstants.radius.medium,
//       textAlign: "center",
//       fontWeight: "500"
//     },
//     successMessage: {
//       backgroundColor: "#ecfdf5",
//       color: "#065f46"
//     },
//     errorMessage: {
//       backgroundColor: "#fef2f2",
//       color: "#991b1b"
//     },
//     footer: {
//       backgroundColor: styleConstants.colors.lightGray,
//       padding: "16px",
//       borderTop: `1px solid ${styleConstants.colors.border}`,
//       textAlign: "center",
//       fontSize: "12px",
//       color: styleConstants.colors.secondary
//     },
//     "@keyframes spin": {
//       "0%": { transform: "rotate(0deg)" },
//       "100%": { transform: "rotate(360deg)" }
//     },
//     pulseAnimation: {
//       animation: "pulse 1.5s infinite"
//     },
//     "@keyframes pulse": {
//       "0%, 100%": { opacity: 1 },
//       "50%": { opacity: 0.5 }
//     }
//   };
  
//   return (
//     <div style={styles.container}>
//       <div style={styles.card}>
//         {/* Header */}
//         <div style={styles.header}>
//           <h1 style={styles.headerTitle}>Voice Authentication</h1>
//           <p style={styles.headerSubtitle}>Secure access with your unique voice</p>
//         </div>
        
//         <div style={styles.body}>
//           {/* User ID Input */}
//           <div style={styles.formGroup}>
//             <label htmlFor="userId" style={styles.label}>User ID</label>
//             <input
//               id="userId"
//               type="text"
//               placeholder="Enter your unique identifier"
//               value={userId}
//               onChange={(e) => setUserId(e.target.value)}
//               style={styles.input}
//             />
    
//           </div>

//           {/* Sentence Display */}
// <div style={styles.formGroup}>
//   <div style={styles.flexRow}>
//     <span style={styles.label}>Please read aloud:</span>
//     <button 
//       onClick={refreshSentence}
//       style={{
//         ...styles.resetButton,
//         padding: "4px 8px",
//         fontSize: "12px"
//       }}
//     >
//       New Sentence
//     </button>
//   </div>
//   <div style={{
//     padding: "16px",
//     backgroundColor: styleConstants.colors.lightGray,
//     borderRadius: styleConstants.radius.medium,
//     border: `1px solid ${styleConstants.colors.border}`,
//     fontSize: "18px",
//     fontWeight: "500",
//     textAlign: "center",
//     marginBottom: "16px",
//     color: styleConstants.colors.primary
//   }}>
//     "{promptSentence}"
//   </div>
// </div>

          
//           {/* Recording Section */}
//           <div style={styles.formGroup}>
//             <div style={styles.flexRow}>
//               <span style={styles.label}>Voice Sample</span>
//               {recording && (
//                 <span style={styles.countdownText}>
//                   Recording: {30 - recordingTime}s left
//                 </span>
//               )}
//             </div>
            
//             {/* Visualizer - only shows when recording */}
//             {recording && (
//               <div style={styles.visualizer}>
//                 {visualizerData.map((height, i) => (
//                   <div 
//                     key={i} 
//                     style={{
//                       ...styles.visualizerBar,
//                       height: `${height}%`
//                     }}
//                   />
//                 ))}
//               </div>
//             )}
            
//             {/* Audio Player - only shows when audio is recorded */}
//             {audioURL && !recording && (
//               <div style={styles.audioPlayer}>
//                 <audio controls src={audioURL} style={{width: "100%", height: "40px"}}></audio>
//               </div>
//             )}
            
//             {/* Recording Feedback */}
//             {recordingFeedback && (
//               <div style={styles.feedbackText}>
//                 {recordingFeedback}
//               </div>
//             )}
            
//             {/* Recording Controls */}
//             <div style={styles.buttonRow}>
//               <button
//                 onClick={recording ? stopRecording : startRecording}
//                 style={{
//                   ...styles.button,
//                   ...(recording ? styles.dangerButton : styles.primaryButton),
//                 }}
//               >
//                 <span style={recording ? {animation: "pulse 1.5s infinite"} : {}}>
//                   {recording ? "Stop Recording" : "Record Voice"}
//                 </span>
//               </button>
              
//               {audioBlob && !recording && (
//                 <button
//                   onClick={resetRecording}
//                   style={styles.resetButton}
//                 >
//                   Reset
//                 </button>
//               )}
//             </div>
//           </div>
          
//           {/* Authentication Actions */}
//           <div style={{...styles.buttonRow, marginBottom: "16px"}}>
//             <button
//               onClick={() => handleSubmit("enroll")}
//               disabled={loading || !audioBlob}
//               style={{
//                 ...styles.button,
//                 ...styles.enrollButton,
//                 ...(loading || !audioBlob ? styles.disabledButton : {})
//               }}
//             >
//               Enroll Voice
//             </button>
            
//             <button
//               onClick={() => handleVerification("verify")}
//               disabled={loading || !audioBlob}
//               style={{
//                 ...styles.button,
//                 ...styles.verifyButton,
//                 ...(loading || !audioBlob ? styles.disabledButton : {})
//               }}
//             >
//               Verify Identity
//             </button>
//           </div>
          
//           {/* Status Message */}
//           {loading && (
//             <div style={styles.loadingContainer}>
//               <div style={{
//                 ...styles.spinner,
//                 animation: "spin 1s linear infinite"
//               }}></div>
//               <span>Processing your voice...</span>
//             </div>
//           )}
          
//           {message && !loading && (
//             <div style={{
//               ...styles.messageContainer,
//               ...(message.startsWith("✅") ? styles.successMessage : styles.errorMessage)
//             }}>
//               {message}
//             </div>
//           )}
//         </div>
        
//         {/* Footer */}
//         <div style={styles.footer}>
//           Secure voice biometric authentication • Your voice data is processed locally
//         </div>
//       </div>

//       <style jsx global>{`
//         @keyframes spin {
//           0% { transform: rotate(0deg); }
//           100% { transform: rotate(360deg); }
//         }
//         @keyframes pulse {
//           0%, 100% { opacity: 1; }
//           50% { opacity: 0.5; }
//         }
//       `}</style>
//     </div>
//   );
// };

// export default App;


import React, { useState, useEffect, useRef } from "react";

const App = () => {
  const [userId, setUserId] = useState("");
  const [audioBlob, setAudioBlob] = useState(null);
  const [recording, setRecording] = useState(false);
  const [message, setMessage] = useState("");
  const [audioURL, setAudioURL] = useState("");
  const [promptSentence, setPromptSentence] = useState("");
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const [visualizerData, setVisualizerData] = useState([]);

  // Fetch a random sentence for verification
  useEffect(() => {
    fetchSentence();
  }, []);

  const fetchSentence = async () => {
    try {
      const response = await fetch("http://localhost:5000/get-sentence");
      const data = await response.json();
      setPromptSentence(data.sentence);
    } catch {
      setPromptSentence("The quick brown fox jumps over the lazy dog.");
    }
  };

  // Start recording audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        setAudioBlob(audioBlob);
        setAudioURL(URL.createObjectURL(audioBlob));
      };

      mediaRecorder.start();
      setRecording(true);
      setMessage("");

      // Audio visualization simulation
      const interval = setInterval(() => {
        setVisualizerData(Array.from({ length: 20 }, () => Math.random() * 100));
      }, 100);

      setTimeout(() => {
        mediaRecorder.stop();
        setRecording(false);
        clearInterval(interval);
      }, 5000);
    } catch (error) {
      setMessage("Error accessing microphone.");
    }
  };

  // Submit audio to Flask backend
  const handleSubmit = async (endpoint) => {
    if (!userId.trim()) {
      setMessage("Please enter a user ID.");
      return;
    }

    if (!audioBlob) {
      setMessage("Please record an audio clip first.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("audio", audioBlob, "audio.wav");

    try {
      const response = await fetch(`http://localhost:5000/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage(endpoint === "enroll" ? "✅ Voice enrolled!" : "✅ Voice verified!");
        fetchSentence();
      } else {
        setMessage(`❌ ${result.error || "Verification failed!"}`);
      }
    } catch {
      setMessage("❌ Error connecting to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.header}>Voice Authentication</h1>
        <p style={styles.subtitle}>Secure access with your voice</p>

        {/* User ID Input */}
        <div style={styles.formGroup}>
          <label>User ID:</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            style={styles.input}
            placeholder="Enter your unique ID"
          />
        </div>

        {/* Display Random Sentence for Verification */}
        <div style={styles.sentenceBox}>
          <p><strong>Please read aloud:</strong></p>
          <p style={styles.sentence}>"{promptSentence}"</p>
          <button onClick={fetchSentence} style={styles.refreshButton}>New Sentence</button>
        </div>

        {/* Recording Controls */}
        <div style={styles.recordSection}>
          <button onClick={startRecording} disabled={recording} style={styles.recordButton}>
            {recording ? "Recording..." : "Record Voice"}
          </button>

          {audioURL && (
            <div style={styles.audioPlayer}>
              <audio controls src={audioURL}></audio>
            </div>
          )}
        </div>

        {/* Visualizer (Simulated) */}
        {recording && (
          <div style={styles.visualizer}>
            {visualizerData.map((height, i) => (
              <div key={i} style={{ ...styles.visualizerBar, height: `${height}%` }}></div>
            ))}
          </div>
        )}

        {/* Submit Buttons */}
        <div style={styles.buttonRow}>
          <button onClick={() => handleSubmit("enroll")} disabled={loading || !audioBlob} style={styles.enrollButton}>
            Enroll
          </button>
          <button onClick={() => handleSubmit("verify")} disabled={loading || !audioBlob} style={styles.verifyButton}>
            Verify
          </button>
        </div>

        {/* Message Display */}
        {loading && <p style={styles.loadingText}>Processing...</p>}
        {message && <p style={styles.message}>{message}</p>}
      </div>
    </div>
  );
};

// Styling
const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f3f4f6",
  },
  card: {
    background: "#fff",
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
    width: "400px",
    textAlign: "center",
  },
  header: {
    fontSize: "24px",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "14px",
    color: "#6b7280",
    marginBottom: "20px",
  },
  formGroup: {
    marginBottom: "15px",
  },
  input: {
    width: "100%",
    padding: "10px",
    fontSize: "16px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  sentenceBox: {
    background: "#eef2ff",
    padding: "10px",
    borderRadius: "5px",
    marginBottom: "15px",
  },
  sentence: {
    fontSize: "16px",
    fontWeight: "bold",
  },
  refreshButton: {
    background: "#4f46e5",
    color: "#fff",
    padding: "5px 10px",
    border: "none",
    cursor: "pointer",
    borderRadius: "5px",
  },
  recordSection: {
    marginBottom: "15px",
  },
  recordButton: {
    background: "#10b981",
    color: "#fff",
    padding: "10px 15px",
    border: "none",
    cursor: "pointer",
    borderRadius: "5px",
  },
  audioPlayer: {
    marginTop: "10px",
  },
  buttonRow: {
    display: "flex",
    justifyContent: "space-between",
  },
  enrollButton: {
    background: "#2563eb",
    color: "#fff",
    padding: "10px 15px",
    border: "none",
    cursor: "pointer",
    borderRadius: "5px",
  },
  verifyButton: {
    background: "#ef4444",
    color: "#fff",
    padding: "10px 15px",
    border: "none",
    cursor: "pointer",
    borderRadius: "5px",
  },
  message: {
    marginTop: "10px",
    fontWeight: "bold",
  },
};

export default App;
