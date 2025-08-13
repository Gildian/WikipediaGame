/**
 * Wikipedia Path Finder - Home Component
 * 
 * Main interface for the Wikipedia pathfinding application with real-time
 * search capabilities, algorithm selection, and results visualization.
 * 
 * @author Gildian Gonzales
 * @license MIT
 */

import React, { useEffect, useMemo, useState, useCallback } from "react";
import axios from "axios";
import "./styles.scss";

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";
const FACTS_API_KEY = import.meta.env.VITE_FACTS_API_KEY || "qKYv6ffmUut4HXbt/CswWA==HIDFaMPKP5qaj5De";
const FACT_REFRESH_INTERVAL = 10000; // 10 seconds

function Home() {
  // Search state
  const [pathData, setPathData] = useState({
    path: "[]",
    timeTaken: 0,
    success: false
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [firstLoad, setFirstLoad] = useState(true);
  
  // Form state
  const [startTitle, setStartTitle] = useState("Python (programming language)");
  const [endTitle, setEndTitle] = useState("Machine learning");
  const [algoToggle, setAlgoToggle] = useState("best_first_search");
  
  // Fun facts state
  const [fact, setFact] = useState("");
  const [factChangerId, setFactChangerId] = useState(null);

  // Computed values
  const clicks = useMemo(() => {
    try {
      let pathArr = pathData.path.replaceAll("'", '"');
      pathArr = pathArr.replaceAll('"s', "'s");
      const parsed = JSON.parse(pathArr);
      return Math.max(0, parsed.length - 1);
    } catch {
      return 0;
    }
  }, [pathData.path]);

  const pathDisplay = useMemo(() => {
    try {
      let pathArr = pathData.path.replaceAll("'", '"');
      pathArr = pathArr.replaceAll('"s', "'s");
      const parsed = JSON.parse(pathArr);
      
      if (parsed.length === 0) return "";
      
      return parsed.join(" → ");
    } catch {
      return "Invalid path data";
    }
  }, [pathData.path]);

  const algoTitle = useMemo(() => {
    switch (algoToggle) {
      case "best_first_search":
        return "Best-First";
      case "depth_first_search":
        return "Depth-First";
      default:
        return "Unknown";
    }
  }, [algoToggle]);

  // Fetch random facts for entertainment during loading
  const fetchFactData = useCallback(async () => {
    try {
      const response = await axios.get("https://api.api-ninjas.com/v1/facts?limit=1", {
        headers: {
          "X-Api-Key": FACTS_API_KEY,
        },
        timeout: 5000
      });
      
      if (response.data && response.data[0]) {
        setFact(response.data[0].fact);
      } else {
        setFact("Did you know? The Wikipedia game was created to explore the connections between different topics!");
      }
    } catch (error) {
      console.warn("Failed to fetch fact:", error.message);
      const fallbackFacts = [
        "Wikipedia contains over 6 million articles in English!",
        "The average Wikipedia page is linked to by about 15 other pages.",
        "Did you know that this bot uses AI to find semantic connections?",
        "Machine learning helps this bot understand article relationships!",
        "The GloVe embeddings used here were trained on billions of words."
      ];
      setFact(fallbackFacts[Math.floor(Math.random() * fallbackFacts.length)]);
    }
  }, []);

  // Initialize facts on first load
  useEffect(() => {
    if (firstLoad) {
      fetchFactData();
      setLoading(false);
    }
  }, [firstLoad, fetchFactData]);

  // Manage fact refresh during loading
  useEffect(() => {
    if (loading && !firstLoad) {
      fetchFactData();
      const factChanger = setInterval(fetchFactData, FACT_REFRESH_INTERVAL);
      setFactChangerId(factChanger);
      
      return () => {
        if (factChanger) {
          clearInterval(factChanger);
        }
      };
    }
    
    return () => {
      if (factChangerId) {
        clearInterval(factChangerId);
        setFactChangerId(null);
      }
    };
  }, [loading, firstLoad, fetchFactData, factChangerId]);

  // Perform search request
  const fetchSearchData = useCallback(async (isRandom) => {
    setError(null);
    
    try {
      const requestData = {
        isRandom: isRandom,
        startArticle: startTitle.trim(),
        endArticle: endTitle.trim(),
        algo: algoToggle,
      };
      
      console.log("🔍 Starting search:", requestData);
      
      const response = await axios.post(`${API_BASE_URL}/`, requestData, {
        timeout: 180000, // 3 minutes
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const { results, start, end } = response.data;
      
      if (!results || results.length === 0) {
        throw new Error("No results returned from search");
      }
      
      // Handle multiple algorithm results
      let selectedResult;
      if (results.length > 1) {
        selectedResult = results.find(result => result.algo === algoToggle) || results[0];
      } else {
        selectedResult = results[0];
      }
      
      if (!selectedResult.success && selectedResult.path === "NO SOLUTION") {
        throw new Error(`No path found between "${start}" and "${end}"`);
      }
      
      setPathData({
        path: selectedResult.path,
        timeTaken: selectedResult.time,
        success: selectedResult.success || true
      });
      
      console.log("✅ Search completed:", selectedResult);
      
    } catch (error) {
      console.error("❌ Search failed:", error);
      
      let errorMessage = "Search failed";
      if (error.code === 'ECONNABORTED') {
        errorMessage = "Search timed out. Try again with different articles.";
      } else if (error.response) {
        errorMessage = error.response.data?.error || `Server error: ${error.response.status}`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      setPathData({
        path: "[]",
        timeTaken: 0,
        success: false
      });
    }
  }, [startTitle, endTitle, algoToggle]);

  // Handle form submission
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    const isRandom = e.nativeEvent.submitter?.value === "random";
    
    // Validation for non-random searches
    if (!isRandom) {
      if (!startTitle.trim() || !endTitle.trim()) {
        setError("Please enter both start and end articles");
        return;
      }
      
      if (startTitle.trim().toLowerCase() === endTitle.trim().toLowerCase()) {
        setError("Start and end articles must be different");
        return;
      }
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await fetchSearchData(isRandom);
      setFirstLoad(false);
    } finally {
      setLoading(false);
    }
  }, [startTitle, endTitle, fetchSearchData]);

  // Handle algorithm toggle
  const handleAlgoToggle = useCallback(() => {
    setAlgoToggle(current => 
      current === "best_first_search" ? "depth_first_search" : "best_first_search"
    );
  }, []);

  // Handle input focus (clear placeholder)
  const handleInputFocus = useCallback((setter) => () => {
    setter("");
  }, []);

  // Handle input validation with visual feedback
  const validateInputs = useCallback(() => {
    const startValid = startTitle.trim().length > 0;
    const endValid = endTitle.trim().length > 0;
    const different = startTitle.trim().toLowerCase() !== endTitle.trim().toLowerCase();
    
    return startValid && endValid && different;
  }, [startTitle, endTitle]);

  // Enhanced success state handling
  const isSuccessState = pathData.success && pathDisplay && !firstLoad && !loading;

  return (
    <div className="homePage">
      <header>
        <h1>Wikipedia Path Finder</h1>
        <p className="subtitle">
          Discover the shortest path between any two Wikipedia articles using advanced AI algorithms
        </p>
      </header>

      <main>
        <div className="centerSection">
          <form id="pathForm" onSubmit={handleSubmit}>
            <div className="input-group">
              <input
                type="text"
                placeholder="Start Article (e.g., Python programming)"
                name="startTitle"
                value={startTitle}
                onFocus={handleInputFocus(setStartTitle)}
                onChange={(e) => setStartTitle(e.target.value)}
                disabled={loading}
                aria-label="Starting Wikipedia article"
                autoComplete="off"
              />
              <span className="connector">→</span>
              <input
                type="text"
                placeholder="End Article (e.g., Machine Learning)"
                name="endTitle"
                value={endTitle}
                onFocus={handleInputFocus(setEndTitle)}
                onChange={(e) => setEndTitle(e.target.value)}
                disabled={loading}
                aria-label="Target Wikipedia article"
                autoComplete="off"
              />
            </div>
            
            <div className="button-group">
              <button 
                className="algoToggleButton" 
                type="button" 
                onClick={handleAlgoToggle}
                disabled={loading}
                title={`Currently using ${algoTitle} algorithm. Click to switch.`}
                aria-label={`Switch from ${algoTitle} to ${algoToggle === "best_first_search" ? "Depth-First" : "Best-First"} algorithm`}
              >
                🔄 {algoTitle} Search
              </button>
              <button 
                className="goButton" 
                type="submit" 
                value="go"
                disabled={loading || !validateInputs()}
                aria-label="Start pathfinding search"
              >
                {loading ? (
                  <>
                    <span className="spinner">⚡</span>
                    Searching...
                  </>
                ) : validateInputs() ? (
                  <>
                    🔍 Find Path
                  </>
                ) : (
                  <>
                    📝 Enter Articles
                  </>
                )}
              </button>
              <button 
                type="submit" 
                value="random"
                disabled={loading}
                title="Find path between two randomly selected Wikipedia articles"
                aria-label="Search between random articles"
              >
                🎲 Random Articles
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message" role="alert">
              <p>⚠️ {error}</p>
            </div>
          )}

          <section className="botInfo" aria-live="polite">
            <div className="infoHeader">
              <div className="infoGroup">
                <p className={loading ? "clicks pizzaSpin" : "clicks"}>
                  {firstLoad ? "•" : clicks}
                </p>
                <span>Steps</span>
              </div>
              <div className="infoGroup">
                <p className={loading ? "timeTaken pizzaSpin" : "timeTaken"}>
                  {firstLoad ? "•" : `${pathData.timeTaken}s`}
                </p>
                <span>Duration</span>
              </div>
            </div>
            
            <div className="pathInfo">
              <div className={!loading ? "path" : "path pathLoader"}>
                {firstLoad && !loading ? (
                  <>
                    Welcome to Wikipedia Path Finder! 🎯
                    <br />
                    Enter two articles above and click <strong>Find Path</strong> to discover how they're connected.
                    <br />
                    Try <strong>Random Articles</strong> for a surprise, or toggle between <strong>{algoTitle} Search</strong> algorithms.
                  </>
                ) : loading ? (
                  <>
                    🧠 AI is analyzing Wikipedia connections
                  </>
                ) : pathData.success && pathDisplay ? (
                  <span className="path-result">
                    🎉 Path found: {pathDisplay}
                  </span>
                ) : (
                  <span className="path-result">
                    😔 No path could be found between these articles
                  </span>
                )}
              </div>
            </div>
          </section>

          {(loading || firstLoad) && (
            <section className="funFact" aria-live="polite">
              <h3>💡 Did You Know?</h3>
              <p>{fact || "Loading fascinating facts about Wikipedia and AI..."}</p>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default Home;
