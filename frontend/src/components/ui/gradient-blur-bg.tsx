import { cn } from "@/lib/utils";
import React from "react";

export const GradientBlurBg: React.FC<{
  children?: React.ReactNode;
  className?: string;
}> = ({ children, className }) => {
  return (
    <div className={cn("min-h-screen w-full bg-white relative", className)}>
      {/* Purple Gradient Grid Right Background */}
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(to right, #f0f0f0 1px, transparent 1px),
            linear-gradient(to bottom, #f0f0f0 1px, transparent 1px),
            radial-gradient(circle 800px at 100% 200px, #d5c5ff, transparent)
          `,
          backgroundSize: "96px 64px, 96px 64px, 100% 100%",
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};

export const Component = GradientBlurBg;
export default GradientBlurBg;
