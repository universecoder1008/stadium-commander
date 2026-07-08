import React, { useEffect, useState, useRef } from "react";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  formatter?: (val: number) => string;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  duration = 600,
  formatter = (val) => String(Math.round(val))
}) => {
  const [displayValue, setDisplayValue] = useState(value);
  const prevValueRef = useRef(value);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // Monitor OS prefers-reduced-motion triggers
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);
    const listener = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener("change", listener);
    return () => mediaQuery.removeEventListener("change", listener);
  }, []);

  useEffect(() => {
    if (prefersReducedMotion) {
      setDisplayValue(value);
      prevValueRef.current = value;
      return;
    }

    const startValue = prevValueRef.current;
    const endValue = value;
    if (startValue === endValue) return;

    let startTime: number | null = null;
    let frameId: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      // Ease-out Quad: f(t) = t * (2 - t)
      const easedProgress = progress * (2 - progress);
      const currentVal = startValue + (endValue - startValue) * easedProgress;
      
      setDisplayValue(currentVal);

      if (progress < 1) {
        frameId = requestAnimationFrame(animate);
      } else {
        prevValueRef.current = endValue;
      }
    };

    frameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frameId);
    };
  }, [value, duration, prefersReducedMotion]);

  return <>{formatter(displayValue)}</>;
};

export default AnimatedCounter;
