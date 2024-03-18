import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./styles.scss";

function Home() {
  const [pathData, setPathData] = useState({
    path: "[]",
    timeTaken: 0,
  });
  const [loading, setLoading] = useState(true);
  const [startTitle, setStartTitle] = useState("Minecraft");
  const [endTitle, setEndTitle] = useState("Pizza");
  const [algoToggle, setAlgoToggle] = useState("best_first_search");
  const [fact, setFact] = useState("");
  const [firstLoad, setFirstLoad] = useState(true);
  const [factChangerId, setFactChangerId] = useState(null);

  const clicks = useMemo(() => {
    let pathArr = pathData.path.replaceAll("'", '"');
    pathArr = pathArr.replaceAll('"s', "'s");
    pathArr = JSON.parse(pathArr);
    return pathArr.length - 1;
  }, [pathData]);

  const path = useMemo(() => {
    let pathArr = pathData.path.replaceAll("'", '"');
    pathArr = pathArr.replaceAll('"s', "'s");
    pathArr = JSON.parse(pathArr);
    let text = "";
    let counter = pathArr.length;
    pathArr.forEach((element) => {
      if (counter === 1) text += `${element}`;
      else text += `${element} > `;
      counter--;
    });
    return text;
  }, [pathData]);

  const algoTitle = useMemo(() => {
    switch (algoToggle) {
      case "best_first_search":
        return "Best";
      case "depth_first_search":
        return "Depth";
    }
  }, [algoToggle]);

  const fetchFactData = async () => {
    try {
      const res = await axios.get("https://api.api-ninjas.com/v1/facts?limit=1", {
        headers: {
          "X-Api-Key": "qKYv6ffmUut4HXbt/CswWA==HIDFaMPKP5qaj5De",
        },
      });
      setFact(res.data[0].fact);
    } catch (error) {
      console.log(`Error: ${error.message}`);
      setFact("I couldn't think of a good one");
    }
  };

  useEffect(() => {
    if (firstLoad) {
      fetchFactData();
      setLoading(false);
    }
  }, [firstLoad]);

  useEffect(() => {
    if (loading && !firstLoad) {
      fetchFactData();
      const factChanger = setInterval(() => {
        fetchFactData();
      }, 10000);
      setFactChangerId(factChanger);
    }
    return () => {
      if (factChangerId) {
        clearInterval(factChangerId);
      }
    };
  }, [loading]);

  const fetchSearchData = async (isRandom) => {
    try {
      const res = await axios.post("http://localhost:4000/", {
        isRandom: isRandom,
        startArticle: startTitle,
        endArticle: endTitle,
        algo: algoToggle,
      });
      let results = res.data.results;
      if (results.length === 2) {
        results = results.find((result) => result.algo === "best_first_search");
        setPathData({
          path: results.path,
          timeTaken: results.time,
        });
      } else {
        setPathData({
          path: results[0].path,
          timeTaken: results[0].time,
        });
      }
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await fetchSearchData(e.target.value === "random" ? true : false);
    setFirstLoad(false);
    setLoading(false);
  };

  const handleAlgoToggle = (e) => {
    switch (algoToggle) {
      case "best_first_search":
        setAlgoToggle("depth_first_search");
        break;
      case "depth_first_search":
        setAlgoToggle("best_first_search");
        break;
    }
  };

  return (
    <div className="homePage">
      <h1>The Wiki Bot</h1>
      <main>
        <div></div>
        <div className="centerSection">
          <form id="pathForm" onSubmit={(e) => handleSubmit(e)}>
            <input
              type="text"
              placeholder="Start Title"
              name="startTitle"
              value={startTitle}
              onFocus={() => setStartTitle("")}
              onChange={(e) => setStartTitle(e.target.value)}
            />
            <p>to</p>
            <input
              type="text"
              placeholder="End Title"
              name="endTitle"
              value={endTitle}
              onFocus={() => setEndTitle("")}
              onChange={(e) => setEndTitle(e.target.value)}
            />
            <button className="algoToggleButton" type="button" onClick={handleAlgoToggle}>
              {algoTitle} First Search
            </button>
            <button className="goButton" type="submit" value="go">
              Go
            </button>
            <button type="submit" value="random">
              Random
            </button>
          </form>
          <section className="botInfo">
            <div className="infoHeader">
              <section className="infoGroup">
                <p className={loading ? "clicks pizzaSpin" : "clicks"}>{firstLoad ? "*" : clicks}</p>
                <p>Clicks</p>
              </section>
              <section className="infoGroup test">
                <p className={loading ? "timeTaken pizzaSpin" : "timeTaken"}>{firstLoad ? "*" : pathData.timeTaken}</p>
                <p>Seconds</p>
              </section>
            </div>
            <div className="pathInfo">
              <p className={!loading ? "path" : "path pathLoader"}>
                {firstLoad && !loading ? (
                  <>
                    Click <span>Go</span> or <span>Random</span> to start your search.
                    <br />
                    Click <span>{algoTitle} First Search</span> to toggle search modes.
                  </>
                ) : loading ? (
                  <>Finding Path</>
                ) : (
                  path
                )}
              </p>
            </div>
          </section>
          {loading || firstLoad ? (
            <div className="funFact">
              <p>
                Fun Fact:
                <br />
                {fact ? fact : "Loading..."}
              </p>
            </div>
          ) : (
            <div className="wikiPages">
              <iframe src="" frameborder="0"></iframe>
              <iframe src="" frameborder="0"></iframe>
            </div>
          )}
        </div>
        <div></div>
      </main>
    </div>
  );
}

export default Home;
