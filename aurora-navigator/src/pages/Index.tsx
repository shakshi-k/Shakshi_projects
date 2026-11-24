import { useEffect } from "react";

// The full navigation app lives as standalone HTML/CSS/JS in /public/navigator/.
// We embed it via an iframe so it works in the Lovable preview AND can be
// deployed as-is from the /navigator/ folder to GitHub Pages, Netlify, or Vercel.
const Index = () => {
  useEffect(() => {
    document.title = "Aurora Navigator — Premium Route Planner";
  }, []);

  return (
    <iframe
      src="./navigator/index.html"
      title="Aurora Navigator"
      style={{
        position: "fixed",
        inset: 0,
        width: "100%",
        height: "100%",
        border: "none",
      }}
    />
  );
};

export default Index;
