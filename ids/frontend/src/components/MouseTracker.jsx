import React, { useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import io from 'socket.io-client';

const MouseTracker = () => {
  const { user, getToken } = useAuth();
  const socketRef = useRef(null);
  const eventsBuffer = useRef([]);
  const movementIdRef = useRef(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    if (!user) return;

    // Connect to Socket.IO server
    socketRef.current = io('http://localhost:3001', {
      auth: {
        token: getToken()
      }
    });

    // Handle connection events
    socketRef.current.on('connect', () => {
      console.log('Mouse tracker connected to server');
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('Mouse tracker connection failed:', error.message);
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('Mouse tracker disconnected:', reason);
    });

    // Set up mouse event listeners
    const handleMouseEvent = (eventType, event) => {
      const mouseEvent = {
        eventType,
        x: event.clientX,
        y: event.clientY,
        timestamp: new Date().toISOString(),
        epoch: Date.now(),
        movementId: movementIdRef.current
      };

      eventsBuffer.current.push(mouseEvent);

      // Debug: Log every 10th event to avoid spam
      if (eventsBuffer.current.length % 10 === 0) {
        console.log(`Mouse events buffered: ${eventsBuffer.current.length}`);
      }
    };

    // Add event listeners
    document.addEventListener('mousemove', (e) => handleMouseEvent('movement', e));
    document.addEventListener('mousedown', (e) => {
      if (e.button === 0) handleMouseEvent('left_press', e);
      else if (e.button === 2) handleMouseEvent('right_press', e);
    });
    document.addEventListener('mouseup', (e) => {
      if (e.button === 0) handleMouseEvent('left_release', e);
      else if (e.button === 2) handleMouseEvent('right_release', e);
    });
    document.addEventListener('wheel', (e) => {
      handleMouseEvent(e.deltaY > 0 ? 'scroll_down' : 'scroll_up', e);
    });

    // Send batched events every 2 seconds
    const interval = setInterval(() => {
      if (eventsBuffer.current.length > 0 && socketRef.current) {
        console.log(`Sending ${eventsBuffer.current.length} mouse events to server`);
        socketRef.current.emit('mouse-events', [...eventsBuffer.current]);
        eventsBuffer.current = []; // Clear buffer
      }
    }, 2000);

    // Cleanup
    return () => {
      clearInterval(interval);
      document.removeEventListener('mousemove', handleMouseEvent);
      document.removeEventListener('mousedown', handleMouseEvent);
      document.removeEventListener('mouseup', handleMouseEvent);
      document.removeEventListener('wheel', handleMouseEvent);

      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [user, getToken]);

  // This component doesn't render anything
  return null;
};

export default MouseTracker;