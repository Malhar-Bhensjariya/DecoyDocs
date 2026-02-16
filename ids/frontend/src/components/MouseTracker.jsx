
import { useEffect, useRef, useState } from "react";
import axios from "axios";

const MouseTracker = ({ onPredictionUpdate }) => {
  const coordsBuffer = useRef([]);
  const [botCount, setBotCount] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e) => {
      coordsBuffer.current.push([e.clientX, e.clientY]);
    };

    document.addEventListener("mousemove", handleMouseMove);

    const interval = setInterval(async () => {
      if (coordsBuffer.current.length < 10) return;

      try {
        const response = await axios.post("http://localhost:5000/predict", {
          coords: coordsBuffer.current,
        });

        const data = response.data;
        console.log("Prediction:", data);

        // Update bot count
        const isBot = data.result === "Bot";
        const newBotCount = isBot ? botCount + 1 : 0;
        setBotCount(newBotCount);

        // Prepare prediction data for parent component
        const predictionData = {
          ...data,
          botCount: newBotCount,
          timestamp: new Date().toLocaleTimeString(),
          shouldAlert: newBotCount > 3,
        };

        // Send to parent component
        if (onPredictionUpdate) {
          onPredictionUpdate(predictionData);
        }
      } catch (error) {
        console.error("Error sending mouse data:", error);
      }

      coordsBuffer.current = [];
    }, 2000);

    return () => {
      clearInterval(interval);
      document.removeEventListener("mousemove", handleMouseMove);
    };
  }, [botCount, onPredictionUpdate]);

  return null;
};

export default MouseTracker;