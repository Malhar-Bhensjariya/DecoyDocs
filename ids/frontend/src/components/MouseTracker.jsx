
import { useEffect, useRef, useState } from "react";
import axios from "axios";

const MouseTracker = () => {
  const coordsBuffer = useRef([]);
  const [alertMessage, setAlertMessage] = useState(null);

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

        if (data.result === "Bot") {
          setAlertMessage("🚨 Bot activity detected!");
        } else {
          setAlertMessage(null);
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
  }, []);

  return (
    <>
      {alertMessage && (
        <div
          className="fixed top-5 right-5 bg-red-600 text-white px-6 py-4 rounded-lg font-bold z-50 shadow-lg animate-bounce"
        >
          {alertMessage}
        </div>
      )}
    </>
  );
};

export default MouseTracker;