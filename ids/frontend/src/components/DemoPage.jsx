import React, { useState } from "react";
import MouseTracker from "./MouseTracker";

const DemoPage = () => {
  const [clicks, setClicks] = useState(0);
  const [hovering, setHovering] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [predictionHistory, setPredictionHistory] = useState([]);

  const handlePredictionUpdate = (data) => {
    setPrediction(data);

    // Add to history (keep last 10)
    setPredictionHistory((prev) => [data, ...prev.slice(0, 9)]);

    // Show alert if bot count exceeds 3
    if (data.shouldAlert) {
      setShowAlert(true);
      // Auto-hide alert after 4 seconds
      setTimeout(() => setShowAlert(false), 4000);
    }
  };

  const getResultColor = (result) => {
    return result === "Human"
      ? "from-green-500 to-emerald-500"
      : "from-red-500 to-red-600";
  };

  const getResultIcon = (result) => {
    return result === "Human" ? "✅" : "⚠️";
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-indigo-50 via-purple-50 to-pink-50 relative overflow-hidden">
      <MouseTracker onPredictionUpdate={handlePredictionUpdate} />

      {/* Critical Alert Overlay */}
      {showAlert && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-red-600 text-white px-8 py-6 rounded-2xl shadow-2xl animate-pulse max-w-md">
            <div className="flex items-center gap-4 mb-4">
              <div className="text-5xl">🚨</div>
              <div>
                <h2 className="text-3xl font-bold">Bot Detected!</h2>
                <p className="text-red-100">Suspicious activity flagged</p>
              </div>
            </div>
            <p className="text-red-100 text-lg">
              More than 3 bot detections recorded. Please verify your activity.
            </p>
          </div>
        </div>
      )}

      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        {/* Header Section */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-linear-to-br from-blue-500 to-purple-600 rounded-2xl mb-6 shadow-lg">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>

          <h1 className="text-6xl font-bold bg-linear-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Behavioral Intrusion Detection
          </h1>

          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Advanced AI-powered system that analyzes mouse movement patterns in
            real-time to detect and prevent automated bot activity
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {/* Card 1 */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-purple-100">
            <div className="w-14 h-14 bg-linear-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              Real-Time Analysis
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Continuous monitoring and instant detection of suspicious behavior patterns
            </p>
          </div>

          {/* Card 2 */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-purple-100">
            <div className="w-14 h-14 bg-linear-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              AI-Powered
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Machine learning algorithms trained to distinguish human from bot behavior
            </p>
          </div>

          {/* Card 3 */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-purple-100">
            <div className="w-14 h-14 bg-linear-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              Secure & Private
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Client-side processing ensures your data stays safe and protected
            </p>
          </div>
        </div>

        {/* Live Prediction Display */}
        {prediction && (
          <div className="mb-12 animate-fade-in">
            <div
              className={`bg-gradient-to-r ${getResultColor(
                prediction.result
              )} rounded-3xl p-8 shadow-2xl text-white border-2 border-white/20`}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="text-6xl">{getResultIcon(prediction.result)}</div>
                  <div>
                    <h2 className="text-4xl font-bold">{prediction.result}</h2>
                    <p className="text-white/80">Activity Status</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-white/70">Last Detection</p>
                  <p className="text-2xl font-bold">{prediction.timestamp}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/10 rounded-2xl p-4 backdrop-blur-sm">
                  <p className="text-white/70 text-sm mb-2">Human Probability</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold">
                      {(prediction.probability_human * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="mt-3 h-2 bg-white/20 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-white transition-all duration-300"
                      style={{
                        width: `${prediction.probability_human * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <div className="bg-white/10 rounded-2xl p-4 backdrop-blur-sm">
                  <p className="text-white/70 text-sm mb-2">Bot Detections</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold">
                      {prediction.botCount}
                    </span>
                    <span className="text-white/70">/3</span>
                  </div>
                  <div className="mt-3 h-2 bg-white/20 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        prediction.botCount > 3
                          ? "bg-red-400"
                          : "bg-white"
                      }`}
                      style={{
                        width: `${Math.min((prediction.botCount / 3) * 100, 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Prediction History */}
        {predictionHistory.length > 0 && (
          <div className="mb-12">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">
              Detection History
            </h3>
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-purple-100">
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {predictionHistory.map((pred, idx) => (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-4 rounded-xl transition-all ${
                      pred.result === "Human"
                        ? "bg-green-50 border border-green-200"
                        : "bg-red-50 border border-red-200"
                    }`}
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <span className="text-2xl">
                        {getResultIcon(pred.result)}
                      </span>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-800">
                          {pred.result === "Human" ? "Human Activity" : "Bot Activity"}
                        </p>
                        <p className="text-sm text-gray-600">{pred.timestamp}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        pred.result === "Human"
                          ? "text-green-600"
                          : "text-red-600"
                      }`}>
                        {(pred.probability_human * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Interactive Demo Section */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-purple-100 mb-12">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Try It Yourself
            </h2>
            <p className="text-lg text-gray-600">
              Move your mouse naturally around the page and interact with the button
            </p>
          </div>

          {/* Interactive Button */}
          <div className="flex flex-col items-center gap-6">
            <button
              onClick={() => setClicks(clicks + 1)}
              onMouseEnter={() => setHovering(true)}
              onMouseLeave={() => setHovering(false)}
              className="group relative px-12 py-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white text-2xl font-bold rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-3">
                <svg
                  className={`w-6 h-6 transition-transform duration-300 ${
                    hovering ? "rotate-12 scale-110" : ""
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
                Click Me!
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </button>

            {/* Click Counter */}
            {clicks > 0 && (
              <div className="animate-bounce-in">
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl px-8 py-4">
                  <p className="text-green-700 font-semibold text-lg">
                    🎉 Total Clicks: <span className="text-2xl font-bold">{clicks}</span>
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Instructions Section */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-10 border border-blue-200">
          <div className="flex items-start gap-6">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                How It Works
              </h3>
              <div className="space-y-3 text-gray-700 leading-relaxed">
                <p className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-white rounded-full flex items-center justify-center text-purple-600 font-bold shadow-sm">
                    1
                  </span>
                  <span>Move your mouse naturally across the page</span>
                </p>
                <p className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-white rounded-full flex items-center justify-center text-purple-600 font-bold shadow-sm">
                    2
                  </span>
                  <span>Our AI analyzes movement patterns in real-time</span>
                </p>
                <p className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-white rounded-full flex items-center justify-center text-purple-600 font-bold shadow-sm">
                    3
                  </span>
                  <span>Bot-like behavior triggers instant alerts</span>
                </p>
                <p className="flex items-center gap-3">
                  <span className="flex-shrink-0 w-8 h-8 bg-white rounded-full flex items-center justify-center text-purple-600 font-bold shadow-sm">
                    4
                  </span>
                  <span>Check the status dashboard for detailed metrics</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Animations */}
      <style jsx>{`
        @keyframes blob {
          0%, 100% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes bounce-in {
          0% {
            opacity: 0;
            transform: scale(0.3);
          }
          50% {
            transform: scale(1.05);
          }
          70% {
            transform: scale(0.9);
          }
          100% {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
        .animate-bounce-in {
          animation: bounce-in 0.6s ease-out;
        }
      `}</style>
    </div>
  );
};

export default DemoPage;