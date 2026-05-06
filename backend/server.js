/**
 * Node.js Express Server
 * Serves the frontend and proxies API requests to the Python backend.
 */

const express = require("express");
const path = require("path");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_API = process.env.PYTHON_API || "http://127.0.0.1:5000";

// Serve static frontend files
app.use(express.static(path.join(__dirname, "..", "frontend")));

// Parse JSON bodies
app.use(express.json());

// Proxy API requests to Python backend
app.use(
  "/api",
  createProxyMiddleware({
    target: PYTHON_API,
    changeOrigin: true,
    pathRewrite: { "^/api": "" },
    onError: (err, req, res) => {
      console.error("Proxy error:", err.message);
      res.status(503).json({
        error:
          "Python backend is not running. Start it with: cd backend && python api.py",
      });
    },
  })
);

// Fallback — serve index.html
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

app.listen(PORT, () => {
  console.log(`\n========================================`);
  console.log(`  College Chatbot Server`);
  console.log(`  Frontend:  http://localhost:${PORT}`);
  console.log(`  Python API: ${PYTHON_API}`);
  console.log(`========================================\n`);
});
