'use client';

import { useEffect, useRef, useState } from 'react';

interface JellyfishCanvasProps {
  color?: string;
  traits?: string[];
  founderGlow?: boolean;
  interactive?: boolean;
  className?: string;
}

const COLORS = {
  pink: { hue: 330, saturation: 85, lightness: 70 },
  purple: { hue: 270, saturation: 70, lightness: 65 },
  cyan: { hue: 180, saturation: 80, lightness: 60 },
  amber: { hue: 40, saturation: 90, lightness: 65 },
  coral: { hue: 15, saturation: 85, lightness: 65 },
  blue: { hue: 200, saturation: 75, lightness: 65 },
  rose: { hue: 340, saturation: 70, lightness: 75 },
  violet: { hue: 280, saturation: 65, lightness: 70 },
  sky: { hue: 195, saturation: 75, lightness: 65 },
};

export function JellyfishCanvas({ 
  color = 'pink', 
  traits = [], 
  founderGlow = false, 
  interactive = true,
  className 
}: JellyfishCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = canvas.clientWidth;
      canvas.height = canvas.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    let animationFrame: number;
    let time = 0;

    const colorData = COLORS[color as keyof typeof COLORS] || COLORS.pink;
    const hasGlow = founderGlow;
    const traitInfluence = calculateTraitInfluence(traits);

    const tentacles = Array.from({ length: 12 }, () => ({
      phase: Math.random() * Math.PI * 2,
      length: 60 + Math.random() * 40,
      offset: Math.random() * 0.5 + 0.5,
    }));

    const animate = (timestamp: number) => {
      time += 0.016;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const x = canvas.width / 2;
      const y = canvas.height / 2;
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(1 + Math.sin(time * 0.5) * 0.02, 1 + Math.cos(time * 0.3) * 0.01);

      drawGlow(ctx, colorData, hasGlow, time);
      drawBell(ctx, colorData, time, traitInfluence);
      drawTentacles(ctx, colorData, time, tentacles, traitInfluence);
      drawCore(ctx, colorData, time, traitInfluence);

      ctx.restore();
      animationFrame = requestAnimationFrame(animate);
    };

    animationFrame = requestAnimationFrame(animate);
    setReady(true);

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener('resize', resize);
    };
  }, [color, traits, founderGlow]);

  const calculateTraitInfluence = (t: string[]) => ({
    speed: t.includes('energetic') || t.includes('enthusiastic') ? 1.5 : 
           t.includes('gentle') || t.includes('calm') ? 0.7 : 1,
    amplitude: t.includes('playful') || t.includes('mischievous') ? 1.3 : 1,
  });

  return (
    <canvas
      ref={canvasRef}
      className={`w-full h-full block transition-all duration-300 ${className || ''}`}
      style={{ display: ready ? 'block' : 'none' }}
    />
  );
}

function drawGlow(ctx: CanvasRenderingContext2D, color: { hue: number; saturation: number; lightness: number }, hasGlow: boolean, time: number) {
  if (hasGlow) {
    const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 120);
    const glowHue = 50;
    gradient.addColorStop(0, `hsla(${glowHue}, 100%, 60%, 0.35)`);
    gradient.addColorStop(0.5, `hsla(${glowHue}, 100%, 70%, 0.15)`);
    gradient.addColorStop(1, 'hsla(0, 0%, 0%, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(0, 0, 100, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = `hsla(${glowHue}, 100%, 60%, 0.3)`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, 85 + Math.sin(time * 2) * 5, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function drawBell(ctx: CanvasRenderingContext2D, color: { hue: number; saturation: number; lightness: number }, time: number, influence: { speed: number; amplitude: number }) {
  const bellHeight = 50;
  const bellWidth = 60;
  const bellContract = Math.sin(time * 2) * 8 * influence.amplitude;

  ctx.fillStyle = `hsl(${color.hue}, ${color.saturation}%, ${color.lightness}%)`;
  ctx.beginPath();
  ctx.moveTo(-bellWidth / 2, 0);
  ctx.bezierCurveTo(
    -bellWidth / 2, -bellHeight + bellContract,
    bellWidth / 2, -bellHeight + bellContract,
    bellWidth / 2, 0
  );
  ctx.bezierCurveTo(
    bellWidth / 2, -bellHeight / 2 + bellContract / 2,
    -bellWidth / 2, -bellHeight / 2 + bellContract / 2,
    -bellWidth / 2, 0
  );
  ctx.fill();

  ctx.fillStyle = `hsla(${color.hue}, ${color.saturation}%, ${Math.min(90, color.lightness + 20)}%, 0.3)`;
  ctx.beginPath();
  ctx.moveTo(-bellWidth / 3, 0);
  ctx.bezierCurveTo(
    -bellWidth / 3, -bellHeight / 2 + bellContract / 2,
    bellWidth / 3, -bellHeight / 2 + bellContract / 2,
    bellWidth / 3, 0
  );
  ctx.fill();
}

function drawTentacles(ctx: CanvasRenderingContext2D, color: { hue: number; saturation: number; lightness: number }, time: number, tentacles: { phase: number; length: number; offset: number }[], influence: { speed: number; amplitude: number }) {
  ctx.strokeStyle = `hsla(${color.hue}, ${color.saturation}%, ${Math.max(20, color.lightness - 15)}%, 0.85)`;
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';

  for (let i = 0; i < tentacles.length; i++) {
    const t = tentacles[i];
    const angle = (i / tentacles.length) * Math.PI - Math.PI / 2;
    const xStart = Math.cos(angle) * 30;
    const yStart = 0;

    ctx.beginPath();
    ctx.moveTo(xStart, yStart);

    for (let s = 0; s <= 10; s++) {
      const wave = Math.sin(time * 1.5 * influence.speed + t.phase + s * Math.PI * 2) * 15 * t.offset * influence.amplitude;
      const x = xStart + wave + Math.sin(s * Math.PI) * 5;
      const y = yStart + (s / 10) * t.length;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

function drawCore(ctx: CanvasRenderingContext2D, color: { hue: number; saturation: number; lightness: number }, time: number, influence: { speed: number; amplitude: number }) {
  ctx.fillStyle = `hsl(${color.hue}, ${color.saturation}%, ${color.lightness}%)`;
  ctx.beginPath();
  ctx.arc(0, -40, 8, 0, Math.PI * 2);
  ctx.fill();

  for (let i = 0; i < 3; i++) {
    ctx.fillStyle = `hsla(${color.hue}, 100%, 85%, ${0.3 + Math.sin(time * 3 + i) * 0.2})`;
    ctx.beginPath();
    ctx.arc(
      Math.cos(time * (i + 1) * 0.5) * 20,
      -40 - Math.sin(time * 0.5 + i) * 5,
      3 + Math.random() * 2,
      0,
      Math.PI * 2
    );
    ctx.fill();
  }
}