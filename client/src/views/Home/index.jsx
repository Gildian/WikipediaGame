import React, { useEffect, useMemo, useState } from "react";
import "./styles.scss";

function Home() {
  const [clicks, setClicks] = useState('3');
  const [timeTaken, setTimeTaken] = useState('Press Go!');
  const [pathData, setPathData] = useState(['Apple TV', 'Papa Johns', 'Pizza']);
  const [loading, setLoading] = useState(false);
  const [startTitle, setStartTitle] = useState('Minecraft');
  const [endTitle, setEndTitle] = useState('Pizza');

  // this changes once data is being loaded/bot running
  const [newPage, setNewPage] = useState(true);

  const path = useMemo((() => {
      let text = '';
      let counter = pathData.length;
      pathData.forEach(element => {
        if (counter === 1) text += `${element}`
        else text += `${element} > `
        counter--;
      });
      return text;
    }), [pathData])

  //const [wiki1, setWiki1] = useState('Fun Fact:')

  useEffect(() => {
    //if (loading) {

    //}
  
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('test submit')
  }

  return (
    <div className="homePage">
      <h1>The Wiki Bot</h1>
      <main>
        <div></div>
        <div className="centerSection">
          <form id="pathForm" onSubmit={(e) => handleSubmit(e)}>
            <input type="text" placeholder="Start Title" name="startTitle" value={startTitle} onFocus={() => setStartTitle('')} onChange={(e) => setStartTitle(e.target.value)}/>
            <p>to</p>
            <input type="text" placeholder="End Title" name="endTitle" value={endTitle} onFocus={() => setEndTitle('')} onChange={(e) => setEndTitle(e.target.value)}/>
            <button>Go</button>
          </form>
          <section className="botInfo">
            <div className="infoHeader">
              <p className="clicks">{clicks} Clicks</p>
              <p className="timeTaken">{timeTaken}</p>
            </div>
            <div className="pathInfo">
              <p className="path">{path}</p>
            </div>
          </section>
          <div className="wikiPages">
            <iframe src="" frameborder="0"></iframe>
            <iframe src="" frameborder="0"></iframe>
          </div>
        </div>
        <div></div>
      </main>
    </div>
  );
}

export default Home;
