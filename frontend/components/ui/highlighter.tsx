"use client";

import { useEffect, useRef } from "react";
import { useInView } from "motion/react";
import { annotate } from "rough-notation";
import type React from "react";
import { type RoughAnnotation } from "rough-notation/lib/model";

type AnnotationAction =
  | "highlight"
  | "underline"
  | "box"
  | "circle"
  | "strike-through"
  | "crossed-off"
  | "bracket";

interface HighlighterProps {
  children: React.ReactNode;
  action?: AnnotationAction;
  color?: string;
  strokeWidth?: number;
  animationDuration?: number;
  iterations?: number;
  padding?: number;
  multiline?: boolean;
  isView?: boolean;
  opacity?: number; // 0..1
}

export function Highlighter({
  children,
  action = "highlight",
  color = "#ffd1dc",
  strokeWidth = 1.5,
  animationDuration = 600,
  iterations = 2,
  padding = 2,
  multiline = true,
  isView = false,
  opacity = 1, // new
}: HighlighterProps) {
  const elementRef = useRef<HTMLSpanElement>(null);
  const annotationRef = useRef<RoughAnnotation | null>(null);

  const isInView = useInView(elementRef, {
    once: true,
    margin: "-10%",
  });

  // If isView is false, always show. If isView is true, wait for inView
  const shouldShow = !isView || isInView;

  useEffect(() => {
    if (!shouldShow) return;

    const element = elementRef.current;
    if (!element) return;

    const toColorWithOpacity = (c: string, a: number) => {
      const alpha = Math.max(0, Math.min(1, a));
      // Hex (#rgb or #rrggbb) -> rgba(...)
      if (c.startsWith("#")) {
        let hex = c.slice(1);
        if (hex.length === 3) hex = hex.split("").map((ch) => ch + ch).join("");
        const num = parseInt(hex, 16);
        const r = (num >> 16) & 255;
        const g = (num >> 8) & 255;
        const b = num & 255;
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
      }
      // rgb(...) -> rgba(...)
      if (c.startsWith("rgb(")) {
        const inside = c.slice(4, -1);
        return `rgba(${inside}, ${alpha})`;
      }
      // Fallback for CSS variables or other color functions
      // Blend with transparent to emulate alpha
      const pct = Math.round(alpha * 100);
      return `color-mix(in oklch, ${c} ${pct}%, transparent)`;
    };

    const effectiveColor = toColorWithOpacity(color, opacity);

    const annotationConfig = {
      type: action,
      color: effectiveColor,
      strokeWidth,
      animationDuration,
      iterations,
      padding,
      multiline,
    };

    const annotation = annotate(element, annotationConfig);

    annotationRef.current = annotation;
    annotationRef.current.show();

    const resizeObserver = new ResizeObserver(() => {
      annotation.hide();
      annotation.show();
    });

    resizeObserver.observe(element);
    resizeObserver.observe(document.body);

    return () => {
      if (element) {
        annotate(element, { type: action }).remove();
        resizeObserver.disconnect();
      }
    };
  }, [
    shouldShow,
    action,
    color,
    opacity, // add dependency
    strokeWidth,
    animationDuration,
    iterations,
    padding,
    multiline,
  ]);

  return (
    <span ref={elementRef} className="relative inline-block bg-transparent">
      {children}
    </span>
  );
}
