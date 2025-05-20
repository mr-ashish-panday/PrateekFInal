import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

function App() {
  const webcamRef = useRef(null);
  const [result, setResult] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Mapping English labels to Nepali script
  const labelMap = {
    'Dhanyabaad': 'धन्यवाद',
    'Ghar': 'घर',
    'Ma': 'म',
    'Namaskaar': 'नमस्कार'
  };

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      setError('Failed to capture image');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/predict', {
        image: imageSrc,
      });
      const nepaliSign = labelMap[response.data.sign] || response.data.sign;
      setResult(nepaliSign);
      setMessage(response.data.message || '');
      setError('');
    } catch (err) {
      setError('Error sending image to backend');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-4">Sign Language Recognition</h1>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
        className="mb-4 border-2 border-gray-300"
      />
      <button
        onClick={capture}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
      >
        Capture & Predict
      </button>
      {result && (
        <div className="text-xl">
          Predicted Sign: <span className="font-bold">{result}</span>
        </div>
      )}
      {message && (
        <div className="text-lg text-gray-600 mt-2">{message}</div>
      )}
      {error && <div className="text-red-500">{error}</div>}
    </div>
  );
}

export default App;