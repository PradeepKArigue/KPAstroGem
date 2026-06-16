import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: "#07111f",
        aurora: "#0f5d7a",
        saffron: "#f2b84b",
        mist: "#e8edf5",
        roseclay: "#9d5c63",
      },
      boxShadow: {
        halo: "0 20px 60px rgba(7, 17, 31, 0.22)",
      },
      backgroundImage: {
        "orbital-grid":
          "radial-gradient(circle at top left, rgba(242, 184, 75, 0.2), transparent 28%), radial-gradient(circle at bottom right, rgba(15, 93, 122, 0.3), transparent 30%)",
      },
    },
  },
  plugins: [],
};

export default config;

